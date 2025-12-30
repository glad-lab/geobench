# 速度优化建议

## 当前性能问题

从日志分析发现：
- **每次迭代耗时约 413 秒**（约 6.9 分钟）
- **num_iter = 2000**，总时间估算：**2000 × 413秒 ≈ 9.6 天**（单个任务）
- **batch_size = 50**（可能偏小）

## 优化方案

### 1. 减少迭代次数（最有效）⭐

**当前配置**：
```bash
num_iter=2000
```

**建议修改**：
```bash
num_iter=500  # 或 1000
```

**效果**：可以将单个任务时间从 9.6 天减少到 2.4-4.8 天

**修改位置**：`iterate_datasets_5.sh` 第 15 行

### 2. 增加 batch_size（如果显存允许）

**当前配置**：
- 代码默认：`batch_size=200`
- 实际运行：`batch_size=50`（可能被显存限制）

**建议**：
- 如果 GPU 显存充足（A100 40GB），可以尝试增加到 100-150
- 需要修改 `rank_opt.py` 中的 `batch_size` 参数

**修改位置**：`rank_opt.py` 第 475 行附近

### 3. 调整显存优化参数

**当前配置**：
```bash
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True,max_split_size_mb:64,garbage_collection_threshold:0.6"
```

**问题**：`max_split_size_mb=64` 可能太小，导致频繁的内存分配/释放，影响速度

**建议**：
```bash
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.6"
```

**修改位置**：`iterate_datasets_5.sh` 第 21 行

### 4. 减少 num_samples（如果允许）

**当前配置**：`num_samples=512`（代码默认）

**建议**：如果精度要求不高，可以减少到 256 或 128

**修改位置**：`rank_opt.py` 中 `rank_opt` 函数调用处

### 5. 减少 num_sts_tokens

**当前配置**：`num_sts_tokens=30`（代码默认）

**建议**：可以减少到 20-25，可能略微影响效果但能提升速度

## 快速优化方案（推荐）

### 方案 A：保守优化（保持效果）

修改 `iterate_datasets_5.sh`：
```bash
num_iter=1000  # 从 2000 减少到 1000
```

**效果**：时间减半，约 4.8 天/任务

### 方案 B：激进优化（快速测试）

修改 `iterate_datasets_5.sh`：
```bash
num_iter=500   # 从 2000 减少到 500
```

同时调整显存优化：
```bash
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.6"
```

**效果**：时间减少到约 2-3 天/任务

### 方案 C：快速验证（最快）

修改 `iterate_datasets_5.sh`：
```bash
num_iter=200   # 快速验证用
test_iter=20   # 减少测试频率
```

**效果**：约 1 天/任务（但效果可能不够好）

## 实施步骤

1. **备份当前脚本**：
   ```bash
   cp iterate_datasets_5.sh iterate_datasets_5.sh.backup
   ```

2. **修改配置**：
   - 打开 `iterate_datasets_5.sh`
   - 修改 `num_iter` 参数
   - 可选：调整显存优化参数

3. **测试单个任务**：
   - 先运行一个任务验证速度
   - 检查结果质量是否可接受

4. **批量运行**：
   - 确认效果后，使用 `run_iterate_datasets_5.sh` 启动

## 注意事项

1. **效果 vs 速度权衡**：
   - 减少迭代次数可能影响优化效果
   - 建议先用较小的 `num_iter` 测试，确认效果后再决定

2. **显存限制**：
   - 增加 `batch_size` 或 `max_split_size_mb` 需要足够的显存
   - A100 40GB 通常可以支持更大的 batch_size

3. **任务总数**：
   - 即使单个任务优化到 2-3 天，200+ 个任务仍需要很长时间
   - 考虑是否需要运行所有任务，或先运行部分任务验证

## 监控建议

运行后监控：
```bash
# 查看当前任务进度
tail -f results_datasets_5_*/AdversarialSEO/books_media/self/llama/default/product1/run1/rank_opt_background.log

# 查看迭代速度
grep "Iteration" results_datasets_5_*/AdversarialSEO/books_media/self/llama/default/product1/run1/rank_opt_background.log | tail -5
```


