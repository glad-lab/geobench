#!/usr/bin/env python3
"""
将不同算法的数据集转换为统一的 JSONL 格式
目标格式参考: geobench/data/coffee_machines.jsonl
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

# 目标格式的字段（基于 geobench/data/coffee_machines.jsonl）
TARGET_FORMAT_FIELDS = ["Name", "Description", "Price", "Rating", "Capacity", "Ideal For"]

# 输出目录
OUTPUT_DIR = "Datasets_clean"
MAX_PRODUCTS_PER_CATEGORY = 10


def sanitize_category_name(category: str) -> str:
    """清理类别名称，使其适合作为文件名"""
    # 移除特殊字符，替换空格为下划线
    category = re.sub(r'[^\w\s-]', '', category)
    category = re.sub(r'[-\s]+', '_', category)
    return category.lower()


def extract_price_from_description(description: str) -> Optional[str]:
    """尝试从描述中提取价格"""
    # 查找 $XX.XX 格式的价格
    price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', description)
    if price_match:
        return price_match.group()
    return None


def extract_rating_from_description(description: str) -> Optional[float]:
    """尝试从描述中提取评分"""
    # 查找 X.X stars 或 X.X/5.0 格式的评分
    rating_match = re.search(r'(\d\.\d)\s*(?:stars?|/5)', description, re.IGNORECASE)
    if rating_match:
        try:
            return float(rating_match.group(1))
        except:
            pass
    return None


def convert_to_target_format(item: Dict[str, Any], source: str) -> Dict[str, Any]:
    """将不同格式的商品数据转换为目标格式"""
    result = {}
    
    # 提取 Name
    result["Name"] = item.get("Name") or item.get("name") or item.get("title", "")
    
    # 提取 Description
    description = (
        item.get("Description") or 
        item.get("description") or 
        item.get("Natural") or 
        item.get("text", "")
    )
    result["Description"] = description
    
    # 提取 Price（如果存在，否则尝试从描述中提取）
    result["Price"] = item.get("Price") or item.get("price") or extract_price_from_description(description) or "$0"
    
    # 提取 Rating（如果存在，否则尝试从描述中提取）
    rating = item.get("Rating") or item.get("rating")
    if rating is None:
        rating = extract_rating_from_description(description)
    if rating is not None:
        try:
            result["Rating"] = float(rating)
        except:
            result["Rating"] = 4.0
    else:
        result["Rating"] = 4.0
    
    # 提取 Capacity（如果存在）
    result["Capacity"] = item.get("Capacity") or item.get("capacity") or ""
    
    # 提取 Ideal For（如果存在）
    result["Ideal For"] = item.get("Ideal For") or item.get("Ideal_For") or item.get("ideal_for") or item.get("Genre") or item.get("genre") or ""
    
    return result


def process_stealthrank_json(source_dir: Path, output_dir: Path):
    """处理 StealthRank/json/ 目录下的数据"""
    json_dir = source_dir / "json"
    if not json_dir.exists():
        print(f"  ⚠️  StealthRank/json 目录不存在")
        return
    
    output_algorithm_dir = output_dir / "StealthRank"
    output_algorithm_dir.mkdir(parents=True, exist_ok=True)
    
    for jsonl_file in json_dir.glob("*.jsonl"):
        category_name = jsonl_file.stem  # 例如: books, cameras, coffee_machines
        output_file = output_algorithm_dir / f"{category_name}.jsonl"
        
        products = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    products.append(convert_to_target_format(item, "StealthRank"))
        
        # 限制商品数量
        products = products[:MAX_PRODUCTS_PER_CATEGORY]
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            for product in products:
                f.write(json.dumps(product, ensure_ascii=False) + '\n')
        
        print(f"  ✅ {category_name}: {len(products)} 个商品 -> {output_file}")


def process_stealthrank_ragroll(source_dir: Path, output_dir: Path):
    """处理 StealthRank/ragroll/ 目录下的数据"""
    ragroll_dir = source_dir / "ragroll"
    if not ragroll_dir.exists():
        print(f"  ⚠️  StealthRank/ragroll 目录不存在")
        return
    
    output_algorithm_dir = output_dir / "StealthRank"
    output_algorithm_dir.mkdir(parents=True, exist_ok=True)
    
    for jsonl_file in ragroll_dir.glob("*.jsonl"):
        category_name = sanitize_category_name(jsonl_file.stem)  # 例如: blender, coffee_maker
        output_file = output_algorithm_dir / f"{category_name}.jsonl"
        
        products = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    products.append(convert_to_target_format(item, "StealthRank"))
        
        # 限制商品数量
        products = products[:MAX_PRODUCTS_PER_CATEGORY]
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            for product in products:
                f.write(json.dumps(product, ensure_ascii=False) + '\n')
        
        print(f"  ✅ {category_name}: {len(products)} 个商品 -> {output_file}")


def process_adversarialseo(source_dir: Path, output_dir: Path):
    """处理 AdversarialSEO/by-category/ 目录下的数据"""
    category_dir = source_dir / "by-category"
    if not category_dir.exists():
        print(f"  ⚠️  AdversarialSEO/by-category 目录不存在")
        return
    
    output_algorithm_dir = output_dir / "AdversarialSEO"
    output_algorithm_dir.mkdir(parents=True, exist_ok=True)
    
    for json_file in category_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # AdversarialSEO 格式是 { "Category Name": [products] }
        for category_name, products_list in data.items():
            sanitized_category = sanitize_category_name(category_name)
            output_file = output_algorithm_dir / f"{sanitized_category}.jsonl"
            
            converted_products = []
            for item in products_list:
                converted_products.append(convert_to_target_format(item, "AdversarialSEO"))
            
            # 限制商品数量
            converted_products = converted_products[:MAX_PRODUCTS_PER_CATEGORY]
            
            # 写入输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                for product in converted_products:
                    f.write(json.dumps(product, ensure_ascii=False) + '\n')
            
            print(f"  ✅ {sanitized_category}: {len(converted_products)} 个商品 -> {output_file}")


def process_llm_rank_optimizer(source_dir: Path, output_dir: Path):
    """处理 llm-rank-optimizer 目录下的数据"""
    output_algorithm_dir = output_dir / "llm-rank-optimizer"
    output_algorithm_dir.mkdir(parents=True, exist_ok=True)
    
    # 处理 data/ 目录
    data_dir = source_dir / "data"
    if data_dir.exists():
        for jsonl_file in data_dir.glob("*.jsonl"):
            category_name = jsonl_file.stem
            output_file = output_algorithm_dir / f"{category_name}.jsonl"
            
            products = []
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        products.append(convert_to_target_format(item, "llm-rank-optimizer"))
            
            # 限制商品数量
            products = products[:MAX_PRODUCTS_PER_CATEGORY]
            
            # 写入输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                for product in products:
                    f.write(json.dumps(product, ensure_ascii=False) + '\n')
            
            print(f"  ✅ {category_name}: {len(products)} 个商品 -> {output_file}")
    
    # 处理 extend_data/ 目录
    extend_dir = source_dir / "extend_data"
    if extend_dir.exists():
        for jsonl_file in extend_dir.glob("*.jsonl"):
            category_name = jsonl_file.stem
            output_file = output_algorithm_dir / f"{category_name}.jsonl"
            
            products = []
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        products.append(convert_to_target_format(item, "llm-rank-optimizer"))
            
            # 限制商品数量
            products = products[:MAX_PRODUCTS_PER_CATEGORY]
            
            # 写入输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                for product in products:
                    f.write(json.dumps(product, ensure_ascii=False) + '\n')
            
            print(f"  ✅ {category_name}: {len(products)} 个商品 -> {output_file}")


def process_rewritetorank(source_dir: Path, output_dir: Path):
    """处理 RewriteToRank 数据"""
    output_algorithm_dir = output_dir / "RewriteToRank"
    output_algorithm_dir.mkdir(parents=True, exist_ok=True)
    
    # RewriteToRank 数据格式不同，需要特殊处理
    # 数据按 user_query 分组，每个查询可能对应多个商品
    # 为了更好的组织，我们只处理常见的查询类别
    
    for json_file in source_dir.glob("*.json"):
        # 跳过已经处理过的文件
        if json_file.name.endswith("_clean.json"):
            continue
            
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 按 user_query 分组
        query_groups = {}
        for item in data:
            query = item.get("user_query", "unknown")
            if query not in query_groups:
                query_groups[query] = []
            query_groups[query].append(item)
        
        # 只处理有足够商品的查询类别（至少有2个商品），并且只保留前10个最常见的查询
        sorted_queries = sorted(query_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        
        # 为每个查询创建一个类别
        for query, items in sorted_queries:
            if len(items) < 2:  # 跳过只有1个商品的查询
                continue
                
            sanitized_category = sanitize_category_name(query)
            output_file = output_algorithm_dir / f"{sanitized_category}.jsonl"
            
            converted_products = []
            for item in items:
                # RewriteToRank 格式转换为目标格式
                converted_item = {
                    "Name": item.get("title", ""),
                    "Description": item.get("text", ""),
                    "Price": "$0",  # RewriteToRank 数据中没有价格
                    "Rating": 4.0,
                    "Capacity": "",
                    "Ideal For": item.get("brand", "")
                }
                converted_products.append(converted_item)
            
            # 限制商品数量
            converted_products = converted_products[:MAX_PRODUCTS_PER_CATEGORY]
            
            # 写入输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                for product in converted_products:
                    f.write(json.dumps(product, ensure_ascii=False) + '\n')
            
            print(f"  ✅ {sanitized_category}: {len(converted_products)} 个商品 -> {output_file}")


def main():
    """主函数"""
    base_dir = Path(__file__).parent
    datasets_dir = base_dir / "Datasets"
    output_dir = base_dir / OUTPUT_DIR
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("开始清理和转换数据集")
    print("=" * 60)
    print(f"输出目录: {output_dir}")
    print(f"每个类别最大商品数: {MAX_PRODUCTS_PER_CATEGORY}")
    print()
    
    # 处理 StealthRank
    print("📦 处理 StealthRank 数据...")
    stealthrank_dir = datasets_dir / "StealthRank"
    if stealthrank_dir.exists():
        process_stealthrank_json(stealthrank_dir, output_dir)
        process_stealthrank_ragroll(stealthrank_dir, output_dir)
    else:
        print("  ⚠️  StealthRank 目录不存在")
    print()
    
    # 处理 AdversarialSEO
    print("📦 处理 AdversarialSEO 数据...")
    adversarialseo_dir = datasets_dir / "AdversarialSEO"
    if adversarialseo_dir.exists():
        process_adversarialseo(adversarialseo_dir, output_dir)
    else:
        print("  ⚠️  AdversarialSEO 目录不存在")
    print()
    
    # 处理 llm-rank-optimizer
    print("📦 处理 llm-rank-optimizer 数据...")
    llm_rank_dir = datasets_dir / "llm-rank-optimizer"
    if llm_rank_dir.exists():
        process_llm_rank_optimizer(llm_rank_dir, output_dir)
    else:
        print("  ⚠️  llm-rank-optimizer 目录不存在")
    print()
    
    # 处理 RewriteToRank
    print("📦 处理 RewriteToRank 数据...")
    rewritetorank_dir = datasets_dir / "RewriteToRank"
    if rewritetorank_dir.exists():
        process_rewritetorank(rewritetorank_dir, output_dir)
    else:
        print("  ⚠️  RewriteToRank 目录不存在")
    print()
    
    print("=" * 60)
    print("✅ 数据处理完成！")
    print(f"输出目录: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()

