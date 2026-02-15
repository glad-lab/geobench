#!/usr/bin/env python3
"""
遍历 datasets_clean 数据集，为每个类别文件的第一个商品运行 rank_opt
每个数据集只选取前 20 个 category（不足 20 个则全部遍历）
每个商品只运行一次（run=1）
"""

import os
import json
import subprocess
import sys
from pathlib import Path
import time

# 配置参数
BASE_DIR = Path("/home/exouser/vscode/geobench")
DATASETS_CLEAN_DIR = BASE_DIR / "datasets_clean"
RESULTS_BASE_DIR = BASE_DIR / "Results_new"
MAX_CATEGORIES_PER_DATASET = 20  # 每个数据集最多处理 20 个 category

# rank_opt 参数
MODE = "self"
USER_MSG_TYPE = "default"
TARGET_LLM = "llama"
NUM_ITER = 2000
TEST_ITER = 50
RUN = 1  # 固定为1
PYTHON_PATH = "conda run -n geo python"

# 显存优化环境变量
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,max_split_size_mb:64,garbage_collection_threshold:0.6"
os.environ["TRANSFORMERS_CACHE"] = "/tmp"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def get_product_count(category_file):
    """获取类别文件中的商品数量"""
    with open(category_file, 'r', encoding='utf-8') as f:
        return len([l for l in f if l.strip()])


def check_if_done(results_dir):
    """检查任务是否已完成"""
    done_file = results_dir / "done.txt"
    if done_file.exists():
        with open(done_file, 'r') as f:
            return "done" in f.read().strip()
    return False


def mark_done(results_dir):
    """标记任务完成"""
    results_dir.mkdir(parents=True, exist_ok=True)
    done_file = results_dir / "done.txt"
    with open(done_file, 'w') as f:
        f.write("done\n")


def run_rank_opt(category_file, algorithm_name, category_name, product_idx, user_msg):
    """运行 rank_opt.py"""
    # 构建结果目录
    results_dir = RESULTS_BASE_DIR / algorithm_name / category_name / MODE / TARGET_LLM / USER_MSG_TYPE / f"product{product_idx}" / f"run{RUN}"
    log_file = results_dir / "rank_opt_background.log"
    
    # 检查是否已完成
    if check_if_done(results_dir):
        return True, "已跳过（已完成）"
    
    # 创建结果目录
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 将文件复制到 data 目录（使用 category_name 作为文件名）
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    data_catalog_path = data_dir / f"{category_name}.jsonl"
    
    # 复制文件（如果不存在或不同）
    if not data_catalog_path.exists():
        import shutil
        shutil.copy2(category_file, data_catalog_path)
    
    # 构建命令
    # 注意：由于 rank_opt.py 的 catalog 参数限制，我们需要使用 category_name
    # 但如果 category_name 不在支持列表中，需要修改 rank_opt.py 或使用其他方法
    # PYTHON_PATH 可能包含多个部分（如 "conda run -n geo python"），需要拆分
    python_cmd = PYTHON_PATH.split()
    cmd = python_cmd + [
        str(BASE_DIR / "rank_opt.py"),
        "--results_dir", str(results_dir),
        "--catalog", category_name,  # 这里使用 category_name，需要在 rank_opt.py 中支持
        "--user_msg_type", USER_MSG_TYPE,
        "--target_product_idx", str(product_idx),
        "--num_iter", str(NUM_ITER),
        "--test_iter", str(TEST_ITER),
        "--random_order",
        "--save_state",
        "--mode", MODE,
        "--target_llm", TARGET_LLM,
    ]
    
    # 运行命令
    try:
        with open(log_file, 'w') as log_f:
            result = subprocess.run(cmd, cwd=str(BASE_DIR), stdout=log_f, stderr=subprocess.STDOUT, check=True)
        
        # 标记完成
        mark_done(results_dir)
        return True, "成功"
    except subprocess.CalledProcessError as e:
        return False, f"失败: {e}"


def main():
    """主函数"""
    print("=" * 60)
    print("开始遍历 datasets_clean 数据集")
    print("=" * 60)
    print(f"数据集目录: {DATASETS_CLEAN_DIR}")
    print(f"结果保存目录: {RESULTS_BASE_DIR}")
    print(f"每个数据集最多处理 {MAX_CATEGORIES_PER_DATASET} 个 category")
    print(f"每个 category 只处理第一个商品 (product1)")
    print()
    
    total_tasks = 0
    completed_tasks = 0
    skipped_tasks = 0
    failed_tasks = 0
    
    # 遍历每个数据集文件夹
    for dataset_dir in sorted(DATASETS_CLEAN_DIR.iterdir()):
        if not dataset_dir.is_dir():
            continue
        
        dataset_name = dataset_dir.name
        print(f"📦 处理数据集: {dataset_name}")
        
        # 获取所有类别文件并排序
        category_files = sorted(dataset_dir.glob("*.jsonl"))
        total_categories = len(category_files)
        
        # 选择前 MAX_CATEGORIES_PER_DATASET 个 category（如果不足则全部）
        selected_categories = category_files[:MAX_CATEGORIES_PER_DATASET]
        
        print(f"  总类别数: {total_categories}")
        print(f"  将处理: {len(selected_categories)} 个类别")
        if total_categories > MAX_CATEGORIES_PER_DATASET:
            print(f"  ⚠️  超过 {MAX_CATEGORIES_PER_DATASET} 个，只处理前 {MAX_CATEGORIES_PER_DATASET} 个")
        
        # 遍历选中的类别文件
        for category_file in selected_categories:
            category_name = category_file.stem
            print(f"  📁 处理类别: {category_name}")
            
            # 获取商品数量
            product_count = get_product_count(category_file)
            print(f"     商品数量: {product_count}")
            
            if product_count == 0:
                print(f"     ⚠️  跳过（无商品）")
                continue
            
            # 读取用户消息（从文件的第一行推断，或者使用通用消息）
            # 这里使用通用的用户消息
            user_msg = "I am looking for a product. Can I get some recommendations?"
            
            # 只处理第一个商品作为 target product
            product_idx = 1
            total_tasks += 1
            print(f"      ▶️  product{product_idx}...", end=" ", flush=True)
            
            success, message = run_rank_opt(
                category_file, 
                dataset_name, 
                category_name, 
                product_idx, 
                user_msg
            )
            
            if message == "已跳过（已完成）":
                skipped_tasks += 1
                print(f"⏭️  跳过")
            elif success:
                completed_tasks += 1
                print(f"✅ 完成")
            else:
                failed_tasks += 1
                print(f"❌ {message}")
            
            print()
        
        print()
    
    print("=" * 60)
    print("遍历完成！")
    print(f"总任务数: {total_tasks}")
    print(f"完成任务数: {completed_tasks}")
    print(f"跳过任务数: {skipped_tasks}")
    print(f"失败任务数: {failed_tasks}")
    print(f"结果目录: {RESULTS_BASE_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()

