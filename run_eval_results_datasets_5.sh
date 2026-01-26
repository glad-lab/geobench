#!/bin/bash
# 使用 nohup 后台启动 eval_results_datasets_5.sh 脚本
#
# 功能：
# - 在后台运行 bashscripts/eval_results_datasets_5.sh
# - 将所有输出重定向到 geobench 根目录下的日志文件
# - 记录 PID，方便后续查看与停止

set -euo pipefail

# ===================== 配置参数 =====================
base_dir="/home/exouser/Desktop/vscode/geobench"
script_name="bashscripts/eval_results_datasets_5.sh"
script_path="${base_dir}/${script_name}"

# 日志 & PID 文件（脚本整体运行日志）
log_file="${base_dir}/run_eval_results_datasets_5.log"
pid_file="${base_dir}/run_eval_results_datasets_5.pid"

# ===================== 检查脚本是否存在 =====================
if [ ! -f "${script_path}" ]; then
    echo "❌ 错误: 脚本文件不存在: ${script_path}"
    exit 1
fi

# ===================== 检查是否已经在运行 =====================
if [ -f "${pid_file}" ]; then
    old_pid=$(cat "${pid_file}")
    if ps -p "${old_pid}" > /dev/null 2>&1; then
        echo "⚠️  警告: eval 任务可能已经在运行中 (PID: ${old_pid})"
        echo "   如果确定没有运行，请删除 PID 文件: rm ${pid_file}"
        exit 1
    else
        # PID 文件存在但进程不存在，删除旧的 PID 文件
        rm -f "${pid_file}"
    fi
fi

# ===================== 使用 nohup 启动脚本 =====================
cd "${base_dir}"

echo "============================================================"
echo "使用 nohup 启动 ${script_name}"
echo "============================================================"
echo "脚本路径: ${script_path}"
echo "日志文件: ${log_file}"
echo "PID 文件: ${pid_file}"
echo ""

# 使用 nohup 启动自动 eval 脚本
nohup bash "${script_path}" > "${log_file}" 2>&1 &

# 保存进程 ID
pid=$!
echo "${pid}" > "${pid_file}"

echo "✅ 自动 eval 脚本已在后台启动！"
echo "进程 ID (PID): ${pid}"
echo ""
echo "📝 常用命令："
echo "   查看运行日志: tail -f ${log_file}"
echo "   查看进程状态: ps aux | grep eval_results_datasets_5.sh | grep -v grep"
echo "   停止脚本: kill ${pid} (或 kill \$(cat ${pid_file}))"
echo "   检查 PID: cat ${pid_file}"
echo ""
echo "💡 提示:"
echo "   - 脚本会顺序遍历 results_datasets_5 下所有 sts.txt"
echo "   - 单个 run 的 eval 结果保存在对应 run 目录下 (eval.json / rank.png 等)"
echo "   - 即使终端关闭，脚本也会继续运行"
echo "============================================================"




