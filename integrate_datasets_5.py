#!/usr/bin/env python3
"""
从 Datasets_clean 中筛选商品数量 >= 5 的类别，整合到 datasets_5 文件夹
包括 GEO 数据集
"""

import shutil
from pathlib import Path

SOURCE_DIR = "Datasets_clean"
TARGET_DIR = "datasets_5"
MIN_PRODUCTS = 5  # 最小商品数量
MAX_CATEGORIES = 5  # 每个算法最多保留的类别数


def integrate_datasets_5():
    """整合商品数量 >= 5 的类别到 datasets_5"""
    source_path = Path(SOURCE_DIR)
    target_path = Path(TARGET_DIR)
    
    if not source_path.exists():
        print(f"❌ 源目录 {SOURCE_DIR} 不存在")
        return
    
    # 创建目标目录
    target_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("开始整合数据集到 datasets_5（商品数量 >= 5）")
    print("=" * 60)
    print()
    
    total_copied = 0
    total_products = 0
    total_skipped = 0
    
    # 处理每个算法文件夹
    for algorithm_dir in sorted(source_path.iterdir()):
        if not algorithm_dir.is_dir() or algorithm_dir.name in ['__pycache__', '.git']:
            continue
        
        algorithm_name = algorithm_dir.name
        print(f"📦 处理 {algorithm_name}...")
        
        # 获取所有 JSONL 文件
        jsonl_files = sorted(algorithm_dir.glob("*.jsonl"))
        
        if len(jsonl_files) == 0:
            print(f"  ⚠️  没有找到 JSONL 文件")
            continue
        
        # 创建目标算法目录
        target_algorithm_dir = target_path / algorithm_name
        target_algorithm_dir.mkdir(parents=True, exist_ok=True)
        
        # 筛选商品数量 >= MIN_PRODUCTS 的文件
        valid_files = []
        skipped_count = 0
        
        for source_file in jsonl_files:
            # 统计商品数量
            with open(source_file, 'r', encoding='utf-8') as f:
                product_count = len([l for l in f if l.strip()])
            
            # 只保留商品数量 >= MIN_PRODUCTS 的文件
            if product_count >= MIN_PRODUCTS:
                valid_files.append((source_file, product_count))
            else:
                skipped_count += 1
        
        # 按文件名排序，只保留前 MAX_CATEGORIES 个
        valid_files.sort(key=lambda x: x[0].name)
        files_to_copy = valid_files[:MAX_CATEGORIES]
        
        # 复制文件
        copied_count = 0
        products_count = 0
        
        for source_file, product_count in files_to_copy:
            target_file = target_algorithm_dir / source_file.name
            shutil.copy2(source_file, target_file)
            copied_count += 1
            products_count += product_count
            print(f"  ✅ {source_file.name}: {product_count} 个商品")
        
        total_copied += copied_count
        total_products += products_count
        total_skipped += skipped_count + (len(valid_files) - len(files_to_copy))
        
        if len(valid_files) > MAX_CATEGORIES:
            print(f"  📊 {algorithm_name}: {copied_count} 个文件（跳过 {skipped_count} 个商品不足的，{len(valid_files) - len(files_to_copy)} 个超出限制）, {products_count} 个商品")
        else:
            print(f"  📊 {algorithm_name}: {copied_count} 个文件（跳过 {skipped_count} 个商品不足的）, {products_count} 个商品")
        print()
    
    # 复制 README.md（如果存在且目标目录没有）
    readme_source = source_path / "README.md"
    readme_target = target_path / "README.md"
    if readme_source.exists() and not readme_target.exists():
        shutil.copy2(readme_source, readme_target)
        print(f"✅ 已复制 README.md")
        print()
    
    print("=" * 60)
    print("✅ 整合完成！")
    print(f"📊 统计信息:")
    print(f"  - 复制的文件数: {total_copied}")
    print(f"  - 跳过的文件数: {total_skipped} (商品数 < {MIN_PRODUCTS})")
    print(f"  - 总商品数: {total_products}")
    print(f"  - 输出目录: {target_path}")
    print("=" * 60)


if __name__ == "__main__":
    integrate_datasets_5()

