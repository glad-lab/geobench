import torch
from numpy.random import randint
from math import ceil
from termcolor import colored
import concurrent.futures
import json
import random  # 新增：用于STS优化中的随机选择
import boto3

def get_nonascii_toks(tokenizer, device='cpu'):
    """
    【修复】必须传入有效的tokenizer，删除原代码中传入None的调用
    Returns the non-ascii tokens in the tokenizer's vocabulary.
    """
    def is_ascii(s):
        return s.isascii() and s.isprintable()

    ascii_toks = []
    # 确保tokenizer有效
    if tokenizer is None:
        raise ValueError("get_nonascii_toks() requires a valid tokenizer, got None")
    
    for i in range(3, tokenizer.vocab_size):
        if not is_ascii(tokenizer.decode([i])):
            ascii_toks.append(i)
    
    # 添加特殊Token到禁止列表
    special_tokens = [tokenizer.bos_token_id, tokenizer.eos_token_id, 
                      tokenizer.pad_token_id, tokenizer.unk_token_id]
    for tok in special_tokens:
        if tok is not None and tok not in ascii_toks:
            ascii_toks.append(tok)
    
    return torch.tensor(ascii_toks, device=device)


def target_loss(embeddings, model, tokenizer, target_sequence):
    """
    【仅用于本地模型】计算目标序列的损失（依赖模型内部嵌入层）
    注：API调用模式下不使用此函数
    """
    device = model.device

    # Tokenize目标序列并获取嵌入
    target_tokens = tokenizer(target_sequence, return_tensors="pt", add_special_tokens=False)["input_ids"].to(device)
    word_embedding_layer = model.get_input_embeddings()
    target_embeddings = word_embedding_layer(target_tokens)

    # 拼接嵌入向量
    target_embeddings = target_embeddings.expand(embeddings.shape[0], -1, -1)
    sequence_embeddings = torch.cat((embeddings, target_embeddings), dim=1)

    # 计算损失
    sequence_logits = model(inputs_embeds=sequence_embeddings).logits
    loss_fn = torch.nn.CrossEntropyLoss()
    loss = []
    for i in range(embeddings.shape[0]):
        loss.append(loss_fn(sequence_logits[i, embeddings.shape[1]-1:-1, :], target_tokens[0]))
    return torch.stack(loss)


def decode_adv_prompt(adv_prompt_ids, adv_idxs, tokenizer):
    """
    【通用】解码对抗性Prompt，高亮显示STS部分（本地模型和API模式均可用）
    """
    adv_prompt_str = ""
    colored_str = ""
    for i in range(len(adv_prompt_ids)):
        temp = tokenizer.decode(adv_prompt_ids[:i+1])
        if i in adv_idxs:
            colored_str += colored(temp[len(adv_prompt_str):], "red")
        else:
            colored_str += temp[len(adv_prompt_str):]
        adv_prompt_str = temp
    return colored_str


# 新增：根据模型输出文本计算产品排名
def rank_products(text: str, product_names: list) -> dict:
    """
    【通用】根据产品在文本中出现的位置计算排名
    位置越靠前，排名越优（数值越小）
    未出现的产品排名为总产品数+1
    
    Args:
        text: 模型生成的推荐文本
        product_names: 所有产品名称列表
        
    Returns:
        ranks: 产品-排名字典（键为产品名称，值为排名）
    """
    # 记录每个产品首次出现的位置
    positions = {}
    for name in product_names:
        # 查找产品名在文本中首次出现的索引
        pos = text.find(name)
        # 未找到则标记为无穷大（排名最后）
        positions[name] = pos if pos != -1 else float('inf')
    
    # 按出现位置排序（升序），位置越小排名越靠前
    sorted_products = sorted(positions.keys(), key=lambda x: positions[x])
    
    # 生成排名字典
    ranks = {}
    for idx, product in enumerate(sorted_products):
        if positions[product] != float('inf'):
            ranks[product] = idx + 1  # 排名从1开始
        else:
            ranks[product] = len(product_names) + 1  # 未出现的产品排名为总数量+1
    
    return ranks


