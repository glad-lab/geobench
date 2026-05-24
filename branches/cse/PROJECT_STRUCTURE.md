# 项目文件结构说明

## 目录结构总览

```
cse-ranking-manipulation-main/
│
├── 📁 核心实验代码
│   ├── attack.py              # TAP攻击算法核心实现
│   ├── adversarial.py         # 对抗攻击实验主程序
│   ├── natural.py             # 自然排名分析实验
│   ├── models.py              # LLM模型接口封装
│   ├── dataset.py             # 数据集加载与处理
│   ├── prompts.py             # 提示词模板
│   └── _types.py              # 数据类型定义
│
├── 📁 helpers/                # 辅助工具模块
│   ├── file_utils.py          # 文件操作工具
│   ├── plot_utils.py          # 绑图工具
│   ├── adversarial_statistics.py  # 统计分析
│   ├── app.py                 # Web应用后端
│   ├── app_interface.py       # Web应用接口
│   ├── home.html              # Web应用首页
│   └── run_server.sh          # 启动服务器脚本
│
├── 📁 scripts/                # 运行脚本
│   └── run.sh                 # 主实验运行脚本
│
├── 📁 dataset/                # 数据集目录
│   └── dataset/               # RAGDOLL数据集
│       └── {category}/        # 50个产品类别
│           ├── products.csv           # 产品元数据
│           ├── pages/                 # 原始HTML网页
│           ├── content/               # 提取的纯文本
│           ├── content_extract/       # LLM清洗后的文本
│           ├── content_truncate/      # 截断后的文本(实验用)
│           └── content_rewrite/       # 品牌替换后的文本
│
├── 📁 测试文件
│   ├── test_single.py         # 单类别自然排名测试
│   └── test_attack_single.py  # 单类别攻击测试
│
├── 📁 文档资料
│   ├── README.md              # 项目说明
│   ├── datasheet.md           # 数据集说明
│   ├── main_figure.png        # 主图
│   └── Ranking Manipulation for Conversational Search Engines.pdf  # 论文
│
├── 📁 压缩包（实验结果）
│   ├── dataset.zip            # 数据集压缩包
│   ├── out.zip                # 实验输出结果
│   ├── out_text.zip           # 文本输出结果
│   └── plots.zip              # 图表结果
│
└── 📁 配置文件
    ├── pyproject.toml         # Python依赖配置
    └── .gitignore             # Git忽略规则
```

---

## 文件功能详解

### 1. 核心实验代码

| 文件 | 功能 | 主要函数/类 |
|------|------|------------|
| `attack.py` | TAP攻击算法 | `get_adversarial_prompt()`, `run_target_and_evaluator()`, `poison_doc()` |
| `adversarial.py` | 对抗实验主程序 | `run_adversarial()`, `main()` |
| `natural.py` | 自然排名分析 | `run_natural_original()`, `run_natural_rewritten()` |
| `models.py` | LLM接口 | `load_model()`, `Models` dict |
| `dataset.py` | 数据加载 | `get_products()`, `get_categories()`, `user_query()` |
| `prompts.py` | 提示词模板 | `get_prompt_for_attacker()`, `get_prompt_for_target()` |
| `_types.py` | 类型定义 | `Product`, `Message`, `TreeNode`, `Role` |

### 2. 辅助模块 (helpers/)

| 文件 | 功能 |
|------|------|
| `file_utils.py` | 文件读写、目录创建 |
| `plot_utils.py` | matplotlib绑图函数 |
| `adversarial_statistics.py` | 攻击效果统计分析 |
| `app.py` | Flask Web应用 |
| `app_interface.py` | Web API接口 |

### 3. 数据文件格式

| 文件类型 | 格式 | 示例 |
|---------|------|------|
| `products.csv` | CSV | `Product,Brand,Model,URL` |
| `pages/*.html` | HTML | 原始网页内容 |
| `content/*.txt` | 纯文本 | BeautifulSoup提取 |
| `content_truncate/*.txt` | 纯文本(≤1000字符) | 实验使用的文档 |

---

## 文件调用关系

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户运行入口                               │
├─────────────────────────────────────────────────────────────────┤
│  python natural.py          →  自然排名实验                       │
│  python adversarial.py      →  对抗攻击实验                       │
│  python dataset.py          →  数据预处理                        │
│  python test_single.py      →  快速测试                          │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                        核心模块依赖                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  adversarial.py ──┬──→ attack.py ──→ models.py                 │
│                   │              ──→ prompts.py                │
│                   │              ──→ _types.py                 │
│                   │                                            │
│                   └──→ dataset.py ──→ helpers/file_utils.py   │
│                                  ──→ models.py                 │
│                                                                 │
│  natural.py ──────┬──→ attack.py                               │
│                   └──→ dataset.py                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 快速运行指南

```bash
# 1. 测试自然排名（单类别）
python test_single.py

# 2. 测试对抗攻击（单类别）
python test_attack_single.py

# 3. 完整自然排名实验
python natural.py --run-eval --target-model gpt-3.5 --num-runs 1

# 4. 完整对抗实验
python adversarial.py --run-eval --target-model gpt-3.5 --num-runs 1

# 5. 数据预处理
python dataset.py --truncate                    # 截断文档
python dataset.py --rewrite                     # 品牌替换
python dataset.py --reextract-content           # 重新提取内容
```
