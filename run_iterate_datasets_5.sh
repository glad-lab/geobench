#!/bin/bash
# 使用 nohup 后台启动 iterate_datasets_5.sh 脚本

set -euo pipefail

# ===================== 配置参数 =====================
base_dir="/home/exouser/Desktop/vscode/geobench"
script_name="iterate_datasets_5.sh"
script_path="${base_dir}/${script_name}"

# 日志文件（脚本本身的运行日志）
log_file="${base_dir}/run_iterate_datasets_5.log"
pid_file="${base_dir}/run_iterate_datasets_5.pid"

# ===================== 检查脚本是否存在 =====================
if [ ! -f "${script_path}" ]; then
    echo "❌ 错误: 脚本文件不存在: ${script_path}"
    exit 1
fi

# ===================== 检查是否已经在运行 =====================
if [ -f "${pid_file}" ]; then
    old_pid=$(cat "${pid_file}")
    if ps -p "${old_pid}" > /dev/null 2>&1; then
        echo "⚠️  警告: 脚本可能已经在运行中 (PID: ${old_pid})"
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

# 使用 nohup 启动脚本
nohup bash "${script_path}" > "${log_file}" 2>&1 &

# 保存进程 ID
pid=$!
echo "${pid}" > "${pid_file}"

echo "✅ 脚本已在后台启动！"
echo "进程 ID (PID): ${pid}"
echo ""
echo "📝 常用命令："
echo "   查看运行日志: tail -f ${log_file}"
echo "   查看进程状态: ps aux | grep ${script_name} | grep -v grep"
echo "   停止脚本: kill ${pid} (或 kill \$(cat ${pid_file}))"
echo "   检查 PID: cat ${pid_file}"
echo ""
echo "💡 提示:"
echo "   - 脚本会顺序执行所有任务（不是并行）"
echo "   - 每个任务的日志保存在对应的结果目录下"
echo "   - 即使终端关闭，脚本也会继续运行"
echo "============================================================"