# ------------------------------
# 以下GCG相关函数【仅用于本地模型】
# API调用模式下需使用启发式优化替代
# ------------------------------
def gcg_step(input_sequence, adv_idxs, model, loss_function, forbidden_tokens, top_k, num_samples, batch_size):
    """仅用于本地模型的GCG优化步骤"""
    num_adv = len(adv_idxs)
    word_embedding_layer = model.get_input_embeddings()
    embedding_matrix = word_embedding_layer.weight.data

    input_embeddings = word_embedding_layer(input_sequence)
    input_embeddings.requires_grad = True

    # 计算损失和梯度（依赖本地模型）
    loss = loss_function(input_embeddings, model)[0]
    (-loss).backward()
    gradients = input_embeddings.grad

    dot_prod = torch.matmul(gradients[0], embedding_matrix.T)
    dot_prod[:, forbidden_tokens] = float("-inf")
    top_k_adv = (torch.topk(dot_prod, top_k).indices)[adv_idxs]

    adv_seq = None
    min_loss = float("inf")

    # 批量生成候选序列
    for i in range(ceil(num_samples / batch_size)):
        this_batch_size = min(batch_size, num_samples - i * batch_size)
        sequence_batch = []
        for _ in range(this_batch_size):
            batch_item = input_sequence.clone().detach()
            rand_adv_idx = randint(0, num_adv)
            random_token_idx = randint(0, top_k)
            batch_item[0, adv_idxs[rand_adv_idx]] = top_k_adv[rand_adv_idx, random_token_idx]
            sequence_batch.append(batch_item)
        sequence_batch = torch.cat(sequence_batch, dim=0)

        batch_loss = loss_function(word_embedding_layer(sequence_batch), model)
        min_batch_loss, min_loss_index = torch.min(batch_loss, dim=0)
        if min_batch_loss.item() < min_loss:
            min_loss = min_batch_loss.item()
            adv_seq = sequence_batch[min_loss_index].unsqueeze(0)
    return adv_seq, min_loss


def gcg_step_multi(input_sequence_list, adv_idxs_list, model_list, loss_function, forbidden_tokens, top_k, num_samples, batch_size, top_candidates):
    """仅用于多本地模型的GCG优化步骤"""
    assert top_candidates <= batch_size, "top_candidates must be ≤ batch_size"
    num_adv = len(adv_idxs_list[0])
    word_embedding_layer_list = [model.get_input_embeddings() for model in model_list]
    embedding_matrix_list = [layer.weight.data for layer in word_embedding_layer_list]
    num_models = len(model_list)
    base_device = model_list[0].device

    # 多模型并行计算梯度（依赖本地模型）
    def compute_dot_prod(i):
        input_embeddings = word_embedding_layer_list[i](input_sequence_list[i])
        input_embeddings.requires_grad = True
        loss = loss_function(input_embeddings, model_list[i])[0]
        (-loss).backward()
        gradients = input_embeddings.grad
        return torch.matmul(gradients[0], embedding_matrix_list[i].T)[adv_idxs_list[i]].to(base_device)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        dot_prod_list = list(executor.map(compute_dot_prod, range(num_models)))
    
    dot_prod_sum = torch.stack(dot_prod_list).sum(dim=0)
    dot_prod_sum[:, forbidden_tokens] = float("-inf")
    top_k_adv = torch.topk(dot_prod_sum, top_k).indices

    # 生成候选序列并筛选最优
    top_candidate_list = [[] for _ in range(num_models)]
    min_loss_list = []
    for i in range(ceil(num_samples / batch_size)):
        this_batch_size = min(batch_size, num_samples - i * batch_size)
        this_batch_top_candidates = min(top_candidates, this_batch_size)
        batch_loss = torch.zeros(this_batch_size).to(base_device)
        sequence_batch_list = [[] for _ in range(num_models)]

        # 生成批量候选
        for _ in range(this_batch_size):
            batch_item_list = [seq.clone().detach() for seq in input_sequence_list]
            rand_adv_idx = randint(0, num_adv)
            random_token_idx = randint(0, top_k)
            for j in range(num_models):
                batch_item_list[j][0, adv_idxs_list[j][rand_adv_idx]] = top_k_adv[rand_adv_idx, random_token_idx]
                sequence_batch_list[j].append(batch_item_list[j])
        sequence_batch_list = [torch.cat(seq_batch, dim=0) for seq_batch in sequence_batch_list]

        # 多模型并行计算损失
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(loss_function, word_embedding_layer_list[j](sequence_batch_list[j]), model_list[j]) for j in range(num_models)]
            for future in futures:
                batch_loss += future.result().to(base_device)

        # 筛选Top候选
        min_batch_loss, min_loss_indices = torch.topk(batch_loss, this_batch_top_candidates, largest=False)
        this_batch_top_cand_idx = 0
        for top_cand_idx in range(top_candidates):
            if this_batch_top_cand_idx < this_batch_top_candidates:
                if top_cand_idx >= len(min_loss_list) or min_batch_loss[this_batch_top_cand_idx] < min_loss_list[top_cand_idx]:
                    for j in range(num_models):
                        top_candidate_list[j].insert(top_cand_idx, sequence_batch_list[j][min_loss_indices[this_batch_top_cand_idx]].unsqueeze(0))
                    min_loss_list.insert(top_cand_idx, min_batch_loss[this_batch_top_cand_idx].item())
                    this_batch_top_cand_idx += 1

    # 多坐标更新与最优筛选
    top_candidate_list = [cand[:top_candidates] for cand in top_candidate_list]
    min_loss_list = min_loss_list[:top_candidates]
    for model_idx in range(num_models):
        for top_cand_idx in range(1, top_candidates):
            for token_idx in range(num_adv):
                base_tok = input_sequence_list[model_idx][0, adv_idxs_list[model_idx][token_idx]]
                if top_candidate_list[model_idx][top_cand_idx][0, adv_idxs_list[model_idx][token_idx]] == base_tok:
                    top_candidate_list[model_idx][top_cand_idx][0, adv_idxs_list[model_idx][token_idx]] = top_candidate_list[model_idx][top_cand_idx-1][0, adv_idxs_list[model_idx][token_idx]]

    top_candidate_list = [torch.cat(cand, dim=0) for cand in top_candidate_list]
    top_candidate_loss = torch.zeros(top_candidates).to(base_device)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(loss_function, word_embedding_layer_list[j](top_candidate_list[j]), model_list[j]) for j in range(num_models)]
        for future in futures:
            top_candidate_loss += future.result().to(base_device)

    min_loss, min_loss_index = torch.min(top_candidate_loss, dim=0)
    adv_seq_list = [top_candidate_list[j][min_loss_index].unsqueeze(0) for j in range(num_models)]
    return adv_seq_list, min_loss.item()


