# iterate_datasets_5.sh 使用说明

## 功能说明

这个脚本用于遍历 `datasets_5` 文件夹下的所有算法数据集，为每个类别文件中的每个商品运行 `rank_opt.py`。

## 运行逻辑

1. **遍历算法文件夹**: 遍历 `datasets_5/` 下的每个算法文件夹（AdversarialSEO, GEO, RewriteToRank, StealthRank, llm-rank-optimizer）

2. **遍历类别文件**: 对每个算法文件夹，遍历其中的所有 `.jsonl` 类别文件

3. **遍历商品**: 对每个类别文件，统计商品数量，然后遍历每个商品（product 参数从 1 到商品数量）

4. **运行配置**:
   - `product`: 从 1 到类别文件中的商品数量
   - `run`: 固定为 1（每个商品只跑一次）
   - `mode`: "self"
   - `user_msg_type`: "default"
   - `target_llm`: "llama"
   - `num_iter`: 2000
   - `test_iter`: 50

5. **结果保存**: 
   - 结果保存在 `/home/exouser/Desktop/vscode/geobench/results_datasets_5/` 目录下
   - 目录结构: `results_datasets_5/{algorithm}/{category}/self/{target_llm}/{user_msg_type}/product{product_idx}/run{run}/`

## 使用方法

```bash
cd /home/exouser/Desktop/vscode/geobench
bash iterate_datasets_5.sh
```

## 特性

- **断点续传**: 如果某个任务已完成（存在 `done.txt` 文件），会自动跳过
- **错误处理**: 如果某个任务失败，会记录日志并继续执行下一个任务
- **日志记录**: 每个任务的日志保存在对应的结果目录下的 `rank_opt_background.log` 文件中

## 修改说明

为了支持任意的 catalog 名称，已修改 `rank_opt.py`：

1. 移除了 `--catalog` 参数的 `choices` 限制
2. 添加了通用 catalog 处理逻辑：如果 catalog 不在预定义列表中，会在 `data/` 目录下查找 `{catalog}.jsonl` 或 `{catalog}.json` 文件

## 注意事项

1. 脚本会将 `datasets_5` 下的类别文件复制到 `data/` 目录（使用类别名称作为文件名）
2. 脚本按顺序执行，每个任务完成后才执行下一个（不是并行执行）
3. 由于任务数量较多，整个脚本可能需要较长时间才能完成
4. 建议在后台运行或使用 screen/tmux 等工具

