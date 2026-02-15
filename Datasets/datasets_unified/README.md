# datasets_unified - 统一格式的数据集

这个目录包含了从不同算法数据集转换而来的统一格式数据。

## 数据格式

所有数据集文件都采用 JSONL 格式（每行一个 JSON 对象），格式如下：

```json
{
  "Name": "产品名称",
  "Description": "产品描述",
  "Price": "$价格",
  "Rating": 评分（浮点数）,
  "Capacity": "容量",
  "Ideal For": "适用人群"
}
```

**参考格式**: 与 `../data/coffee_machines.jsonl` 的格式一致。

## 目录结构

```
Datasets/datasets_unified/
├── AdversarialSEO/          # Adversarial SEO 数据集
│   ├── books_media.jsonl
│   ├── cameras.jsonl
│   ├── computing_hardware.jsonl
│   ├── home_furniture.jsonl
│   ├── kitchen_appliances.jsonl
│   └── lenses.jsonl
├── RewriteToRank/            # Rewrite-to-Rank 数据集
│   ├── flowers.jsonl
│   ├── weather.jsonl
│   └── ... (11个类别文件)
├── StealthRank/              # Stealth Rank 数据集
│   ├── json/                 # 原始 JSON 数据
│   │   ├── books.jsonl
│   │   ├── cameras.jsonl
│   │   └── coffee_machines.jsonl
│   └── ragroll/              # RAG Roll 数据 (53个类别文件)
│       ├── blender.jsonl
│       ├── coffee_maker.jsonl
│       └── ...
└── llm-rank-optimizer/       # LLM Rank Optimizer 数据集
    ├── books.jsonl
    ├── cameras.jsonl
    ├── coffee_machines.jsonl
    ├── election_articles.jsonl
    └── ... (扩展数据)
```

## 数据集统计

| 算法 | 文件数 | 商品总数 | 平均每个文件 |
|------|--------|----------|--------------|
| AdversarialSEO | 6 | 54 | 9.0 |
| RewriteToRank | 12 | 88 | 7.3 |
| StealthRank | 53 | 429 | 8.1 |
| llm-rank-optimizer | 9 | 84 | 9.3 |
| **总计** | **80** | **655** | **8.2** |

## 数据限制

- 每个商品类别最多包含 **10 个商品**
- 如果原始数据超过10个商品，只保留前10个
- 每个商品类别至少包含 **4 个商品**（少于4个的类别已被过滤）

## 转换说明

数据转换脚本：`../clean_datasets.py`

转换过程：
1. 从不同算法的原始数据集读取数据
2. 将不同格式的数据统一转换为目标格式
3. 清理和规范化字段名称
4. 限制每个类别的商品数量
5. 按算法和商品类别组织输出

## 使用示例

```python
import json

# 读取一个数据集文件
with open('Datasets/datasets_unified/StealthRank/coffee_machines.jsonl', 'r') as f:
    products = [json.loads(line) for line in f if line.strip()]

for product in products:
    print(f"{product['Name']}: {product['Price']}")
```

## 注意事项

1. 所有文件使用 UTF-8 编码
2. 某些字段可能为空字符串（如 `Capacity` 或 `Ideal For`），这取决于原始数据源
3. 价格格式可能不一致，有些可能从描述中提取，有些可能为 "$0"
4. 评分默认为 4.0（如果原始数据中没有评分信息）

