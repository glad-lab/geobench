#!/bin/bash
set -euo pipefail  # 严格模式：报错立即退出、未定义变量报错、管道失败报错

# ===================== 配置参数（恢复原始状态，无batch_size配置）=====================
product=4
run=1
catalog="kitchen_appliances"
mode="self"
user_msg_type="default"
target_llm="llama"
num_iter=2000
test_iter=50
python_path="python"  # 若用conda环境，替换为实际路径

# 结果目录和日志文件路径
results_dir="results4/${catalog}/${mode}/${target_llm}/${user_msg_type}/product${product}/run${run}"
log_file="${results_dir}/rank_opt_background.log"  # 后台运行日志（保存所有输出和报错）

# ===================== 显存优化环境变量（保留，解决OOM关键）=====================
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True,max_split_size_mb:64,garbage_collection_threshold:0.6"
export TRANSFORMERS_CACHE="/tmp"
export CUDA_VISIBLE_DEVICES=0  # 单卡独占，避免多卡调度冲突

# ===================== 预处理（确保目录存在）=====================
# 自动创建结果目录（含上级目录）
mkdir -p "${results_dir}"
echo "✅ 结果目录已创建/存在：${results_dir}"
echo "📝 运行日志将保存到：${log_file}"
echo "⚙️  配置参数：使用程序默认配置" >> "${log_file}"

# ===================== 后台运行核心命令（恢复原始，无--batch_size参数）=====================
nohup ${python_path} rank_opt.py \
    --results_dir "${results_dir}" \
    --catalog "${catalog}" \
    --user_msg_type "${user_msg_type}" \
    --target_product_idx "${product}" \
    --num_iter "${num_iter}" \
    --test_iter "${test_iter}" \
    --random_order \
    --save_state \
    --mode "${mode}" \
    --target_llm "${target_llm}" > "${log_file}" 2>&1 &

# 保存进程ID（PID）到文件，方便后续管理
pid=$!
echo "${pid}" > "${results_dir}/rank_opt_pid.txt"

# ===================== 运行状态提示（保持你原来的写法）=====================
echo "🚀 程序已在后台启动！"
echo "进程ID（PID）：${pid}"
echo "查看实时日志：tail -f ${log_file}"
echo "停止程序：kill -9 ${pid}（或 kill -9 \`cat ${results_dir}/rank_opt_pid.txt\`）"
echo "SLURM节点信息：${SLURM_NODELIST:-"未使用SLURM"}" >> "${log_file}"