# ------------------------------
# 以下为【API模式专用】启发式优化函数
# 替代本地模型的GCG逻辑
# ------------------------------
def sts_optimize_step_api(
    sts_text: str,
    target_product: str,
    product_list: list,
    user_msg: str,
    product_names: list,
    forbidden_tokens: list,
    tokenizer,
    api_generate_func,  # 即bedrock_generate
    api_model: str,
    client: boto3.client,  # 新增：传入Bedrock客户端
    top_k: int = 50
) -> tuple:
    """
    API模式下的STS启发式优化步骤
    新增client参数，用于传递Bedrock客户端实例
    """
    # 找到目标产品在列表中的索引
    target_idx = next(i for i, p in enumerate(product_list) if p["Name"] == target_product)
    
    # 生成带STS的Prompt并调用API（正确传递3个参数）
    def get_rank(sts: str) -> int:
        prompt = _generate_api_prompt(target_idx, product_list, user_msg, sts, tokenizer)
        # 正确调用：传入client、prompt、api_model
        api_output = api_generate_func(client, prompt, api_model)
        if not api_output.strip():
            return len(product_names) + 1  # 调用失败时排名记为最后
        return rank_products(api_output, product_names)[target_product]

    
    # 评估当前STS效果
    current_rank = get_rank(sts_text)
    best_sts = sts_text
    best_rank = current_rank

    # 生成候选STS（随机替换字符，排除禁止Token）
    sts_chars = list(sts_text)
    valid_chars = [c for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.,! " 
                  if c not in forbidden_tokens]
    
    for _ in range(top_k):
        # 随机替换一个字符
        idx = randint(0, len(sts_chars)-1)
        new_char = random.choice(valid_chars)
        new_sts = "".join([sts_chars[i] if i != idx else new_char for i in range(len(sts_chars))])
        
        # 测试新STS
        new_rank = get_rank(new_sts)
        print(f"  测试STS: {new_sts} => 排名: {new_rank}")
        if new_rank < best_rank:
            best_rank = new_rank
            best_sts = new_sts

    return best_sts, best_rank


def _generate_api_prompt(target_idx: int, product_list: list, user_msg: str, sts_text: str, tokenizer) -> str:
    """API模式专用：生成带STS的Prompt（适配tokenizer格式）"""
    system_prompt = (
        "You are a product recommendation assistant. Output a numbered list of products ranked by relevance. "
        "Each item must include the product name and key features, all products from the provided product list must be covered without exception, and only the products in the provided product list may be used (no additional products outside the list are allowed)."
    )

    product_text = "Product List:\n"
    for i, product in enumerate(product_list):
        product_str = json.dumps(product, ensure_ascii=False)
        if i == target_idx:
            product_text += f"{product_str} [Strategic Text: {sts_text}]\n"
        else:
            product_text += f"{product_str}\n"

    # 用tokenizer处理特殊字符（避免API解析错误）
    full_prompt = f"{system_prompt}\n\n{product_text}\nUser's request: {user_msg}"
    return tokenizer.bos_token + full_prompt + tokenizer.eos_token if tokenizer.bos_token else full_prompt
    