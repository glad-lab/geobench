#!/usr/bin/env python3
"""
将 GEO/unified_dataset.json 转换为统一的 JSONL 格式
目标格式参考: data/coffee_machines.jsonl
"""

import json
import os
import re
from pathlib import Path

SOURCE_FILE = "Datasets/GEO/unified_dataset.json"
OUTPUT_DIR = "Datasets_clean/GEO"
MAX_PRODUCTS_PER_CATEGORY = 10  # 每个类别最多保留10个商品


def sanitize_category_name(category: str) -> str:
    """清理类别名称，使其适合作为文件名"""
    category = re.sub(r'[^\w\s-]', '', category)
    category = re.sub(r'[-\s]+', '_', category)
    return category.lower()


def convert_geo_dataset():
    """转换 GEO unified_dataset.json 文件"""
    source_path = Path(SOURCE_FILE)
    output_path = Path(OUTPUT_DIR)
    
    if not source_path.exists():
        print(f"❌ 源文件 {SOURCE_FILE} 不存在")
        return
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("开始转换 GEO unified_dataset.json")
    print("=" * 60)
    print(f"源文件: {source_path}")
    print(f"输出目录: {output_path}")
    print()
    
    # 读取 JSON 文件
    with open(source_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, dict):
        print(f"❌ 数据格式错误，期望字典类型，得到 {type(data)}")
        return
    
    total_categories = len(data)
    total_files = 0
    total_products = 0
    
    print(f"📦 发现 {total_categories} 个商品类别")
    print()
    
    # 处理每个类别
    for category_name, products_list in sorted(data.items()):
        if not isinstance(products_list, list):
            print(f"  ⚠️  {category_name}: 跳过（不是列表格式）")
            continue
        
        # 清理类别名称作为文件名
        sanitized_category = sanitize_category_name(category_name)
        output_file = output_path / f"{sanitized_category}.jsonl"
        
        # 限制商品数量（保留原始字段，不做任何修改）
        products_to_save = products_list[:MAX_PRODUCTS_PER_CATEGORY]
        
        # 只保存至少有1个商品的文件
        if len(products_to_save) == 0:
            continue
        
        # 写入 JSONL 文件（直接输出原始数据，不修改字段）
        with open(output_file, 'w', encoding='utf-8') as f:
            for product in products_to_save:
                f.write(json.dumps(product, ensure_ascii=False) + '\n')
        
        total_files += 1
        total_products += len(products_to_save)
        print(f"  ✅ {sanitized_category}: {len(products_to_save)} 个商品 -> {output_file}")
    
    print()
    print("=" * 60)
    print("✅ 转换完成！")
    print(f"📊 统计信息:")
    print(f"  - 总类别数: {total_categories}")
    print(f"  - 生成文件数: {total_files}")
    print(f"  - 总商品数: {total_products}")
    print(f"  - 输出目录: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    convert_geo_dataset()

