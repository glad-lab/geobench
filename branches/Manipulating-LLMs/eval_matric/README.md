# eval_matric

基于 `Results_new` 目录计算论文中的评估指标：NRG、Success@α、Promote@α、KVR、PPL-R。

- **数据来源**：`Results_new` 下各 run 的 `rank.csv`、`exp_config.json`、`sts.txt` 以及 catalog jsonl。
- **PPL 模型**：使用每个 run 的 `exp_config.json` 里 `Model path(s)` 指定的本地模型（如 Llama-3.1-8B-Instruct）计算 PPL(orig) 与 PPL(adv)，再算 PPL-R；同一路径的模型会缓存，只加载一次。

## 用法

在仓库根目录执行：

```bash
# 默认：Results_new，输出 eval_matric/results_metrics.csv，含 PPL-R（用 exp_config 里的 Llama）
python eval_matric/eval_metrics.py

# 指定结果目录与输出 CSV
python eval_matric/eval_metrics.py --results_root Results_new --out_csv eval_matric/results_metrics.csv

# 不计算 PPL-R（只算 NRG / Success@α / Promote@α / KVR），更快
python eval_matric/eval_metrics.py --skip_ppl

# 自定义 α 与 PPL 截断长度
python eval_matric/eval_metrics.py --alphas 0.1,0.2,0.5 --ppl_max_length 1024
```

## 输出列

- `algorithm`, `category`, `product`, `run`, `run_dir`, `catalog_path`, `L`, `num_iter`, `model_path`
- `r_before`, `r_after`, `r_best`, `last_iter`, `nrg_raw`, `nrg`
- `success@0.1`, `success@0.2`, `promote@0.1`, `promote@0.2`（随 `--alphas` 变化）
- `kvr`, `kvr_available`
- `ppl_orig`, `ppl_adv`, `ppl_r`（未 `--skip_ppl` 时）
