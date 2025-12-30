# 1. ???????ModelScope????Tokenizer???Hugging Face????
from modelscope.models import AutoModelForCausalLM
from modelscope.tokenizers import AutoTokenizer
import torch
import json
import random
import argparse
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import time

from tools import *  # ??????????decode_adv_prompt?target_loss??

sns.set_style("darkgrid")

def rank_products(text, product_names):
    '''
    Rank the products based on their position in the text.

    Args:
        text: The text containing the product recommendations.
        product_names: A list of product names.

    Returns:
        ranks: A dictionary containing the ranks of the products.
    '''
    # Find position of each product in the text
    position_dict = {}
    for name in product_names:
        position = text.find(name)
        if position != -1:
            position_dict[name] = position
        else:
            position_dict[name] = float('inf')

    # Sort products by position
    sorted_products = sorted(position_dict, key=position_dict.get)

    ranks = {}
    for i, prod in enumerate(sorted_products):
        if position_dict[prod] != float('inf'):
            ranks[prod] = i + 1
        else:
            ranks[prod] = len(sorted_products) + 1

    return ranks

def prompt_generator_vicuna(target_product_idx, product_list, user_msg, tokenizer, device, sts_tokens):
    '''Generate prompt for Vicuna (???????)'''
    system_prompt = "A chat between a user and an assistant. The assistant provides a numbered list of " \
                    + "product recommendations ranked based on the user's request.\n\n" \
                    + "USER:\n\nProducts:\n"

    head = system_prompt
    tail = ''

    # Generate the adversarial prompt
    for i, product in enumerate(product_list):
        if i < target_product_idx:
            head += json.dumps(product) + "\n"
        elif i == target_product_idx:
            head += json.dumps(product) + "\n"
            tail += head[-3:]
            head = head[:-3]
        else:
            tail += json.dumps(product) + "\n"

    tail += "\n" + user_msg + "\n\nASSISTANT: "

    head_tokens = tokenizer(head, return_tensors="pt")["input_ids"].to(device)
    sts_tokens = sts_tokens.to(device)
    head_sts = torch.cat((head_tokens, sts_tokens), dim=1)
    sts_idxs = torch.arange(head_sts.shape[1] - sts_tokens.shape[1], head_sts.shape[1], device=device)
    tail_tokens = tokenizer(tail, return_tensors="pt", add_special_tokens=False)["input_ids"].to(device)
    sts_prompt_ids = torch.cat((head_sts, tail_tokens), dim=1)

    return sts_prompt_ids, sts_idxs

def prompt_generator_llama(target_product_idx, product_list, user_msg, tokenizer, device, sts_tokens):
    '''Generate prompt for Llama (???????)'''
    system_prompt = "[INST] <<SYS>>\nA chat between a human and an artificial " \
                    + "intelligence assistant. The assistant provides a numbered list of " \
                    + "product recommendations ranked based on the user's request.\n" \
                    + "<</SYS>>\n\nProducts:\n"

    head = system_prompt
    tail = ''

    # Generate the adversarial prompt
    for i, product in enumerate(product_list):
        if i < target_product_idx:
            head += json.dumps(product) + "\n"
        elif i == target_product_idx:
            head += json.dumps(product) + "\n"
            tail += head[-3:]
            head = head[:-3]
        else:
            tail += json.dumps(product) + "\n"

    tail += "\n" + user_msg + " [/INST]"

    head_tokens = tokenizer(head, return_tensors="pt")["input_ids"].to(device)
    sts_tokens = sts_tokens.to(device)
    head_sts = torch.cat((head_tokens, sts_tokens), dim=1)
    sts_idxs = torch.arange(head_sts.shape[1] - sts_tokens.shape[1], head_sts.shape[1], device=device)
    tail_tokens = tokenizer(tail, return_tensors="pt", add_special_tokens=False)["input_ids"].to(device)
    sts_prompt_ids = torch.cat((head_sts, tail_tokens), dim=1)

    return sts_prompt_ids, sts_idxs

