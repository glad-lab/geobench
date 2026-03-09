#!/bin/bash
set -euo pipefail  # 严格模式：报错立即退出、未定义变量报错、管道失败报错
shopt -s nullglob  # 如果通配符没有匹配到文件，返回空列表而不是字面量

# ===================== 配置参数 =====================
base_dir="/home/exouser/vscode/geobench"
datasets_clean_20_dir="${base_dir}/Datasets_clean_20"

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
results_base_dir="${base_dir}/Results_new"

mode="self"
user_msg_type="default"
target_llm="llama"
num_iter=1200
test_iter=50
run=1  # 固定为1，每个商品只跑一次
python_path="conda run -n geo python -u"  # 使用 geo conda 环境，-u 参数禁用输出缓冲

# ===================== 显存优化环境变量 =====================
# 降低 max_split_size_mb 以减少内存占用，避免 OOM
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8"
export TRANSFORMERS_CACHE="/tmp"
export CUDA_VISIBLE_DEVICES=0  # 单卡独占，避免多卡调度冲突
export PYTHONUNBUFFERED=1  # 禁用 Python 输出缓冲，实时写入日志

# ===================== 遍历函数 =====================
echo "============================================================"
echo "开始遍历 Datasets_clean_20 数据集"
echo "============================================================"
echo "数据集目录: ${datasets_clean_20_dir}"
echo "结果保存目录: ${results_base_dir}"
echo "每个数据集最多处理 10 个 category"
echo "每个 category 只处理第一个 product"
echo ""

total_tasks=0
skipped_tasks=0
completed_tasks=0

