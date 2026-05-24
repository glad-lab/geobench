import boto3
import json
import random
import argparse
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import time
from typing import List, Dict, Tuple
from botocore.exceptions import ClientError
from transformers import AutoTokenizer  # 导入tokenizer（用于处理文本和禁止Token）

# 导入修复后的tools2.py
from tools2 import (
    get_nonascii_toks, rank_products, target_loss, decode_adv_prompt,
    sts_optimize_step_api, _generate_api_prompt
)

sns.set_style("darkgrid")


# 初始化Bedrock客户端
def init_bedrock_client(region_name: str = "us-east-1") -> boto3.client:
    try:
        client = boto3.client("bedrock-runtime", region_name=region_name)
        print(f"成功连接Bedrock（区域：{region_name}）")
        return client
    except ClientError as e:
        print(f"Bedrock初始化失败: {str(e)}")
        raise


# Bedrock API调用函数（适配Llama 3格式）
def bedrock_generate(client: boto3.client, prompt: str, model_id: str = "meta.llama3-70b-instruct-v1:0",
                     max_gen_len: int = 800, temperature: float = 0.7) -> str:
    try:
        formatted_prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
{prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
        native_request = {
            "prompt": formatted_prompt,
            "max_gen_len": max_gen_len,
            "temperature": temperature,
            "top_p": 0.9
        }
        response = client.invoke_model(modelId=model_id, body=json.dumps(native_request))
        # print(response)
        model_response = json.loads(response["body"].read())
        print(model_response["generation"].strip())
        print("调用成功")
        return model_response["generation"].strip()
    except Exception as e:
        print(f"Bedrock调用失败: {str(e)}")
        # print("调用失败")

        return ""


def rank_opt_bedrock(target_product_idx: int, product_list: List[Dict], client: boto3.client, model_id: str,
                     tokenizer, forbidden_tokens: List[str], save_path: str, num_iter: int = 1000, top_k: int = 50,
                     test_iter: int = 50, num_sts_chars: int = 30, verbose: bool = True,
                     random_order: bool = True, save_state: bool = True) -> None:
    # 初始化目录和基础信息
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    product_names = [p["Name"] for p in product_list]
    target_product = product_names[target_product_idx]
    num_prod = len(product_names)
    state_dict_path = os.path.join(save_path, "state_dict_bedrock.pth")

    # 加载历史状态
    if save_state and os.path.exists(state_dict_path):
        state_dict = torch.load(state_dict_path)
        sts_text = state_dict["sts_text"]
        start_iter = state_dict["iteration"] + 1
        loss_df = state_dict["loss_df"]
        rank_df = state_dict["rank_df"]
        avg_iter_time = state_dict["avg_iter_time"]
        top_count = state_dict["top_count"]
        best_top_count = state_dict["best_top_count"]
    else:
        # 初始化STS（使用有效字符，排除禁止Token）
        valid_chars = [c for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.,! " 
                      if c not in forbidden_tokens]
        sts_text = "".join(random.choice(valid_chars) for _ in range(num_sts_chars))
        start_iter = 0
        rank_df = pd.DataFrame(columns=["Iteration", "Rank"])
        loss_df = pd.DataFrame(columns=["Iteration", "Rank_Loss"])
        avg_iter_time = 0
        top_count = 0
        best_top_count = 0

    # 初始评估
    if verbose and start_iter == 0:
        initial_prompt = _generate_api_prompt(target_product_idx, product_list, user_msg, sts_text, tokenizer)
        initial_output = bedrock_generate(client, initial_prompt, model_id)
        initial_rank = rank_products(initial_output, product_names)[target_product]
        rank_df.loc[0] = [0, initial_rank]
        print(f"初始状态 - 目标产品: {target_product}, 排名: {initial_rank}")
        print(f"初始STS: {sts_text}")
        print("\n迭代进度: 迭代次数, 当前排名, 平均耗时, 最优STS")

    # 优化主循环
    for iter in range(start_iter, num_iter):
        start_time = time.time()

        # 打乱产品列表（增强鲁棒性）
        if random_order:
            random.shuffle(product_list)
            target_product_idx = product_names.index(target_product)

        # 【关键修复】使用API专用优化函数（替代GCG）
        sts_text, current_rank = sts_optimize_step_api(
            sts_text=sts_text,
            target_product=target_product,
            product_list=product_list,
            user_msg=user_msg,
            product_names=product_names,
            forbidden_tokens=forbidden_tokens,
            tokenizer=tokenizer,
            api_generate_func=bedrock_generate,  # 传入API调用函数
            api_model=model_id,
            client=client,  # 新增：传入Bedrock客户端实例
            top_k=top_k
        )


        # 记录数据
        rank_percent = (current_rank - 1) / (num_prod - 1)  # num_prod是产品总数
        loss_df.loc[iter] = [iter + 1, rank_percent]
        iter_time = time.time() - start_time
        avg_iter_time = ((iter * avg_iter_time) + iter_time) / (iter + 1)

        # 更新Top3计数
        if current_rank <= 3:
            top_count += 1
            best_top_count = max(best_top_count, top_count)
        else:
            top_count = 0

        # 打印进度
        if verbose:
            print(f"{iter+1}/{num_iter}, {current_rank}, {avg_iter_time:.1f}s, {sts_text[:20]}...", 
                  flush=True, end="\r")

        # 定期评估与保存
        if (iter + 1) % test_iter == 0 or iter == num_iter - 1:
            # 新增：配置 Matplotlib 支持中文的字体
            plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']  # 优先使用系统已安装的中文字体
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示异常的问题
            test_idx = product_names.index(target_product)
            test_prompt = _generate_api_prompt(test_idx, product_list, user_msg, sts_text, tokenizer)
            test_output = bedrock_generate(client, test_prompt, model_id)
            test_rank = rank_products(test_output, product_names)[target_product]
            rank_df.loc[len(rank_df)] = [iter + 1, test_rank]

            # 保存结果
            with open(os.path.join(save_path, "sts_bedrock.txt"), "w", encoding="utf-8") as f:
                f.write(f"迭代次数: {iter+1}\n目标产品: {target_product}\n排名: {test_rank}\nSTS: {sts_text}")
            rank_df.to_csv(os.path.join(save_path, "rank_bedrock.csv"), index=False)
            loss_df.to_csv(os.path.join(save_path, "loss_bedrock.csv"), index=False)

            # 生成可视化图表
            # 排名变化图
            plt.figure(figsize=(7, 4))
            sns.scatterplot(data=rank_df, x="Iteration", y="Rank", s=80, color="#1f77b4")
            plt.fill_between([-(0.015*num_iter), num_iter + (0.015*num_iter)], 
                             (num_prod+1)*1.04, num_prod+0.5, color="grey", alpha=0.3, zorder=0)
            plt.xlabel("Iteration", fontsize=14)
            plt.ylabel("Target Product Rank", fontsize=14)
            plt.ylim((num_prod+1)*1.04, 1 - ((num_prod+1)*0.04))
            plt.yticks(range(num_prod, 0, -1), fontsize=12)
            plt.title(f"Target Product ({target_product}) Rank", fontsize=16)
            plt.xlim(-(0.015*num_iter), num_iter + (0.015*num_iter))
            plt.xticks(range(0, num_iter+1, num_iter//5), fontsize=12)
            plt.legend(handles=[mpatches.Patch(color='grey', alpha=0.3, label='Not Recommended')])
            plt.tight_layout()
            plt.savefig(os.path.join(save_path, "rank_bedrock.png"), dpi=300)
            plt.close()

            # 损失变化图
            plt.figure(figsize=(7, 4))
            sns.lineplot(data=loss_df, x="Iteration", y="Rank_Loss", linewidth=2, color="#ff7f0e")
            plt.xlabel("Iteration", fontsize=14)
            plt.ylabel("Rank Loss (Smaller = Better)", fontsize=14)
            plt.title("Rank Loss Over Iterations", fontsize=16)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            plt.tight_layout()
            plt.savefig(os.path.join(save_path, "loss_bedrock.png"), dpi=300)
            plt.close()

            # 打印评估信息
            print(f"\n\n迭代 {iter+1} 评估:")
            print(f"Prompt预览: {test_prompt[:500]}...")
            print(f"模型输出预览: {test_output[:500]}...")
            print(f"目标产品排名: {test_rank}")
            print(f"连续Top3次数: {top_count}, 最佳: {best_top_count}\n")

        # 保存状态（中断后可恢复）
        if save_state:
            state_dict = {
                "iteration": iter,
                "sts_text": sts_text,
                "loss_df": loss_df,
                "rank_df": rank_df,
                "avg_iter_time": avg_iter_time,
                "top_count": top_count,
                "best_top_count": best_top_count
            }
            # torch.save(state_dict, state_dict_path)

    print("\n优化完成！结果保存至:", save_path)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Product Rank Optimization (Bedrock API)")
    argparser.add_argument("--results_dir", type=str, default="results/test_bedrock", help="结果目录")
    argparser.add_argument("--catalog", type=str, default="咖啡机_tiny", 
                           choices=["election_articles", "coffee_machines", "books", "cameras", "咖啡机_tiny"], 
                           help="产品目录")
    argparser.add_argument("--num_iter", type=int, default=10, help="迭代次数")
    argparser.add_argument("--test_iter", type=int, default=1, help="评估间隔")
    argparser.add_argument("--random_order", action="store_true", help="打乱产品列表")
    argparser.add_argument("--target_product_idx", type=int, default=0, help="目标产品索引（0=随机）")
    argparser.add_argument("--model_id", type=str, default="meta.llama3-70b-instruct-v1:0", help="Bedrock模型ID")
    argparser.add_argument("--region", type=str, default="us-east-1", help="AWS区域")
    argparser.add_argument("--top_k", type=int, default=20, help="候选Token数量")
    argparser.add_argument("--num_sts_chars", type=int, default=30, help="STS字符长度")
    argparser.add_argument("--user_msg_type", type=str, default="default", choices=["default", "custom"], help="用户消息类型")
    argparser.add_argument("--save_state", action="store_true", help="保存状态")
    args = argparser.parse_args()

    # 1. 初始化Bedrock客户端和Tokenizer（【关键修复】传入有效Tokenizer）
    client = init_bedrock_client(region_name=args.region)
    # 使用与模型匹配的Tokenizer（Llama 3可直接使用LlamaTokenizer）
    tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
  # 与Bedrock Llama 3兼容
    tokenizer.pad_token = tokenizer.eos_token  # 避免pad_token为None

    # 2. 加载产品和用户消息
    catalog_path = f"data/{args.catalog}.jsonl"
    if args.catalog == "coffee_machines":
        user_msg = "I am looking for a coffee machine. Can I get recommendations?" if args.user_msg_type == "default" else "I need an affordable coffee machine."
    elif args.catalog == "咖啡机_tiny":
        user_msg = "I am looking for a coffee machine. Can I get recommendations?" if args.user_msg_type == "default" else "I need an affordable coffee machine."
    elif args.catalog == "books":
        user_msg = "Recommend a book in any genre." if args.user_msg_type == "default" else "Recommend an adventure novel."
    elif args.catalog == "cameras":
        user_msg = "Recommend a camera." if args.user_msg_type == "default" else "Recommend a high-resolution camera."
    elif args.catalog == "election_articles":
        user_msg = "Recommend an election article."
    else:
        raise ValueError("无效目录")

    product_list = []
    with open(catalog_path, "r", encoding="utf-8") as f:
        for line in f:
            product_list.append(json.loads(line.strip()))

    # 确定目标产品索引
    if args.target_product_idx <= 0:
        target_product_idx = random.randint(0, len(product_list)-1)
    else:
        target_product_idx = args.target_product_idx - 1  # 转为0-based
    target_product = product_list[target_product_idx]["Name"]

    # 3. 生成禁止Token（【关键修复】传入有效Tokenizer）
    forbidden_tokens_torch = get_nonascii_toks(tokenizer, device="cpu")  # 本地计算禁止Token
    forbidden_chars = []
    for tok_id in forbidden_tokens_torch:
        char = tokenizer.decode([tok_id]).strip()
        if char:  # 过滤空字符
            forbidden_chars.append(char)
    # 额外添加易导致API解析错误的符号
    forbidden_chars.extend(["\\", "/", "*", "(", ")", "[", "]", "{", "}", "|", "~", "`"])

    # 4. 保存配置并启动优化
    exp_config = {
        "Bedrock Model": args.model_id,
        "AWS Region": args.region,
        "Target Product": target_product,
        "Iterations": args.num_iter,
        "Results Dir": args.results_dir
    }
    os.makedirs(args.results_dir, exist_ok=True)
    with open(os.path.join(args.results_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(exp_config, f, indent=4)

    # 打印配置
    print("="*50)
    for k, v in exp_config.items():
        print(f"{k}: {v}")
    print("="*50)

    # 启动优化
    rank_opt_bedrock(
        target_product_idx=target_product_idx,
        product_list=product_list,
        client=client,
        model_id=args.model_id,
        tokenizer=tokenizer,
        forbidden_tokens=forbidden_chars,
        save_path=args.results_dir,
        num_iter=args.num_iter,
        top_k=args.top_k,
        test_iter=args.test_iter,
        num_sts_chars=args.num_sts_chars,
        verbose=True,
        random_order=args.random_order,
        save_state=args.save_state
    )