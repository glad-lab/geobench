#!/usr/bin/env python3
"""
清洗 RewriteToRank 数据集
- 从 train_data.json 读取数据（处理格式错误）
- 按 user_query 分组（每个 user_query 是一个 category）
- 按 item 数量从高到低排序，选择前 20 个 category
- 如果 item > 10，只取前 10 个；否则全部保留
- 输出到 datasets_clean/RewriteToRank/ 目录，每个类别一个 jsonl 文件
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path

# 配置路径
input_file = Path("/home/exouser/vscode/geobench/Datasets/RewriteToRank/train_data.json")
output_dir = Path("/home/exouser/vscode/geobench/datasets_clean/RewriteToRank")
reference_dir = Path("/home/exouser/vscode/geobench/Datasets_clean/RewriteToRank")

# 创建输出目录
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("开始清洗 RewriteToRank 数据集")
print("=" * 60)
print(f"输入文件: {input_file}")
print(f"输出目录: {output_dir}")
print()

# 读取数据（使用 ijson 流式解析，处理格式错误）
print("正在读取数据...")
data = []

try:
    # 尝试使用 ijson 流式解析
    try:
        import ijson
        with open(input_file, 'rb') as f:
            # 解析 JSON 数组中的每个对象
            parser = ijson.items(f, 'item')
            for item in parser:
                data.append(item)
        print(f"✓ 使用 ijson 成功加载，共 {len(data)} 条记录")
    except ImportError:
        print("⚠️  ijson 未安装，尝试其他方法...")
        raise
    except Exception as e:
        print(f"⚠️  ijson 解析失败: {e}")
        print("尝试使用修复后的 JSON 解析...")
        raise
except:
    # 备用方法：尝试修复 JSON 格式
    print("尝试修复 JSON 格式并解析...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试修复常见的 JSON 格式问题
        # 方法1: 直接尝试解析
        try:
            data = json.loads(content)
            print(f"✓ 直接解析成功，共 {len(data)} 条记录")
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON 格式错误: {e}")
            print("尝试使用正则表达式提取 JSON 对象...")
            
            # 方法2: 使用正则表达式提取每个 JSON 对象（改进版）
            # 匹配从 { 开始到 } 结束的完整对象，考虑嵌套
            print("使用正则表达式提取 JSON 对象...")
            # 更准确的正则：匹配完整的 JSON 对象
            # 使用状态机方法更可靠
            obj_start = -1
            brace_depth = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(content):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if in_string:
                    continue
                    
                if char == '{':
                    if brace_depth == 0:
                        obj_start = i
                    brace_depth += 1
                elif char == '}':
                    brace_depth -= 1
                    if brace_depth == 0 and obj_start >= 0:
                        obj_str = content[obj_start:i+1].strip().rstrip(',').strip()
                        try:
                            item = json.loads(obj_str)
                            if 'user_query' in item:
                                data.append(item)
                        except:
                            pass
                        obj_start = -1
            
            print(f"✓ 正则表达式提取完成，共 {len(data)} 条记录")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        exit(1)

if len(data) == 0:
    print("❌ 未能读取到任何数据，请检查文件格式")
    exit(1)

# 按 user_query 分组
print("\n正在按 user_query 分组...")
grouped_data = defaultdict(list)
for item in data:
    user_query = item.get('user_query', '').strip()
    if user_query:
        grouped_data[user_query].append(item)

print(f"✓ 共找到 {len(grouped_data)} 个不同的 user_query")

# 筛选：按 item 数量从高到低排序，选择前 20 个 category
print("\n正在筛选数据（按数量排序，选择前 20 个）...")
# 按 item 数量排序
sorted_categories = sorted(grouped_data.items(), key=lambda x: len(x[1]), reverse=True)

# 选择前 20 个
target_count = 20
selected_categories = sorted_categories[:target_count]

filtered_data = {}
for user_query, items in selected_categories:
    # 如果 > 10，只取前 10 个；否则全部保留
    if len(items) > 10:
        filtered_data[user_query] = items[:10]
        print(f"  {user_query}: {len(items)} -> {len(filtered_data[user_query])}")
    else:
        filtered_data[user_query] = items
        print(f"  {user_query}: {len(items)} -> {len(filtered_data[user_query])}")

print(f"✓ 筛选后共 {len(filtered_data)} 个类别")

# 生成文件名映射（参考 Datasets_clean 的命名方式）
def sanitize_filename(query):
    """将 user_query 转换为文件名"""
    # 移除特殊字符，替换空格为下划线
    filename = query.lower().strip()
    # 替换特殊字符
    filename = filename.replace(' ', '_')
    filename = filename.replace('/', '_')
    filename = filename.replace('\\', '_')
    filename = filename.replace(':', '_')
    filename = filename.replace('*', '_')
    filename = filename.replace('?', '_')
    filename = filename.replace('"', '_')
    filename = filename.replace('<', '_')
    filename = filename.replace('>', '_')
    filename = filename.replace('|', '_')
    # 移除多余的下划线
    filename = '_'.join(filter(None, filename.split('_')))
    return filename

# 保存到文件
print("\n正在保存文件...")
saved_count = 0
for user_query, items in filtered_data.items():
    filename = sanitize_filename(user_query)
    output_file = output_dir / f"{filename}.jsonl"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in items:
                # 确保输出格式与参考文件一致
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        saved_count += 1
        print(f"  ✓ {filename}.jsonl ({len(items)} 条记录)")
    except Exception as e:
        print(f"  ❌ 保存 {filename}.jsonl 失败: {e}")

print()
print("=" * 60)
print("清洗完成！")
print(f"共处理 {len(data)} 条原始记录")
print(f"共生成 {saved_count} 个类别文件")
print(f"输出目录: {output_dir}")
print("=" * 60)