def rank_opt(target_product_idx, product_list, model_list, tokenizer, loss_function, prompt_gen_list,
             forbidden_tokens, save_path, num_iter=1000, top_k=256, num_samples=512, batch_size=200,
             test_iter=50, num_sts_tokens=30, top_candidates=1, verbose=True, random_order=True, save_state=True):
    '''?????????????????'''
    # Create directory to save plots and result
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # Get product names and target product
    product_names = [product['Name'] for product in product_list]
    target_product = product_names[target_product_idx]
    num_prod = len(product_names)

    # Initialize STS tokens and other variables
    state_dict_path = save_path + "/state_dict.pth"
    if save_state and os.path.exists(state_dict_path):        
        state_dict = torch.load(state_dict_path)
        sts_tokens = state_dict["sts_tokens"]
        start_iter = state_dict["iteration"] + 1
        loss_df = state_dict["loss_df"]
        rank_df = state_dict["rank_df"]
        avg_loss = state_dict["avg_loss"]
        avg_iter_time = state_dict["avg_iter_time"]
        top_count = state_dict["top_count"]
        best_top_count = state_dict["best_top_count"]
    else:
        sts_tokens = torch.full((1, num_sts_tokens), tokenizer.encode('*')[1])  # Insert optimizable tokens
        start_iter = 0
        rank_df = pd.DataFrame(columns=["Iteration", "Rank"])
        loss_df = pd.DataFrame(columns=["Iteration", "Current Loss", "Average Loss"])
        avg_loss = 0
        avg_iter_time = 0
        top_count = 0
        best_top_count = 0

    decay = 0.99    # Decay factor for average loss

    input_sequence_list = []
    sts_idxs_list = []

    num_models = len(model_list)

    for i in range(num_models):
        # Generate input prompt
        inp_prompt_ids, sts_idxs = prompt_gen_list[i](target_product_idx, product_list, tokenizer, model_list[i].device, sts_tokens)
        input_sequence_list.append(inp_prompt_ids)
        sts_idxs_list.append(sts_idxs)

    if verbose:
        rand_idx = random.randint(0, num_models - 1)
        model = model_list[rand_idx]
        inp_prompt_ids = input_sequence_list[rand_idx]
        sts_idxs = sts_idxs_list[rand_idx]

        print("\nADV PROMPT:\n" + decode_adv_prompt(inp_prompt_ids[0], sts_idxs, tokenizer), flush=True)
        model_output = model.generate(inp_prompt_ids, model.generation_config, max_new_tokens=800)
        model_output_new = tokenizer.decode(model_output[0, len(inp_prompt_ids[0]):]).strip()
        print("\nLLM RESPONSE:\n" + model_output_new, flush=True)

        product_rank = rank_products(model_output_new, product_names)[target_product]
        if start_iter == 0:
            rank_df.loc[0] = [0, product_rank]
        print(colored(f"\nTarget Product Rank: {product_rank}", "blue"), flush=True)
        print("")
        print("\nIteration, Curr loss, Avg loss, Avg time, Opt sequence")

    for iter in range(start_iter, num_iter):

        # Perform one step of the optimization procedure
        start_time = time.time()
        input_sequence_list, curr_loss = gcg_step_multi(input_sequence_list, sts_idxs_list, model_list,
                                                        loss_function, forbidden_tokens, top_k, num_samples,
                                                        batch_size, top_candidates)
        end_time = time.time()
        iter_time = end_time - start_time
        avg_iter_time = ((iter * avg_iter_time) + iter_time) / (iter + 1)

        # Average loss with decay
        avg_loss = (((1 - decay) * curr_loss) + ((1 - (decay ** iter)) * decay * avg_loss)) / (1 - (decay ** (iter + 1)))
        
        loss_df.loc[iter] = [iter + 1, curr_loss, avg_loss]

        sts_tokens = input_sequence_list[0][0, sts_idxs_list[0]].unsqueeze(0)

        if random_order:
            random.shuffle(product_list)

        # Find target product index in the shuffled list
        target_product_idx = [product['Name'] for product in product_list].index(target_product)

        input_sequence_list = []
        sts_idxs_list = []

        for i in range(num_models):
            # Generate input prompt
            inp_prompt_ids, sts_idxs = prompt_gen_list[i](target_product_idx, product_list, tokenizer, model_list[i].device, sts_tokens)
            input_sequence_list.append(inp_prompt_ids)
            sts_idxs_list.append(sts_idxs)
        
        eval_sequence_list = input_sequence_list
        eval_sts_idxs_list = sts_idxs_list

        if verbose:
            # Print current loss and best loss
            rand_idx = random.randint(0, num_models - 1)
            model = model_list[rand_idx]
            eval_prompt_ids = eval_sequence_list[rand_idx]
            eval_opt_idxs = eval_sts_idxs_list[rand_idx]

            print(str(iter + 1) + "/{}, {:.4f}, {:.4f}, {:.1f}s, {}".format(num_iter, curr_loss, avg_loss, avg_iter_time, colored(tokenizer.decode(eval_prompt_ids[0, eval_opt_idxs]), 'red'))
                                                           + " " * 10, flush=True, end="\r")

            # Evaluate STS every test_iter iterations
            if (iter + 1) % test_iter == 0 or iter == num_iter - 1:
                
                print("\n\nEvaluating STS...")
                print("\nADV PROMPT:\n" + decode_adv_prompt(eval_prompt_ids[0], eval_opt_idxs, tokenizer), flush=True)
                model_output = model.generate(eval_prompt_ids, model.generation_config, max_new_tokens=800)
                model_output_new = tokenizer.decode(model_output[0, len(eval_prompt_ids[0]):]).strip()
                print("\nLLM RESPONSE:\n" + model_output_new, flush=True)

                product_rank = rank_products(model_output_new, product_names)[target_product]
                rank_df.loc[len(rank_df)] = [iter + 1, product_rank]
                print(colored(f"\nTarget Product Rank: {product_rank}", "blue"), flush=True)
                rank_df.to_csv(save_path + "/rank.csv", index=False)

                # Update top count
                if product_rank <= 3:
                    top_count += 1
                else:
                    top_count = 0

                # Save product line with optimized sequence
                if top_count >= best_top_count:
                    best_top_count = top_count
                    eval_prompt_str = tokenizer.decode(eval_prompt_ids[0])
                    eval_prompt_lines = eval_prompt_str.split("\n")
                    for _, line in enumerate(eval_prompt_lines):
                        if target_product in line:
                            with open(save_path + "/sts.txt", "w") as file:
                                file.write(line + "\n")
                            break

                print(f'\nTop count: {top_count}, Best top count: {best_top_count}', flush=True)

                # Plot iteration vs. top as dots
                plt.figure(figsize=(7, 4))
                sns.scatterplot(data=rank_df, x="Iteration", y="Rank", s=80)
                plt.fill_between([-(0.015*num_iter), num_iter + (0.015*num_iter)], (num_prod+1) * 1.04, num_prod + 0.5, color="grey", alpha=0.3, zorder=0)
                plt.xlabel("Iteration", fontsize=16)
                plt.ylabel("Rank", fontsize=16)
                plt.ylim((num_prod+1) * 1.04, 1 - ((num_prod+1) * 0.04))
                plt.yticks(range(num_prod, 0, -1), fontsize=14)
                plt.title("Target Product Rank", fontsize=18)
                plt.xlim(-(0.015*num_iter), num_iter + (0.015*num_iter))
                plt.xticks(range(0, num_iter + 1, num_iter//5), fontsize=14)
                grey_patch = mpatches.Patch(color='grey', alpha=0.3, label='Not Recommended')
                plt.legend(handles=[grey_patch])
                plt.tight_layout()
                plt.savefig(save_path + "/rank.png")
                plt.close()

                # Plot iteration vs. current loss and average loss
                plt.figure(figsize=(7, 4))
                sns.lineplot(data=loss_df, x="Iteration", y="Current Loss", label="Current Loss")
                sns.lineplot(data=loss_df, x="Iteration", y="Average Loss", label="Average Loss", linewidth=2)
                plt.xlabel("Iteration", fontsize=16)
                plt.xticks(fontsize=14)
                plt.ylabel("Loss", fontsize=16)
                plt.yticks(fontsize=14)
                plt.title("Current and Average Loss", fontsize=18)
                plt.tight_layout()
                plt.savefig(save_path + "/loss.png")
                plt.close()

                if iter < num_iter - 1:                    
                    print("")
                    print("Iteration, Curr loss, Avg loss, Opt sequence", flush=True)

        if save_state:
            # Save the STS and iteration number in a pytorch state dictionary
            state_dict = {
                "iteration": iter,
                "sts_tokens": sts_tokens,
                "loss_df": loss_df,
                "rank_df": rank_df,
                "avg_loss": avg_loss,
                "avg_iter_time": avg_iter_time,
                "top_count": top_count,
                "best_top_count": best_top_count
            }
            torch.save(state_dict, state_dict_path)

    print("")


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Product Rank Optimization (ModelScope Version)")
    argparser.add_argument("--results_dir", type=str, default="results/test", help="The directory to save the results.")
    argparser.add_argument("--catalog", type=str, default="coffee_machines", choices=["election_articles","coffee_machines", "books", "cameras"], help="The product catalog to use.")
    argparser.add_argument("--num_iter", type=int, default=500, help="The number of iterations.")
    argparser.add_argument("--test_iter", type=int, default=20, help="The number of test iterations.")
    argparser.add_argument("--random_order", action="store_true", help="Whether to shuffle the product list in each iteration.")
    argparser.add_argument("--target_product_idx", type=int, default=0, help="The index of the target product in the product list.")
    argparser.add_argument("--mode", type=str, default="self", choices=["self", "transfer"], help="Mode of optimization.")
    argparser.add_argument("--target_llm", type=str, default="llama", choices=["llama", "vicuna"],
                           help="Target language model to generate STS for in self mode.")
    argparser.add_argument("--top_candidates", type=int, default=1, help="Number of top candidates to consider for multi-coordinate updates.")
    argparser.add_argument("--user_msg_type", type=str, default="default", choices=["default", "custom"], help="User message type.")
    argparser.add_argument("--save_state", action="store_true", help="Whether to save the state of the optimization procedure.")
    args = argparser.parse_args()

    # 2. ?????ModelScope????????Hugging Face???
    # ??????ModelScope?????????????Llama??????
    model_path_llama_7b = "modelscope/Llama-2-7b-chat-ms"  # ModelScope Llama-