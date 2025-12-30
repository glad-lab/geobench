#!/bin/bash
set -euo pipefail  # 严格模式：报错立即退出、未定义变量报错、管道失败报错
shopt -s nullglob  # 如果通配符没有匹配到文件，返回空列表而不是字面量

# ===================== 配置参数 =====================
base_dir="/home/exouser/Desktop/vscode/geobench"
datasets_5_dir="${base_dir}/datasets_5"

# ===================== 防止并行执行锁机制 =====================
lock_file="${base_dir}/.iterate_datasets_5.lock"
if [ -f "${lock_file}" ]; then
    old_pid=$(cat "${lock_file}" 2>/dev/null || echo "")
    if [ -n "${old_pid}" ] && ps -p "${old_pid}" > /dev/null 2>&1; then
        echo "❌ 错误: 脚本已在运行中 (PID: ${old_pid})"
        echo "   如果确定没有运行，请删除锁文件: rm ${lock_file}"
        exit 1
    else
        # 锁文件存在但进程不存在，删除旧的锁文件
        rm -f "${lock_file}"
    fi
fi

# 创建锁文件
echo $$ > "${lock_file}"

# 脚本退出时清理锁文件
trap "rm -f ${lock_file}" EXIT INT TERM

# 使用固定的结果目录（统一所有结果）
results_base_dir="${base_dir}/results_datasets_5"

mode="self"
user_msg_type="default"
target_llm="llama"
num_iter=1600
test_iter=50
run=1  # 固定为1，每个商品只跑一次
python_path="python"

# ===================== 显存优化环境变量 =====================
# 增加max_split_size_mb从64到256，减少内存分配/释放频率，提升速度
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True,max_split_size_mb:256,garbage_collection_threshold:0.6"
export TRANSFORMERS_CACHE="/tmp"
export CUDA_VISIBLE_DEVICES=0  # 单卡独占，避免多卡调度冲突

# ===================== 遍历函数 =====================
echo "============================================================"
echo "开始遍历 datasets_5 数据集"
echo "============================================================"
echo "数据集目录: ${datasets_5_dir}"
echo "结果保存目录: ${results_base_dir}"
echo ""

total_tasks=0
skipped_tasks=0
completed_tasks=0

# 按照指定顺序遍历算法文件夹
algorithm_order=("StealthRank" "llm-rank-optimizer" "AdversarialSEO" "GEO")
# RewriteToRank 跳过，不处理

