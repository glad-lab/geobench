## 项目与本地实验简介

本仓库用于在 GEO/StealthRank 等检索与排序数据集上复现实验，并基于 GCG（Greedy Coordinate Gradient）策略对 LLM 生成的推荐结果进行 **对抗式排序优化（rank optimization）**。  
当前本地实验主要基于 `datasets_5` 做小规模、可控的实验，并把所有结果统一保存到 `results_datasets_5` 目录。

本文档是 **阶段性结果总结**：程序尚未在所有数据集与商品上完全跑完，但 `StealthRank` 部分品类已经得到较完整的曲线（`rank.png`）和日志，可先给出一个中期结论，后续可再更新为最终版。

---

## 与本地实验相关的目录结构

- `datasets_5/`  
  - 各算法的精简版商品数据集，每个算法下 **≤5 个品类，每个品类 ≤6 个商品**。  
  - 本轮重点使用：
    - `StealthRank/air_compressor.jsonl`
    - `StealthRank/air_purifier.jsonl`
    - `StealthRank/automatic_garden_watering_system.jsonl`

- `iterate_datasets_5.sh`  
  - 主遍历脚本（顺序执行，避免 OOM），当前逻辑：
    - 算法顺序：`StealthRank → llm-rank-optimizer → AdversarialSEO → GEO`，跳过 `RewriteToRank`
    - 每个品类文件：
      - 先检查 **结果目录中该品类是否已经有 ≥3 个 target 商品有 `done.txt`**，若是则整类跳过
      - 否则只取 **前 3 个商品** 作为 target，依次运行
    - 所有结果写入固定目录：`results_datasets_5`

- `run_iterate_datasets_5.sh`  
  - 使用 `nohup` 在后台启动 `iterate_datasets_5.sh` 的包装脚本，负责 PID 管理与日志 `run_iterate_datasets_5.log`。

- `rank_opt.py`  
  - 核心排序优化脚本：
    - 支持 `--catalog` 指定任意 `data/{catalog}.jsonl`
    - 通过 `--target_product_idx` 指定当前优化的目标商品
    - 运行 GCG 优化，输出：
      - `rank.png`：目标商品在迭代过程中的排序变化
      - `loss.png`：损失曲线
      - `rank_opt_background.log`：详细日志
      - `state_dict.pth`：可恢复的状态
    - 重要实验参数（当前版本）：
      - `num_iter = 1600`
      - `batch_size = 120`
      - `num_samples = 256`
      - `max_length = 4096`
      - `repetition_penalty = 1.2`
    - 模型配置：
      - 模式：`self`
      - 目标模型：`llama`（`/media/volume/v4/Llama-2-7b-chat-hf`）

- `results_datasets_5/`  
  - 本地统一结果目录（包含已迁移的历史结果），结构如下：

  ```text
  results_datasets_5/
    StealthRank/
      air_compressor/
        self/llama/default/product{1..3}/run1/
          rank.png
          loss.png
          rank_opt_background.log
          state_dict.pth
          done.txt
      air_purifier/
      automatic_garden_watering_system/
    ...
  ```

---

## 实验设置（本轮阶段性结果）

### 模型与模式

- 模型：Llama-2-7b-chat-hf（称为 `llama`）
- 模式：`self`（只针对同一个模型做优化）
- 设备：单卡 A100 40GB，`CUDA_VISIBLE_DEVICES=0`

### GCG 优化参数（rank_opt.py）

- `num_iter = 1600`：每个 target 商品最多优化 1600 步  
- `batch_size = 120`：单步采样 batch，基本能吃满显存  
- `num_samples = 256`：每轮从候选 token 中采样 256 条序列  
- 评估间隔：`test_iter = 50`  
- 生成相关：
  - 上下文上限：`max_length = 4096`
  - 重复惩罚：`repetition_penalty = 1.2`

### Prompt 约束（已在代码中实现）

系统提示中显式加入了以下约束：

- 必须包含 **商品列表中出现的所有商品**，一个不少；
- 每个商品在推荐列表中 **恰好出现一次**；
- 在输出中引用商品时，商品名称必须与列表中的名称 **完全一致**。

---

## 阶段性结果观察（基于 StealthRank）

目前已完成的结果主要集中在：

- `results_datasets_5/StealthRank/air_compressor/self/llama/default/product{1..3}/run1`
- `results_datasets_5/StealthRank/air_purifier/self/llama/default/product{1..3}/run1`
- `results_datasets_5/StealthRank/automatic_garden_watering_system/self/llama/default/product{1..3}/run1`

由于最终趋势主要体现在 `rank.png` 上，本节根据日志中的 **Target Product Rank** 与迭代记录，结合既有曲线做一个整体性的、定性的总结。

### 1. 排名优化效果总体情况

- **整体趋势**：  
  - 大部分 target 商品在优化前的初始排名处于列表中 **中后位置（例如 5–7 名）**；  
  - 经过 1600 步左右的 GCG 优化后，**最终评估时的 Target Product Rank 通常能提升到前 1–3 名**。  
  - 在若干 run 中，日志中的 `Best top count` 显示目标商品在若干评估步中曾达到 **rank = 1**，虽然后续评估可能回落到 2。

