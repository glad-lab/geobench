#!/usr/bin/env python3
"""
更新 datasets_5/llm-rank-optimizer 文件夹，只保留指定的4个文件
- books.jsonl
- cameras.jsonl
- coffee_machines.jsonl
- election_articles.jsonl

每个文件保留前6个商品（根据下采样原则）
"""

import json
import os
from pathlib import Path

def update_llm_rank_optimizer_dataset():
    # 路径配置
    base_dir = Path(__file__).parent
    source_dir = base_dir / "Datasets/llm-rank-optimizer/data"
    output_dir = base_dir / "datasets_5/llm-rank-optimizer"
    
    # 要处理的文件列表
    files_to_process = [
        "books.jsonl",
        "cameras.jsonl",
        "coffee_machines.jsonl",
        "election_articles.jsonl"
    ]
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 删除旧文件（保留要处理的文件）
    print("清理旧文件...")
    for file in output_dir.glob("*.jsonl"):
        if file.name not in files_to_process:
            print(f"  删除: {file.name}")
            file.unlink()
    
    # 处理每个文件
    total_products = 0
    print(f"\n处理文件:")
    for filename in files_to_process:
        source_file = source_dir / filename
        output_file = output_dir / filename
        
        if not source_file.exists():
            print(f"  ⚠️  源文件不存在: {source_file}")
            continue
        
        # 读取原始数据
        products = []
        with open(source_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    products.append(json.loads(line))
        
        # 每个文件最多保留6个商品
        selected_products = products[:6]
        
        # 保存到输出目录
        with open(output_file, 'w', encoding='utf-8') as f:
            for product in selected_products:
                json.dump(product, f, ensure_ascii=False)
                f.write('\n')
        
        print(f"  ✅ {filename}: {len(products)} 个商品 -> 保留前 {len(selected_products)} 个")
        total_products += len(selected_products)
    
    print(f"\n✅ 完成！")
    print(f"   - 文件数: {len(files_to_process)}")
    print(f"   - 商品总数: {total_products}")
    print(f"   - 平均每个文件: {total_products / len(files_to_process):.1f}")
    
    return files_to_process, total_products

if __name__ == "__main__":
    update_llm_rank_optimizer_dataset()



