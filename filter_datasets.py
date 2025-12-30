#!/usr/bin/env python3
"""
过滤掉 Datasets_clean 目录下商品数量少于4个的文件
"""

import json
from pathlib import Path

MIN_PRODUCTS = 4
DATASETS_CLEAN_DIR = "Datasets_clean"


def filter_datasets():
    """过滤掉商品数量少于MIN_PRODUCTS的文件"""
    datasets_dir = Path(DATASETS_CLEAN_DIR)
    
    if not datasets_dir.exists():
        print(f"❌ 目录 {DATASETS_CLEAN_DIR} 不存在")
        return
    
    print("=" * 60)
    print("开始过滤数据集文件（删除商品数量少于4个的文件）")
    print("=" * 60)
    print()
    
    files_to_remove = []
    total_files = 0
    total_products_before = 0
    total_products_after = 0
    
    # 统计所有文件
    for jsonl_file in sorted(datasets_dir.rglob("*.jsonl")):
        total_files += 1
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            products = [l for l in f if l.strip()]
            count = len(products)
            total_products_before += count
            
            if count < MIN_PRODUCTS:
                files_to_remove.append((jsonl_file, count))
    
    print(f"📊 统计信息:")
    print(f"  - 总文件数: {total_files}")
    print(f"  - 总商品数（过滤前）: {total_products_before}")
    print(f"  - 需要删除的文件数: {len(files_to_remove)}")
    print()
    
    if files_to_remove:
        print("🗑️  将删除以下文件:")
        for file_path, count in sorted(files_to_remove):
            print(f"  - {file_path}: {count} 个商品")
        print()
        
        # 删除文件
        removed_count = 0
        for file_path, count in files_to_remove:
            try:
                file_path.unlink()
                removed_count += 1
                print(f"  ✅ 已删除: {file_path}")
            except Exception as e:
                print(f"  ❌ 删除失败 {file_path}: {e}")
        
        print()
        print(f"✅ 成功删除 {removed_count} 个文件")
    else:
        print("✅ 没有需要删除的文件")
    
    # 重新统计
    remaining_files = 0
    for jsonl_file in sorted(datasets_dir.rglob("*.jsonl")):
        remaining_files += 1
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            total_products_after += len([l for l in f if l.strip()])
    
    print()
    print("=" * 60)
    print("📊 过滤后的统计:")
    print(f"  - 剩余文件数: {remaining_files}")
    print(f"  - 总商品数（过滤后）: {total_products_after}")
    print(f"  - 删除的商品数: {total_products_before - total_products_after}")
    print("=" * 60)


if __name__ == "__main__":
    filter_datasets()

