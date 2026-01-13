#!/bin/bash

# 自动遍历 results_datasets_5 中所有包含 sts.txt 的目录，
# 调用 evaluate.py 计算 eval.json，并用 plot/plot_dist.py 画图。
# 参考：bashscripts/eval_self.sh

set -euo pipefail

# 计算工程根目录和结果根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ROOT_DIR="${PROJECT_ROOT}/results_datasets_5"
NUM_ITER=200          # 每个 sts 评价多少次，可按需调整
PROD_ORD="random"

echo "=========================================="
echo "自动评估 results_datasets_5 中的所有 sts.txt"
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

    # 如果已经有 eval.json，就跳过（避免重复评估）
    if [ -f "${run_dir}/eval.json" ]; then
        echo "✅ 已存在 eval.json，跳过: ${run_dir}"
        continue
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
    catalog_path="$(jq -r '."Product catalog"' "${exp_config}")"
    user_msg_type="$(jq -r '."User message type"' "${exp_config}")"

    if [ -z "${model_path}" ] || [ "${model_path}" = "null" ]; then
        echo "⚠️ exp_config.json 中缺少 \"Model path(s)\"，跳过: ${run_dir}"
        continue
    fi
    if [ -z "${catalog_path}" ] || [ "${catalog_path}" = "null" ]; then
        echo "⚠️ exp_config.json 中缺少 \"Product catalog\"，跳过: ${run_dir}"
        continue
    fi

    # 由 catalog 文件名粗略推一个 evaluate.py 需要的 --catalog（只影响 user_msg 模板）
    catalog_base="$(basename "${catalog_path}" .jsonl)"
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

    # 调用 evaluate.py
    python evaluate.py \
        --model_path "${model_path}" \
        --prod_idx "${prod_idx}" \
        --sts_dir "${run_dir}" \
        --catalog "${catalog_arg}" \
        --catalog_path "${catalog_path}" \
        --num_iter "${NUM_ITER}" \
        --prod_ord "${PROD_ORD}" \
        --user_msg_type "${user_msg_type}"

    # 画 rank 分布图（如果生成了 eval.json）
    if [ -f "${run_dir}/eval.json" ]; then
        python plot/plot_dist.py "${run_dir}/eval.json" || echo "⚠️ plot_dist 绘图失败: ${run_dir}"
    else
        echo "⚠️ 未找到 eval.json，跳过绘图: ${run_dir}"
    fi

done < <(find "${ROOT_DIR}" -type f -name "sts.txt" | sort)

echo ""
echo "=========================================="
echo "✅ 所有 sts.txt 的自动评估流程已完成（仅对存在 exp_config.json 的目录执行）"
echo "=========================================="


