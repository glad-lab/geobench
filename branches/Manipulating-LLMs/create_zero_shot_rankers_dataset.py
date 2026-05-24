#!/usr/bin/env python3
"""
根据 datasets_5/README.md 的下采样原则，从 Zero-Shot Rankers 数据集中筛选数据
- 每个算法文件夹最多保留5个商品种类（按文件名排序，商品数量 >= 5）
- 每个商品类别最多包含6个商品
"""

import json
import os
from pathlib import Path

def create_zero_shot_rankers_dataset():
    # 路径配置
    base_dir = Path(__file__).parent
    input_file = base_dir / "Datasets/Zero-Shot Rankers/unified_dataset.json"
    output_dir = base_dir / "datasets_5/Zero-Shot Rankers"
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取原始数据
    print(f"读取数据文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 筛选类别：按名称排序，选择商品数量 >= 5 的类别
    categories = [(k, v) for k, v in sorted(data.items()) if len(v) >= 5]
    
    # 取前5个类别
    selected_categories = categories[:5]
    
    print(f"\n总类别数: {len(categories)}")
    print(f"选择的类别数: {len(selected_categories)}")
    print("\n选择的类别:")
    for cat_name, items in selected_categories:
        print(f"  {cat_name}: {len(items)} 个商品 -> 保留前 6 个")
    
    # 处理每个类别
    total_products = 0
    for cat_name, items in selected_categories:
        # 每个类别最多保留6个商品
        selected_items = items[:6]
        
        # 转换为 JSONL 格式（每行一个 JSON 对象）
        # 处理文件名：转小写，替换空格和单引号
        filename = cat_name.lower().replace(' ', '_').replace("'", '')
        output_file = output_dir / f"{filename}.jsonl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in selected_items:
                # 保持原始格式（name, description）
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        
        print(f"  ✅ 已保存: {output_file} ({len(selected_items)} 个商品)")
        total_products += len(selected_items)
    
    print(f"\n✅ 完成！")
    print(f"   - 类别数: {len(selected_categories)}")
    print(f"   - 商品总数: {total_products}")
    print(f"   - 平均每个文件: {total_products / len(selected_categories):.1f}")
    
    return selected_categories, total_products

if __name__ == "__main__":
    create_zero_shot_rankers_dataset()

