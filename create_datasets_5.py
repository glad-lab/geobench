#!/usr/bin/env python3
"""
从 Datasets_clean 中提取每个算法文件夹的前5个商品种类，保存到 datasets_5 文件夹
"""

import shutil
from pathlib import Path

SOURCE_DIR = "Datasets_clean"
TARGET_DIR = "datasets_5"
NUM_CATEGORIES = 5


def create_datasets_5():
    """创建只包含前5个商品种类的数据集"""
    source_path = Path(SOURCE_DIR)
    target_path = Path(TARGET_DIR)
    
    if not source_path.exists():
        print(f"❌ 源目录 {SOURCE_DIR} 不存在")
        return
    
    # 创建目标目录
    target_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("开始创建 datasets_5（每个算法保留前5个商品种类）")
    print("=" * 60)
    print()
    
    total_copied = 0
    total_products = 0
    
    # 处理每个算法文件夹
    for algorithm_dir in sorted(source_path.iterdir()):
        if not algorithm_dir.is_dir() or algorithm_dir.name in ['__pycache__', '.git']:
            continue
        
        algorithm_name = algorithm_dir.name
        print(f"📦 处理 {algorithm_name}...")
        
        # 获取所有 JSONL 文件并按名称排序
        jsonl_files = sorted(algorithm_dir.glob("*.jsonl"))
        
        if len(jsonl_files) == 0:
            print(f"  ⚠️  没有找到 JSONL 文件")
            continue
        
        # 只保留前 NUM_CATEGORIES 个文件
        files_to_copy = jsonl_files[:NUM_CATEGORIES]
        
        # 创建目标算法目录
        target_algorithm_dir = target_path / algorithm_name
        target_algorithm_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制文件
        copied_count = 0
        products_count = 0
        for source_file in files_to_copy:
            target_file = target_algorithm_dir / source_file.name
            shutil.copy2(source_file, target_file)
            copied_count += 1
            
            # 统计商品数量
            with open(target_file, 'r', encoding='utf-8') as f:
                products_count += len([l for l in f if l.strip()])
            
            print(f"  ✅ 已复制: {source_file.name}")
        
        total_copied += copied_count
        total_products += products_count
        print(f"  📊 {algorithm_name}: {copied_count} 个文件, {products_count} 个商品")
        print()
    
    # 复制 README.md（如果存在）
    readme_source = source_path / "README.md"
    if readme_source.exists():
        readme_target = target_path / "README.md"
        shutil.copy2(readme_source, readme_target)
        print(f"✅ 已复制 README.md")
        print()
    
    print("=" * 60)
    print("✅ 创建完成！")
    print(f"📊 统计信息:")
    print(f"  - 总文件数: {total_copied}")
    print(f"  - 总商品数: {total_products}")
    print(f"  - 输出目录: {target_path}")
    print("=" * 60)


if __name__ == "__main__":
    create_datasets_5()

