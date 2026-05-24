#!/bin/bash

# 自动遍历 Results_new 中所有包含 sts.txt 的目录，
# 调用 evaluate.py 计算 eval.json，并用 plot/plot_dist.py 画图。
# 参考：bashscripts/eval_self.sh

set -euo pipefail

# 计算工程根目录和结果根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ROOT_DIR="${PROJECT_ROOT}/Results_new"
NUM_ITER=200          # 每个 sts 评价多少次，可按需调整
PROD_ORD="random"

echo "=========================================="
echo "自动评估 Results_new 中的所有 sts.txt"
echo "根目录: ${ROOT_DIR}"
echo "每个 STS 评估迭代次数: ${NUM_ITER}"
echo "=========================================="
echo ""

if [ ! -d "${ROOT_DIR}" ]; then
    echo "❌ 根目录不存在: ${ROOT_DIR}"
    exit 1
fi

# 遍历所有包含 sts.txt 的 run 目录
while IFS= read -r sts_path; do
    run_dir="$(dirname "${sts_path}")"

    # 检查是否已经成功评估过（类似 iterate_datasets_5.sh 的检查逻辑）
    eval_json="${run_dir}/eval.json"
    eval_log="${run_dir}/eval.log"
    skip_eval=false
    need_plot=false
    plot_files=(
        "${run_dir}/ranks.png"
        "${run_dir}/ranks_cleaned.png"
        "${run_dir}/rank_barplot.png"
        "${run_dir}/rank_barplot_cleaned.png"
        "${run_dir}/advantage.png"
        "${run_dir}/advantage_cleaned.png"
    )
    
    # 如果 eval.json 存在，检查是否有效（文件大小 > 0，且包含有效 JSON）
    if [ -f "${eval_json}" ]; then
        # 检查文件大小（空文件或损坏的文件应该重新评估）
        if [ ! -s "${eval_json}" ]; then
            echo "⚠️ eval.json 存在但为空，将重新评估: ${run_dir}"
            rm -f "${eval_json}"
        else
            # 检查是否是有效的 JSON（至少包含 "rank_list" 字段）
            if command -v jq >/dev/null 2>&1; then
                if jq -e '.rank_list' "${eval_json}" >/dev/null 2>&1; then
                    # 检查是否有错误日志（类似 iterate 脚本检查 OOM）
                    if [ -f "${eval_log}" ] && (grep -qi "Traceback\|Error\|Exception\|KeyError\|FileNotFoundError" "${eval_log}" 2>/dev/null); then
                        echo "⚠️ 检测到 eval 错误日志，将重新评估: ${run_dir}"
                        rm -f "${eval_json}" "${eval_log}"
                    else
                        echo "✅ 已存在有效的 eval.json：将跳过评估并检查是否需要补画图: ${run_dir}"
                        skip_eval=true
                    fi
                else
                    echo "⚠️ eval.json 格式无效，将重新评估: ${run_dir}"
                    rm -f "${eval_json}"
                fi
            else
                # 如果没有 jq，简单检查文件大小和基本内容
                if grep -q "rank_list" "${eval_json}" 2>/dev/null; then
                    echo "✅ 已存在 eval.json（未验证格式）：将跳过评估并检查是否需要补画图: ${run_dir}"
                    skip_eval=true
                else
                    echo "⚠️ eval.json 可能无效，将重新评估: ${run_dir}"
                    rm -f "${eval_json}"
                fi
            fi
        fi
    fi

    # 如果已经有 eval.json，检查图是否齐全；缺失则补画图
    if [ -f "${eval_json}" ] && [ "${skip_eval}" = "true" ]; then
        for pf in "${plot_files[@]}"; do
            if [ ! -f "${pf}" ]; then
                need_plot=true
                break
            fi
        done
        # 如果之前日志里明确出现 plot_dist 失败，也强制补画
        if [ -f "${eval_log}" ] && grep -qi "plot_dist" "${eval_log}" 2>/dev/null; then
            need_plot=true
        fi
    fi

    # 需要有 exp_config.json 才能自动读取配置
    exp_config="${run_dir}/exp_config.json"
    if [ ! -f "${exp_config}" ]; then
        echo "⚠️ 未找到 exp_config.json，跳过: ${run_dir}"
        continue
    fi

    echo "------------------------------------------"
    echo "▶ 评估目录: ${run_dir}"

    # 解析 product 索引（product1/run1 -> 1）
    prod_idx="$(echo "${run_dir}" | sed -n 's@.*product\([0-9]\+\)/run[0-9]\+.*@\1@p')"
    if [ -z "${prod_idx}" ]; then
        echo "⚠️ 无法从路径解析 product index，跳过: ${run_dir}"
        continue
    fi

    # 从 exp_config.json 中读取模型路径、catalog 路径、user_msg_type
    if ! command -v jq >/dev/null 2>&1; then
        echo "❌ 需要安装 jq 才能解析 exp_config.json，请先安装 jq"
        exit 1
    fi

    model_path="$(jq -r '."Model path(s)"' "${exp_config}")"
    catalog_path_raw="$(jq -r '."Product catalog"' "${exp_config}")"
    user_msg_type="$(jq -r '."User message type"' "${exp_config}")"

    if [ -z "${model_path}" ] || [ "${model_path}" = "null" ]; then
        echo "⚠️ exp_config.json 中缺少 \"Model path(s)\"，跳过: ${run_dir}"
        continue
    fi
    if [ -z "${catalog_path_raw}" ] || [ "${catalog_path_raw}" = "null" ]; then
        echo "⚠️ exp_config.json 中缺少 \"Product catalog\"，跳过: ${run_dir}"
        continue
    fi

    # 解析 catalog 文件路径（eval 时可以直接用原始路径，不需要复制到 data/）
    catalog_path="${catalog_path_raw}"
    catalog_base="$(basename "${catalog_path_raw}" .jsonl)"
    
    # 如果 exp_config.json 里记录的是 data/ 路径但文件不存在，尝试从原始位置找
    if [ ! -f "${PROJECT_ROOT}/${catalog_path}" ]; then
        # 从 run_dir 解析算法名称：Results_new/<algorithm_name>/...
        # 这样可以覆盖 Ragroll/Ragdoll/RewriteToRank_Subsampled/LLMRank/STSData/C-SEO 等
        algorithm_name=""
        if echo "${run_dir}" | grep -q "/Results_new/"; then
            rel="${run_dir#${PROJECT_ROOT}/Results_new/}"
            algorithm_name="${rel%%/*}"
        fi
        
        if [ -z "${algorithm_name}" ]; then
            echo "❌ 无法从路径解析算法名称，无法定位 catalog 文件"
            echo "   跳过: ${run_dir}"
            continue
        fi

        # 依次尝试多个可能位置（以便兼容不同生成方式）
        candidate_paths=(
            "${PROJECT_ROOT}/${catalog_path_raw}"
            "${PROJECT_ROOT}/data/${catalog_base}.jsonl"
            "${PROJECT_ROOT}/datasets_5/${algorithm_name}/${catalog_base}.jsonl"
            "${PROJECT_ROOT}/Datasets_clean_20/${algorithm_name}/${catalog_base}.jsonl"
        )

        found=""
        for p in "${candidate_paths[@]}"; do
            if [ -f "${p}" ]; then
                found="${p}"
                break
            fi
        done

        if [ -n "${found}" ]; then
            catalog_path="${found#${PROJECT_ROOT}/}"
            echo "  ℹ️ 使用定位到的 catalog 文件: ${catalog_path}"
        else
            echo "❌ 无法找到 catalog 文件。尝试过："
            for p in "${candidate_paths[@]}"; do
                echo "   - ${p}"
            done
            echo "   跳过: ${run_dir}"
            continue
        fi
    fi

    # 由 catalog 文件名粗略推一个 evaluate.py 需要的 --catalog（只影响 user_msg 模板）
    # catalog_base 已在上面定义
    catalog_arg="coffee_machines"
    case "${catalog_base}" in
        books|books_media|action|adventure|animation|childrens|comedy)
            catalog_arg="books"
            ;;
        cameras)
            catalog_arg="cameras"
            ;;
        election_articles)
            catalog_arg="election_articles"
            ;;
        *)
            catalog_arg="coffee_machines"
            ;;
    esac

    echo "  模型: ${model_path}"
    echo "  catalog 文件: ${catalog_path}"
    echo "  evaluate.py --catalog: ${catalog_arg}"
    echo "  product index: ${prod_idx}"
    echo "  user_msg_type: ${user_msg_type}"

    # 进入项目根目录再调用 python（假定当前脚本在 geobench/bashscripts 下）
    cd "${PROJECT_ROOT}"

    # 调用 evaluate.py，将输出保存到日志文件（用于错误检测）
    eval_log="${run_dir}/eval.log"
    if [ "${skip_eval}" = "true" ]; then
        echo "  ⏭️  跳过评估（已存在有效 eval.json）"
    else
        echo "  开始评估，日志保存至: ${eval_log}"
        if python evaluate.py \
            --model_path "${model_path}" \
            --prod_idx "${prod_idx}" \
            --sts_dir "${run_dir}" \
            --catalog "${catalog_arg}" \
            --catalog_path "${catalog_path}" \
            --num_iter "${NUM_ITER}" \
            --prod_ord "${PROD_ORD}" \
            --user_msg_type "${user_msg_type}" \
            > "${eval_log}" 2>&1; then
            echo "  ✅ 评估完成"
        else
            echo "  ❌ 评估失败，查看日志: ${eval_log}"
            # 如果失败，删除可能不完整的 eval.json
            rm -f "${run_dir}/eval.json"
            continue
        fi
        need_plot=true
    fi

    # 画 rank 分布图（如果生成了 eval.json；或已存在 eval.json 但缺图则补画）
    if [ -f "${run_dir}/eval.json" ]; then
        if [ "${need_plot}" = "true" ]; then
            if python plot/plot_dist.py "${run_dir}/eval.json" >> "${eval_log}" 2>&1; then
                echo "  ✅ 绘图完成"
            else
                echo "  ⚠️ plot_dist 绘图失败: ${run_dir}"
            fi
        else
            echo "  ✅ 绘图文件已齐全，跳过绘图"
        fi
    else
        echo "  ⚠️ 未找到 eval.json，跳过绘图: ${run_dir}"
    fi

done < <(find "${ROOT_DIR}" -type f -name "sts.txt" | sort)

echo ""
echo "=========================================="
echo "✅ 所有 sts.txt 的自动评估流程已完成（仅对存在 exp_config.json 的目录执行）"
echo "=========================================="