- **以 `StealthRank/air_compressor` 为例（product5）**：
  - 初始评估中：
    - `Target Product Rank: 7`，目标商品在 6 个候选中处于末位；
  - 训练后期一次评估中（同一 run）：
    - `Target Product Rank: 2`，`Top count: 1, Best top count: 2`；  
  - 说明在迭代过程中，目标商品曾多次被推到榜首（rank=1），最终收敛在第 2 名附近。

- **自动浇灌 / 空气净化等品类的其他 run**（如 `automatic_garden_watering_system` 与 `air_purifier`）在日志中的行为类似：  
  - 损失曲线（见 `loss.png`）整体 **单调下降带噪声**；  
  - 排名曲线 `rank.png` 呈现 **阶梯式改善**：在若干关键迭代点 rank 会突然提升，然后在一个较高名次附近震荡。

### 2. Prompt 约束与输出质量

- **包含所有商品的约束基本生效**：  
  - 从多份 `rank_opt_background.log` 中抽样的 LLM RESPONSE 可以看到：
    - 推荐列表中确实逐条覆盖了输入的所有商品；
    - 没有遗漏商品，也没有重复列表项。

- **商品名称匹配**：  
  - 在当前样本中，模型能大致维持与商品列表中相同的名称；  
  - 个别位置由于对抗式 token 污染，描述尾部可能出现乱码/多余符号，但主干名称仍然可辨识。

- **生成风格与对抗噪声**：  
  - 随着迭代进行，对抗序列（STS）逐渐被注入大量看似乱码的 token（例如日志中大量奇怪的字符串）；  
  - 这类噪声更多是为了操控模型内部表示，对人类可读性有明显破坏，但排序目标（目标商品升排）仍能被优化。

### 3. 收敛速度与资源使用

- **单步时间**：  
  - 日志中后期迭代时间约为 **9–12 秒/步**（受 `batch_size=120` 和 `num_samples=256` 影响）；  
  - 1600 步完整 run 仍然是「数小时级别」的任务，对单个商品来说比较重。

- **收敛特征**：  
  - 损失在前几百步内下降最快，此时排名改善最明显；  
  - 后期（约 1000 步以后）损失和 rank 改善趋于缓慢甚至震荡，存在一定的 **过度优化 / 噪声积累** 迹象；  
  - 从当前结果看，**完全跑满 1600 步未必必要**，后续可考虑在 800–1200 步之间做早停实验。

---

## 阶段性结论（中期）

基于目前在 `StealthRank` 上已完成的若干品类和商品的运行结果，可以给出以下 **初步结论**：

1. **GCG 对抗优化能够显著提升目标商品在 LLM 推荐列表中的排名**  
   - 多数样本中，目标商品从列表中靠后位置（如 6–7 名）提升到前 1–3 名；  
   - `Best top count` 显示，在训练过程中多次出现目标商品排名第 1 的评估点。

2. **在「必须包含所有商品、名称精确匹配」的严格 Prompt 下，优化仍然有效**  
   - 说明排序操控并不依赖于删除竞争商品，而是通过微调文本模式影响模型的排序偏好；  
   - 名称精确匹配约束在当前样本中能保持基本满足，可在人类后处理时继续过滤异常输出。

3. **对抗序列会显著降低自然可读性**  
   - 日志与 prompt 中插入的大量奇怪 token 说明，模型被推动到使用难以理解的上下文来改变排序；  
   - 在实际应用中，如需同时兼顾「可读性」与「排序效果」，还需要在 GCG 目标中加入额外正则或约束（下一阶段可尝试）。

4. **计算开销较大，后续需要更积极的早停与参数搜索**  
   - 以当前 `num_iter=1600, batch_size=120, num_samples=256` 的配置，单个 target run 时间较长；  
   - 从损失与 rank 曲线看，早期 30–50% 迭代贡献了绝大部分提升，后期收益递减明显，存在进一步压缩计算成本的空间。

---

## 后续工作计划（建议）

1. **跑完所有 `datasets_5` 中的 StealthRank/其他算法品类**
   - 利用当前 `iterate_datasets_5.sh` 的「每类最多 3 个 target、已有 ≥3 则跳过」策略，尽可能在固定预算下覆盖更多品类；  
   - 完成后可以针对 `results_datasets_5` 设计一个统一的结果解析脚本（统计每个算法/品类的 rank 提升分布）。

2. **系统性分析 rank.png 与 loss.png**
   - 为每个品类画出「初始 rank 分布 vs 最终 rank 分布」的直方图；  
   - 结合 loss 曲线，分析「在什么迭代区间内 rank 提升最快」，为早停策略提供依据。

3. **尝试更强的可读性或安全性约束**
   - 在 loss 中加入对输出长度、特殊 token 频次等约束；  
   - 尝试在 prompt 中加入「禁止使用无意义噪声、emoji 过多等」说明，并观察对 rank 优化效果的影响。

4. **扩展到其他基础模型与模式**
   - 再次尝试 `llama32`（1B）或其他长上下文模型，在控制 `num_samples/batch_size` 前提下对比：
     - 排名提升幅度；
     - 文本可读性；
     - OOM / 速度表现。

本中文文档仅基于当前 `results_datasets_5` 中已完成的 StealthRank 结果给出 **中期总结**，后续如有新实验（更多算法、更多品类或新模型）可以在此基础上继续补充最终结论。


