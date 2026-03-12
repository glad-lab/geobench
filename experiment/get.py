import transformers, torch, json
import os

def get_user_query(catalog):
    user_msg = f'I am looking for a {catalog}. Can I get some recommendations from the following products?'
    return user_msg


def get_model(model_path, precision, device):
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=eval(f'torch.float{precision}'),
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        use_cache=False,
        use_safetensors=True
    ).to(device).eval()

    model.generation_config.do_sample = True

    for param in model.parameters():
        param.requires_grad = False
 
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_path,
                                                           trust_remote_code=True,
                                                           use_fast=False,
                                                           use_cache=True)

    if 'llama' in model_path:
        tokenizer.pad_token = tokenizer.unk_token
        tokenizer.padding_side = 'left'

    return model, tokenizer


def get_product_list(catalog, target_product_idx, dataset):
    # Check if using benchmark dataset or original datasets
    if dataset in ["rewrite_to_rank", "ragdoll", "ragdoll_subsampled", "llm_rank_subsampled", "llmrank_subsampled", "llm_rank_optimizer", "llm_rank_optimizer_subsampled", "cseo_subsampled"]:
        data_path = f'benchmark_data/{dataset}/{catalog}.jsonl'
    else:
        data_path = f'data2/{dataset}/{catalog}.jsonl'
    
    product_list = []
    with open(data_path, "r") as file:
        for line in file:
            product_list.append(json.loads(line))

    target_product_idx = target_product_idx - 1
    
    target_product = product_list[target_product_idx]['Name']
    target_product_natural = product_list[target_product_idx]['Natural']
    target_str = "1. " + target_product

    return product_list, target_product, target_product_natural, target_str