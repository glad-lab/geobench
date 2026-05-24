# datasets_5 - 精简数据集（每个算法最多5个商品种类）

这个目录包含了从 `Datasets_clean` 中提取的精简数据集，每个算法文件夹最多保留5个商品种类（按文件名排序，商品数量 >= 5）。

## 数据格式

所有数据集文件都采用 JSONL 格式（每行一个 JSON 对象），格式根据原始数据源有所不同。

- **GEO 数据集**: 保留原始字段（如 `name`, `description`）
- **Zero-Shot Rankers 数据集**: 保留原始字段（如 `name`, `description`）
- **其他数据集**: 统一格式包含 Name, Description, Price, Rating, Capacity, Ideal For 等字段

## 目录结构

```
datasets_5/
├── AdversarialSEO/          # Adversarial SEO 数据集（5个类别）
│   ├── books_media.jsonl
│   ├── cameras.jsonl
│   ├── computing_hardware.jsonl
│   ├── home_furniture.jsonl
│   └── kitchen_appliances.jsonl
├── GEO/                      # GEO 数据集（5个类别）
│   ├── accessories.jsonl
│   ├── action_figures.jsonl
│   ├── adhesives.jsonl
│   ├── air_compressors.jsonl
│   └── apparel.jsonl
├── RewriteToRank/            # Rewrite-to-Rank 数据集（5个类别）
│   ├── berrylook.jsonl
│   ├── best_buy.jsonl
│   ├── best_dresses.jsonl
│   ├── facebook_log_in.jsonl
│   └── flowers.jsonl
├── StealthRank/              # Stealth Rank 数据集（5个类别）
│   ├── air_compressor.jsonl
│   ├── air_purifier.jsonl
│   ├── automatic_garden_watering_system.jsonl
│   ├── barbecue_grill.jsonl
│   └── beard_trimmer.jsonl
├── llm-rank-optimizer/       # LLM Rank Optimizer 数据集（4个类别）
│   ├── books.jsonl
│   ├── cameras.jsonl
│   ├── coffee_machines.jsonl
│   └── election_articles.jsonl
└── Zero-Shot Rankers/        # Zero-Shot Rankers 数据集（5个类别）
    ├── action.jsonl
    ├── adventure.jsonl
    ├── animation.jsonl
    ├── childrens.jsonl
    └── comedy.jsonl
```

## 数据集统计

| 算法 | 文件数 | 商品总数 | 平均每个文件 |
|------|--------|----------|--------------|
| AdversarialSEO | 5 | 30 | 6.0 |
| GEO | 5 | 30 | 6.0 |
| RewriteToRank | 5 | 30 | 6.0 |
| StealthRank | 5 | 30 | 6.0 |
| llm-rank-optimizer | 4 | 24 | 6.0 |
| Zero-Shot Rankers | 5 | 30 | 6.0 |
| **总计** | **29** | **174** | **6.0** |

## 数据说明

- 每个算法文件夹包含 **最多 5 个商品类别**（按文件名排序，取前5个）
- 每个商品类别最多包含 **6 个商品**
- 数据来源于 `../Datasets_clean/` 目录和 `../Datasets/Zero-Shot Rankers/` 目录
- 包括 GEO 数据集（5 个类别）和 Zero-Shot Rankers 数据集（5 个类别）

## 使用示例

```python
import json

# 读取一个数据集文件
with open('datasets_5/StealthRank/coffee_machines.jsonl', 'r') as f:
    products = [json.loads(line) for line in f if line.strip()]

for product in products:
    print(f"{product['Name']}: {product['Price']}")
```
