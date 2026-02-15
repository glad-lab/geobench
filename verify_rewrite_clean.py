#!/usr/bin/env python3
"""验证清洗结果"""
from collections import Counter
import json
import re
from pathlib import Path

input_file = Path("Datasets/RewriteToRank/train_data.json")

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 使用状态机提取 JSON 对象
data = []
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

queries = [item['user_query'] for item in data]
counter = Counter(queries)
print(f'总记录数: {len(data)}')
print(f'总类别数: {len(counter)}')
print(f'>=10的类别数: {sum(1 for v in counter.values() if v >= 10)}')
print(f'\n>=10的类别详情:')
for query, count in sorted(counter.items(), key=lambda x: x[1], reverse=True):
    if count >= 10:
        print(f'  {query}: {count} 条')

