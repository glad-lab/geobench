# llm-rank-optimizer 整合到 geobench 的漏洞报告

**状态**: ✅ 所有问题已修复

## 发现的漏洞

### 1. 数据文件路径问题

#### 1.1 `rank_opt.py` 中 books 目录的路径错误
**位置**: `rank_opt.py` 第 439 行
**问题**: 
- 当前代码使用: `catalog = "data/Datasets/StealthRank/json/books.jsonl"`
- 由于 `data` 是指向 `Datasets/llm-rank-optimizer/data` 的符号链接，这个路径会解析为 `Datasets/llm-rank-optimizer/data/Datasets/StealthRank/json/books.jsonl`，该路径不存在
- 正确的路径应该是: `Datasets/StealthRank/json/books.jsonl`

#### 1.2 `rank_opt.py` 中 kitchen_appliances 目录的路径错误
**位置**: `rank_opt.py` 第 457 行
**问题**:
- 当前代码使用: `catalog = "data/Datasets/AdversarialSEO/products_kitchen.json"`
- 该文件不存在
- 正确的路径应该是: `Datasets/AdversarialSEO/by-category/kitchen-appliances.json`

### 2. Bash 脚本中的硬编码路径问题

#### 2.1 `bash_test/test.sh`
**位置**: 第 10 行
**问题**: 
- 使用绝对路径: `/home/exouser/vscode/llm-rank-optimizer/rank_opt.py`
- 应该改为相对路径: `python rank_opt.py` 或使用当前目录的相对路径

#### 2.2 `bash_test/eval_self_single.sh`
**位置**: 第 11 行和第 26 行
**问题**:
- 使用绝对路径: `/home/exouser/Desktop/vscode/llm-rank-optimizer/eval_logs`
- 使用绝对路径: `/home/exouser/Desktop/vscode/llm-rank-optimizer/results4/...`
- 应该改为相对路径或使用 `geobench` 目录

#### 2.3 `bashscripts/eval_self2.sh`
**位置**: 第 11 行
**问题**:
- 使用绝对路径: `/home/exouser/vscode/llm-rank-optimizer/results2/...`
- 应该改为相对路径

### 3. 其他潜在问题

#### 3.1 缺失的文件/目录
- `llm-rank-optimizer` 中有 `figures/framework.png` 和 `result.md`，但 `geobench` 中没有这些文件（这可能不是关键问题）

#### 3.2 符号链接依赖
- `geobench/data` 是指向 `Datasets/llm-rank-optimizer/data` 的符号链接
- 代码依赖于这个符号链接的存在，如果链接断开，代码将无法正常工作
- 建议：要么保持符号链接，要么将代码中的 `data/` 路径全部更新为 `Datasets/llm-rank-optimizer/data/`

## 修复建议

1. ✅ 修复 `rank_opt.py` 中的路径引用
2. ✅ 更新所有 bash 脚本中的硬编码路径
3. 考虑是否需要保持符号链接，或者统一使用 `Datasets/llm-rank-optimizer/data/` 路径

## 已完成的修复

### 1. ✅ rank_opt.py 路径修复
- **books 路径**: 已从 `data/Datasets/StealthRank/json/books.jsonl` 修复为 `Datasets/StealthRank/json/books.jsonl`
- **kitchen_appliances 路径**: 已从 `data/Datasets/AdversarialSEO/products_kitchen.json` 修复为 `Datasets/AdversarialSEO/by-category/kitchen-appliances.json`

### 2. ✅ Bash 脚本路径修复
- **bash_test/test.sh**: 已从绝对路径修复为相对路径 `rank_opt.py`
- **bash_test/eval_self_single.sh**: 已修复日志目录和结果目录路径
- **bashscripts/eval_self2.sh**: 已修复结果目录路径
- **bashscripts_api/self_p1r1_api.sh**: 已从绝对路径修复为相对路径 `rank_opt_api.py`

### 验证结果
- ✅ `Datasets/StealthRank/json/books.jsonl` 路径验证通过
- ✅ `Datasets/AdversarialSEO/by-category/kitchen-appliances.json` 路径验证通过