for algorithm_name in "${algorithm_order[@]}"; do
    algorithm_dir="${datasets_5_dir}/${algorithm_name}"
    
    if [ ! -d "${algorithm_dir}" ]; then
        echo "⚠️  警告: 算法文件夹不存在，跳过: ${algorithm_name}"
        continue
    fi
    
    echo "📦 处理算法: ${algorithm_name}"
    echo "   算法目录: ${algorithm_dir}"
    
    # 遍历该算法下的每个类别文件
    category_count=0
    for category_file in "${algorithm_dir}"/*.jsonl; do
        if [ ! -f "${category_file}" ]; then
            continue
        fi
        category_count=$((category_count + 1))
        
        category_name=$(basename "${category_file}" .jsonl)
        echo "  📁 处理类别: ${category_name}"

        # 检查结果目录中该类别是否已经有至少 3 个不同的 target 商品结果，如果有则整类跳过
        existing_category_dir="${results_base_dir}/${algorithm_name}/${category_name}/${mode}/${target_llm}/${user_msg_type}"
        if [ -d "${existing_category_dir}" ]; then
            existing_target_count=0
            for result_run_dir in "${existing_category_dir}"/product*/run1; do
                if [ -f "${result_run_dir}/done.txt" ] && grep -q "done" "${result_run_dir}/done.txt" 2>/dev/null; then
                    existing_target_count=$((existing_target_count + 1))
                fi
            done

            if [ "${existing_target_count}" -ge 3 ]; then
                echo "     ✅ 结果目录中已存在至少 3 个不同的 target 商品（${existing_target_count} 个），跳过该类别"
                echo ""
                continue
            else
                echo "     ℹ️  结果目录中已有 ${existing_target_count} 个 target 商品结果，继续处理..."
            fi
        fi

        # 统计商品数量（使用 Python）
        product_count=$(python3 -c "
import json
with open('${category_file}', 'r', encoding='utf-8') as f:
    products = [json.loads(l) for l in f if l.strip()]
print(len(products))
")
        
        echo "     商品数量: ${product_count}"
        
        # 将文件复制到 data 目录，使用 category_name 作为文件名
        data_dir="${base_dir}/data"
        mkdir -p "${data_dir}"
        data_catalog_path="${data_dir}/${category_name}.jsonl"
        cp -f "${category_file}" "${data_catalog_path}"
        
        # 只遍历前 3 个商品作为 target product（如果商品少于 3 个，则全量遍历）
        max_target_products=3
        last_product_idx=${product_count}
        if [ "${product_count}" -gt "${max_target_products}" ]; then
            last_product_idx=${max_target_products}
        fi

        for product_idx in $(seq 1 ${last_product_idx}); do
            # 构建结果目录
            # 格式: results_datasets_5/{algorithm}/{category}/self/{target_llm}/{user_msg_type}/product{product_idx}/run{run}
            results_dir="${results_base_dir}/${algorithm_name}/${category_name}/${mode}/${target_llm}/${user_msg_type}/product${product_idx}/run${run}"
            log_file="${results_dir}/rank_opt_background.log"
            
            # 检查是否已完成
            if [ -f "${results_dir}/done.txt" ] && grep -q "done" "${results_dir}/done.txt" 2>/dev/null; then
                skipped_tasks=$((skipped_tasks + 1))
                echo "      ⏭️  product${product_idx}: 已完成，跳过"
                continue
            fi
            
            # 创建结果目录
            mkdir -p "${results_dir}"
            
            total_tasks=$((total_tasks + 1))
            echo "      ▶️  product${product_idx}: 开始运行..."
            
            # 确保前一个 rank_opt.py 进程完全结束（防止并行执行）
            while pgrep -f "rank_opt.py.*${category_name}.*product${product_idx}" > /dev/null 2>&1; do
                echo "      ⏳ 等待前一个进程结束..."
                sleep 2
            done
            
            # 运行 rank_opt.py（前台运行，等待完成后再执行下一个任务）
            # 使用 category_name 作为 catalog 参数（文件已在 data/ 目录下）
            cd "${base_dir}"
            if ${python_path} rank_opt.py \
                --results_dir "${results_dir}" \
                --catalog "${category_name}" \
                --user_msg_type "${user_msg_type}" \
                --target_product_idx "${product_idx}" \
                --num_iter "${num_iter}" \
                --test_iter "${test_iter}" \
                --random_order \
                --save_state \
                --mode "${mode}" \
                --target_llm "${target_llm}" > "${log_file}" 2>&1; then
                echo "done" > "${results_dir}/done.txt"
                completed_tasks=$((completed_tasks + 1))
                echo "      ✅ product${product_idx}: 完成"
            else
                echo "      ❌ product${product_idx}: 失败，请查看日志: ${log_file}"
            fi
            
            # 显式等待进程完全结束（确保不会并行执行）
            sleep 1
            while pgrep -f "rank_opt.py.*${category_name}.*product${product_idx}" > /dev/null 2>&1; do
                echo "      ⏳ 等待进程完全结束..."
                sleep 1
            done
        done
        
        echo ""
    done
    
    if [ ${category_count} -eq 0 ]; then
        echo "   ⚠️  警告: 未找到任何 .jsonl 文件"
    else
        echo "   ✅ 找到 ${category_count} 个类别文件"
    fi
    
    echo ""
done

echo "============================================================"
echo "遍历完成！"
echo "总任务数: ${total_tasks}"
echo "完成任务数: ${completed_tasks}"
echo "跳过任务数: ${skipped_tasks}"
echo "结果目录: ${results_base_dir}"
echo ""
echo "📝 查看日志："
echo "   tail -f ${results_base_dir}/*/*/self/${target_llm}/${user_msg_type}/product*/run${run}/rank_opt_background.log"
echo ""
echo "💡 提示:"
echo "   - 任务完成后会自动创建 done.txt 文件"
echo "   - 可以使用 screen 或 tmux 在后台运行此脚本"
echo "============================================================"