# 自动获取 Datasets_clean_20 下的所有文件夹（排除 README.md）
mapfile -t dataset_folders < <(ls -d "${datasets_clean_20_dir}"/*/ 2>/dev/null | xargs -n1 basename | grep -v "^README.md$" | sort)

if [ ${#dataset_folders[@]} -eq 0 ]; then
    echo "❌ 错误: 在 ${datasets_clean_20_dir} 中未找到任何数据集文件夹"
    exit 1
fi

echo "找到 ${#dataset_folders[@]} 个数据集文件夹: ${dataset_folders[*]}"
echo ""

for algorithm_name in "${dataset_folders[@]}"; do
    algorithm_dir="${datasets_clean_20_dir}/${algorithm_name}"
    
    if [ ! -d "${algorithm_dir}" ]; then
        echo "⚠️  警告: 算法文件夹不存在，跳过: ${algorithm_name}"
        continue
    fi
    
    echo "📦 处理算法: ${algorithm_name}"
    echo "   算法目录: ${algorithm_dir}"
    
    # 遍历该算法下的前 10 个类别文件（按文件名排序，如果少于 10 个则全部处理）
    category_count=0
    mapfile -t category_files < <(ls "${algorithm_dir}"/*.jsonl 2>/dev/null | sort)
    max_categories=10
    total_categories=${#category_files[@]}
    categories_to_process=${total_categories}
    if [ ${total_categories} -gt ${max_categories} ]; then
        categories_to_process=${max_categories}
    fi
    
    echo "   总类别数: ${total_categories}, 将处理: ${categories_to_process}"
    
    for category_file in "${category_files[@]:0:${categories_to_process}}"; do
        if [ ! -f "${category_file}" ]; then
            continue
        fi
        category_count=$((category_count + 1))

        category_name=$(basename "${category_file}" .jsonl)
        echo "  📁 处理类别: ${category_name}"

        # 检查结果目录中该类别是否已经有至少 1 个 target 商品结果（当前只跑第 1 个商品），如果有则整类跳过
        # 改进检测逻辑：不仅要检查 done.txt，还要检查日志中是否有 OOM 错误
        existing_category_dir="${results_base_dir}/${algorithm_name}/${category_name}/${mode}/${target_llm}/${user_msg_type}"
        if [ -d "${existing_category_dir}" ]; then
            existing_target_count=0
            for result_run_dir in "${existing_category_dir}"/product*/run1; do
                # 检查是否有 done.txt 且包含 "done"
                if [ -f "${result_run_dir}/done.txt" ] && grep -q "done" "${result_run_dir}/done.txt" 2>/dev/null; then
                    # 还要检查日志中是否有 OOM 错误，如果有 OOM 则视为未成功运行
                    log_file="${result_run_dir}/rank_opt_background.log"
                    if [ -f "${log_file}" ] && (grep -qi "OutOfMemoryError\|CUDA out of memory" "${log_file}" 2>/dev/null); then
                        # 有 OOM 错误，视为未成功运行，不计数
                        continue
                    else
                        # 没有 OOM 错误且 done.txt 存在，视为成功运行
                        existing_target_count=$((existing_target_count + 1))
                    fi
                fi
            done

            if [ "${existing_target_count}" -ge 1 ]; then
                echo "     ✅ 结果目录中已存在至少 1 个成功运行的 target 商品结果（${existing_target_count} 个），当前策略只跑第 1 个商品，跳过该类别"
                echo ""
                continue
            else
                echo "     ℹ️  结果目录中已有 ${existing_target_count} 个成功运行的 target 商品结果，继续处理当前策略（只跑第 1 个商品）..."
            fi
        fi

        # 统计商品数量（使用 Python，路径通过 argv 传入，避免文件名中的单引号导致语法错误）
        product_count=$(conda run -n geo python3 -c '
import json
import sys
with open(sys.argv[1], "r", encoding="utf-8") as f:
    products = [json.loads(l) for l in f if l.strip()]
print(len(products))
' "${category_file}")
        
        echo "     商品数量: ${product_count}"
        
        # 将文件复制到 data 目录，使用 category_name 作为文件名
        data_dir="${base_dir}/data"
        mkdir -p "${data_dir}"
        data_catalog_path="${data_dir}/${category_name}.jsonl"
        cp -f "${category_file}" "${data_catalog_path}"
        
        # 只遍历第 1 个商品作为 target product，减小迭代数量
        max_target_products=1
        last_product_idx=${product_count}
        if [ "${product_count}" -gt "${max_target_products}" ]; then
            last_product_idx=${max_target_products}
        fi

        for product_idx in $(seq 1 ${last_product_idx}); do
            # 构建结果目录
            # 格式: results_datasets_5/{algorithm}/{category}/self/{target_llm}/{user_msg_type}/product{product_idx}/run{run}
            results_dir="${results_base_dir}/${algorithm_name}/${category_name}/${mode}/${target_llm}/${user_msg_type}/product${product_idx}/run${run}"
            log_file="${results_dir}/rank_opt_background.log"
            
            # 检查是否已完成（改进：不仅要检查 done.txt，还要检查日志中是否有 OOM 错误）
            if [ -f "${results_dir}/done.txt" ] && grep -q "done" "${results_dir}/done.txt" 2>/dev/null; then
                # 检查日志中是否有 OOM 错误，如果有 OOM 则视为未成功运行，需要重新运行
                if [ -f "${log_file}" ] && (grep -qi "OutOfMemoryError\|CUDA out of memory" "${log_file}" 2>/dev/null); then
                    echo "      ⚠️  product${product_idx}: 检测到 OOM 错误，将重新运行（减少商品数量）"
                    # 删除 done.txt，以便重新运行
                    rm -f "${results_dir}/done.txt"
                else
                    skipped_tasks=$((skipped_tasks + 1))
                    echo "      ⏭️  product${product_idx}: 已完成，跳过"
                    continue
                fi
            fi
            
            # 创建结果目录
            mkdir -p "${results_dir}"
            
            total_tasks=$((total_tasks + 1))
            echo "      ▶️  product${product_idx}: 开始运行..."
            
            # 确保前一个 rank_opt.py 进程完全结束（防止并行执行）
            # 添加超时机制，避免无限等待（最多等待 60 秒）
            wait_timeout=60
            wait_count=0
            while pgrep -f "rank_opt.py.*${category_name}.*product${product_idx}" > /dev/null 2>&1; do
                if [ ${wait_count} -ge ${wait_timeout} ]; then
                    echo "      ⚠️  等待超时（${wait_timeout}秒），强制停止残留进程..."
                    pkill -f "rank_opt.py.*${category_name}.*product${product_idx}" 2>/dev/null
                    sleep 2
                    break
                fi
                echo "      ⏳ 等待前一个进程结束... (${wait_count}/${wait_timeout}秒)"
                sleep 2
                wait_count=$((wait_count + 2))
            done
            
            # 运行 rank_opt.py（前台运行，等待完成后再执行下一个任务）
            # 使用 category_name 作为 catalog 参数（文件已在 data/ 目录下）
            # 添加 OOM 自动重试逻辑：如果 OOM，则逐个减少商品数量并重新运行（最少到 3 个）
            cd "${base_dir}"
            
            # 动态生成商品数量列表：从 product_count-1 开始，逐个减少到 3
            # 例如：如果 product_count=6，则列表为 (5 4 3)
            min_products=3
            default_max_products=10  # 默认最大商品数，避免 OOM
            max_products_in_prompt_list=()
            
            # 如果商品数量 >= 10，先尝试使用 8 个商品，避免 OOM
            initial_max_products=""
            if [ "${product_count}" -ge 10 ]; then
                initial_max_products=${default_max_products}
            fi
            
            if [ "${product_count}" -gt "${min_products}" ]; then
                # 生成从 product_count-1 到 min_products 的列表
                for ((i=$((product_count - 1)); i >= min_products; i--)); do
                    # 如果 initial_max_products 已设置，跳过它（避免重复）
                    if [ -z "${initial_max_products}" ] || [ "${i}" -ne "${initial_max_products}" ]; then
                        max_products_in_prompt_list+=(${i})
                    fi
                done
            fi
            
            run_success=false
            # 如果设置了 initial_max_products，先尝试它；否则尝试全部商品
            # 如果 OOM 则逐个减少商品数量
            if [ -n "${initial_max_products}" ]; then
                # 先尝试 initial_max_products（避免 OOM），如果失败再尝试其他数量
                # 注意：如果 initial_max_products 等于 product_count，就不需要再尝试 ""（全部商品）
                if [ "${initial_max_products}" -eq "${product_count}" ]; then
                    max_products_sequence=("${initial_max_products}" "${max_products_in_prompt_list[@]}")
                else
                    max_products_sequence=("${initial_max_products}" "" "${max_products_in_prompt_list[@]}")
                fi
            else
                # 先尝试全部商品，然后尝试减少的数量
                max_products_sequence=("" "${max_products_in_prompt_list[@]}")
            fi
            
            attempt_count=0
            for max_products in "${max_products_sequence[@]}"; do
                attempt_count=$((attempt_count + 1))
                if [ ${attempt_count} -gt 1 ]; then
                    if [ -n "${max_products}" ]; then
                        echo "      🔄 product${product_idx}: 检测到 OOM，使用 ${max_products} 个商品重新运行..."
                    else
                        echo "      🔄 product${product_idx}: 检测到 OOM，尝试使用全部商品重新运行..."
                    fi
                fi
                
                # 构建命令参数
                cmd_args=(
                    --results_dir "${results_dir}"
                    --catalog "${category_name}"
                    --user_msg_type "${user_msg_type}"
                    --target_product_idx "${product_idx}"
                    --num_iter "${num_iter}"
                    --test_iter "${test_iter}"
                    --random_order
                    --save_state
                    --mode "${mode}"
                    --target_llm "${target_llm}"
                )
                # 如果设置了 max_products，添加该参数
                if [ -n "${max_products}" ]; then
                    cmd_args+=(--max_products_in_prompt "${max_products}")
                fi
                
                # 使用 stdbuf 禁用缓冲，确保实时输出到日志文件
                # 已设置 PYTHONUNBUFFERED=1 和 python -u，但 conda run 可能仍有缓冲，使用 stdbuf 强制实时输出
                # 同时使用 tee 来同时输出到日志和控制台（用于调试）
                # 修改：使用 append 模式（>>）确保 OOM 错误也能被记录
                if stdbuf -oL -eL ${python_path} rank_opt.py "${cmd_args[@]}" 2>&1 | stdbuf -oL -eL tee -a "${log_file}" > /dev/null; then
                    # 检查日志中是否有 OOM 错误
                    if [ -f "${log_file}" ] && (grep -qi "OutOfMemoryError\|CUDA out of memory" "${log_file}" 2>/dev/null); then
                        echo "      ⚠️  product${product_idx}: 检测到 OOM 错误"
                        if [ -n "${max_products}" ] && [ "${max_products}" = "${min_products}" ]; then
                            # 已经尝试了最少商品数量（3个），仍然 OOM
                            echo "      ❌ product${product_idx}: 即使使用 ${min_products} 个商品仍然 OOM，跳过"
                            run_success=false
                            break
                        else
                            # 继续尝试更少的商品数量
                            continue
                        fi
                    else
                        # 没有 OOM 错误，运行成功
                        echo "done" > "${results_dir}/done.txt"
                        completed_tasks=$((completed_tasks + 1))
                        if [ -n "${max_products}" ]; then
                            echo "      ✅ product${product_idx}: 完成（使用了 ${max_products} 个商品）"
                        else
                            echo "      ✅ product${product_idx}: 完成"
                        fi
                        run_success=true
                        break
                    fi
                else
                    # 检查是否是 OOM 错误
                    if [ -f "${log_file}" ] && (grep -qi "OutOfMemoryError\|CUDA out of memory" "${log_file}" 2>/dev/null); then
                        echo "      ⚠️  product${product_idx}: 检测到 OOM 错误"
                        if [ -n "${max_products}" ] && [ "${max_products}" = "${min_products}" ]; then
                            # 已经尝试了最少商品数量（3个），仍然 OOM
                            echo "      ❌ product${product_idx}: 即使使用 ${min_products} 个商品仍然 OOM，跳过"
                            run_success=false
                            break
                        else
                            # 继续尝试更少的商品数量
                            continue
                        fi
                    else
                        # 其他错误（非 OOM）
                        echo "      ❌ product${product_idx}: 失败，请查看日志: ${log_file}"
                        run_success=false
                        break
                    fi
                fi
            done
            
            if [ "${run_success}" = "false" ]; then
                echo "      ❌ product${product_idx}: 最终失败，请查看日志: ${log_file}"
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
