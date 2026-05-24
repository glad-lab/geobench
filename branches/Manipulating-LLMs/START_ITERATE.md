# 启动 iterate_datasets_5.sh 脚本

## 方式一：使用包装脚本（推荐）✨

最简单的方式，使用提供的包装脚本：

```bash
cd /home/exouser/Desktop/vscode/geobench
bash run_iterate_datasets_5.sh
```

或者直接运行（脚本已有执行权限）：

```bash
cd /home/exouser/Desktop/vscode/geobench
./run_iterate_datasets_5.sh
```

**优点**：
- 自动使用 nohup 后台运行
- 即使终端关闭也不会中断
- 自动管理 PID 文件
- 日志统一保存到 `run_iterate_datasets_5.log`

### 查看运行状态

```bash
# 查看脚本运行日志
tail -f /home/exouser/Desktop/vscode/geobench/run_iterate_datasets_5.log

# 查看进程状态
ps aux | grep iterate_datasets_5.sh | grep -v grep

# 查看 PID
cat /home/exouser/Desktop/vscode/geobench/run_iterate_datasets_5.pid

# 停止脚本
kill $(cat /home/exouser/Desktop/vscode/geobench/run_iterate_datasets_5.pid)
```

## 方式二：手动使用 nohup

```bash
cd /home/exouser/Desktop/vscode/geobench
nohup bash iterate_datasets_5.sh > iterate_datasets_5_run.log 2>&1 &

# 查看日志
tail -f iterate_datasets_5_run.log
```

## 方式三：使用 screen

```bash
# 1. 创建一个新的 screen 会话
screen -S iterate_datasets

# 2. 进入项目目录并运行脚本
cd /home/exouser/Desktop/vscode/geobench
bash iterate_datasets_5.sh

# 3. 按 Ctrl+A 然后按 D 来分离会话（脚本继续在后台运行）

# 4. 重新连接会话查看进度
screen -r iterate_datasets
```

## 方式四：使用 tmux

```bash
# 1. 创建一个新的 tmux 会话
tmux new -s iterate_datasets

# 2. 进入项目目录并运行脚本
cd /home/exouser/Desktop/vscode/geobench
bash iterate_datasets_5.sh

# 3. 按 Ctrl+B 然后按 D 来分离会话

# 4. 重新连接会话
tmux attach -t iterate_datasets
```

## 日志文件位置

### 1. 脚本运行日志（如果使用包装脚本或 nohup）

- 使用包装脚本：`/home/exouser/Desktop/vscode/geobench/run_iterate_datasets_5.log`
- 手动 nohup：`/home/exouser/Desktop/vscode/geobench/iterate_datasets_5_run.log`

### 2. 每个任务的运行日志（主要日志）

每个任务的日志保存在：

```
/home/exouser/Desktop/vscode/geobench/results_datasets_5_{timestamp}/{algorithm}/{category}/self/llama/default/product{product_idx}/run1/rank_opt_background.log
```

示例：
```
results_datasets_5_20251226_012817/AdversarialSEO/books_media/self/llama/default/product1/run1/rank_opt_background.log
results_datasets_5_20251226_012817/GEO/accessories/self/llama/default/product1/run1/rank_opt_background.log
```

## 检查任务状态

### 查看已完成的任务

```bash
# 统计已完成的任务数（查找所有 done.txt 文件）
find /home/exouser/Desktop/vscode/geobench/results_datasets_5_* -name "done.txt" | wc -l

# 列出所有已完成的任务
find /home/exouser/Desktop/vscode/geobench/results_datasets_5_* -name "done.txt" -exec dirname {} \;
```

### 查看正在运行的任务

```bash
# 查看所有 rank_opt.py 进程
ps aux | grep rank_opt.py | grep -v grep
```

## 停止任务

### 停止脚本本身

```bash
# 如果使用包装脚本
kill $(cat /home/exouser/Desktop/vscode/geobench/run_iterate_datasets_5.pid)

# 或查找进程并停止
pkill -f "iterate_datasets_5.sh"
```

### 停止正在运行的任务（不推荐）

```bash
# 停止所有 rank_opt.py 进程（会中断当前正在运行的任务）
pkill -f "rank_opt.py"
```

⚠️ **注意**：停止脚本后，当前正在运行的任务会继续完成，但后续任务不会启动。

## 重要说明

1. **顺序执行**：任务会一个个顺序执行，不是并行运行
2. **断点续传**：如果任务已完成（存在 `done.txt`），脚本会自动跳过，可以安全地重新运行
3. **结果目录**：每次运行会创建新的带时间戳的目录，不会覆盖之前的结果
4. **资源使用**：所有任务使用 GPU 0，注意显存限制
