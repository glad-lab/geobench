#!/bin/bash
set -euo pipefail

# ===================== 配置参数 =====================
# Override via env var: e.g. LLAMA2_PATH=/path/to/Llama-2-7b-chat-hf bash bash_test/eval_self_single.sh
LLAMA2_PATH="${LLAMA2_PATH:-/media/volume/v4/Llama-2-7b-chat-hf}"

catalog="cameras"
num_iter=200
user_msg_type="default"
python_path="python"  # conda环境需替换为绝对路径

# 日志路径（按时间命名，避免覆盖）
log_dir="eval_logs"
mkdir -p "${log_dir}"
log_file="${log_dir}/eval_background_$(date +%Y%m%d_%H%M%S).log"

# ===================== 后台运行核心逻辑 =====================
nohup bash -c '
    catalog="books"
    num_iter=100
    user_msg_type="default"
    python_path="'"${python_path}"'"
    llama2_path="'"${LLAMA2_PATH}"'"

    for run in 1
    do
        for product in 4
        do
            eval_dir="results4/books/self/llama/default/product4/run1"

            # 检查是否已完成
            if [ -f "${eval_dir}/done.txt" ] && grep -q "done" "${eval_dir}/done.txt"; then
                echo "[$(date +\%Y-\%m-\%d \%H:\%M:\%S)] Evaluation for product $product already done" >> "'"${log_file}"'"
                continue
            fi

            # 输出任务开始信息
            echo "[$(date +\%Y-\%m-\%d \%H:\%M:\%S)] Starting evaluation: product=$product, run=$run" >> "'"${log_file}"'"

            # 执行评估
            "${python_path}" evaluate.py \
                --model_path "${llama2_path}" \
                --prod_idx "${product}" \
                --sts_dir "${eval_dir}" \
                --catalog "${catalog}" \
                --num_iter "${num_iter}" \
                --prod_ord random \
                --user_msg_type "${user_msg_type}" >> "'"${log_file}"'" 2>&1

            # 绘图
            echo "[$(date +\%Y-\%m-\%d \%H:\%M:\%S)] Starting plot for product $product" >> "'"${log_file}"'"
            "${python_path}" plot/plot_dist.py "${eval_dir}/eval.json" >> "'"${log_file}"'" 2>&1

            # 标记完成
            touch "${eval_dir}/done.txt"
            echo "done" > "${eval_dir}/done.txt"

            # 输出任务完成信息
            echo "[$(date +\%Y-\%m-\%d \%H:\%M:\%S)] Evaluation for product $product finished" >> "'"${log_file}"'"
            echo "--------------------------------------------------" >> "'"${log_file}"'"
        done
    done

    echo "[$(date +\%Y-\%m-\%d \%H:\%M:\%S)] All evaluations completed!" >> "'"${log_file}"'"
    echo "SLURM_NODELIST: ${SLURM_NODELIST:-"未使用SLURM"}" >> "'"${log_file}"'"
' > "${log_file}" 2>&1 &

# 运行状态提示
pid=$!
echo "🚀 评估脚本已在后台启动！"
echo "进程ID（PID）：${pid}"
echo "日志文件：${log_file}"
echo "查看实时日志：tail -f ${log_file}"
echo "停止脚本：kill -9 ${pid}"