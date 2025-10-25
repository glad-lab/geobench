import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

# Test on one model, one catalog
import sys
sys.path.insert(0, '.')

from experiment.evaluate import *

result_dir = "results_new/full/suffix/v1"
model = 'deepseek-7b'
catalog = 'books'
indices = [1, 2, 3]  # Just 3 targets for quick test

device = "cuda" if torch.cuda.is_available() else "cpu"
ppl_model, ppl_tokenizer = get_model("lmsys/vicuna-7b-v1.5", 16, device)

print("Testing rank...")
avg_rank, std_rank = calculate_average_rank(result_dir, model, catalog, True, indices)
print(f"Rank: {avg_rank:.2f}±{std_rank:.2f}")

print("\nTesting perplexity...")
avg_ppl, std_ppl = calculate_avg_perplexity(result_dir, model, catalog, True, ppl_model, ppl_tokenizer, device, indices)
print(f"Perplexity: {avg_ppl:.2f}±{std_ppl:.2f}")

print("\nTesting bad words...")
avg_bad, std_bad = calculate_avg_bad_word_ratio(result_dir, model, catalog, True, indices)
print(f"Bad word ratio: {avg_bad:.2f}±{std_bad:.2f}")