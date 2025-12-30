#!/usr/bin/env python3
"""
限制 datasets_5 文件夹中每个 jsonl 文件最多保留 8 个商品
"""
import json
import os
from pathlib import Path

def limit_products_in_file(file_path, max_products=6):
    """
    限制 JSONL 文件中的商品数量
    
    Args:
        file_path: JSONL 文件路径
        max_products: 最大商品数量
    """
    products = []
    
    # 读取所有商品
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    products.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"⚠️  警告: {file_path} 中有一行无法解析: {e}")
                    continue
    
    original_count = len(products)
    
    # 如果商品数量超过限制，只保留前 max_products 个
    if original_count > max_products:
        products = products[:max_products]
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            for product in products:
                f.write(json.dumps(product, ensure_ascii=False) + '\n')
        
        print(f"✅ {file_path}: {original_count} → {len(products)} 个商品")
        return True
    else:
        print(f"✓  {file_path}: {original_count} 个商品（无需修改）")
        return False

def main():
    base_dir = Path("/home/exouser/Desktop/vscode/geobench/datasets_5")
    max_products = 6
    
    if not base_dir.exists():
        print(f"❌ 错误: 目录不存在: {base_dir}")
        return
    
    print(f"📁 处理目录: {base_dir}")
    print(f"📊 限制每个文件最多 {max_products} 个商品\n")
    
    total_files = 0
    modified_files = 0
    
    # 遍历所有算法文件夹
    for algorithm_dir in base_dir.iterdir():
        if not algorithm_dir.is_dir():
            continue
        
        print(f"\n📂 {algorithm_dir.name}/")
        
        # 遍历该算法文件夹下的所有 jsonl 文件
        for jsonl_file in sorted(algorithm_dir.glob("*.jsonl")):
            total_files += 1
            if limit_products_in_file(jsonl_file, max_products):
                modified_files += 1
    
    print(f"\n{'='*60}")
    print(f"📊 统计:")
    print(f"   - 总文件数: {total_files}")
    print(f"   - 修改文件数: {modified_files}")
    print(f"   - 未修改文件数: {total_files - modified_files}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

