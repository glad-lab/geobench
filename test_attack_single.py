"""
Test adversarial attack on a single category.
Usage: python test_attack_single.py
"""

import os
import dataset
from attack import (
    load_target,
    load_attacker,
    run_target_and_evaluator,
    get_adversarial_prompt,
    poison_doc
)
import numpy as np

DATASET_PATH = './dataset/dataset'

class Args:
    # Target model (the one being attacked)
    target_model = 'gpt-3.5'
    target_temp = 0.3
    target_top_p = 1.0
    target_max_tokens = 1500

    # Attacker model (generates adversarial prompts)
    attacker_model = 'gpt-3.5'  # Use gpt-3.5 to save cost (paper uses gpt-4-turbo)
    attacker_temp = 1.0
    attacker_top_p = 1.0
    attacker_max_tokens = 1024

    # TAP algorithm parameters (reduced for quick test)
    root_nodes = 1        # Default: 3
    branching_factor = 1  # Default: 3
    width = 2             # Default: 5
    depth = 2             # Default: 5
    response_summary_chars = 500
    stop_score = 7
    target_responses = 1  # Default: 2

def main():
    if not os.environ.get('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY not set!")
        return

    args = Args()

    # Test with 'tablet' category
    category = 'tablet'

    print(f"Loading products for: {category}")
    products, docs = [], []
    for product, doc, _ in dataset.get_products(
        category, dataset_dir=DATASET_PATH, returned_doc='content_truncate'
    ):
        products.append(product)
        docs.append(doc)

    user_query = dataset.user_query(category)
    target = load_target(args)

    # Step 1: Get natural ranking
    print("\n" + "="*50)
    print("STEP 1: Natural Ranking (before attack)")
    print("="*50)

    scores, _, responses = run_target_and_evaluator(
        target_chat=target,
        user_query=user_query,
        products=products,
        docs=docs,
        num_runs=1,
        include_ordering_prompt=True,
        shuffle_context_order=True
    )

    # Find lowest ranked product
    avg_scores = {p: np.mean(s) for p, s in scores.items()}
    promoted_product = min(avg_scores, key=avg_scores.get)
    promoted_idx = products.index(promoted_product)
    promoted_doc = docs[promoted_idx]

    print("\nNatural ranking:")
    for p, s in sorted(avg_scores.items(), key=lambda x: x[1], reverse=True):
        marker = " <-- TARGET (lowest)" if p == promoted_product else ""
        print(f"  {p.brand} {p.model}: {s:.1f}{marker}")

    # Step 2: Generate adversarial prompt
    print("\n" + "="*50)
    print(f"STEP 2: Generating attack for {promoted_product.brand}")
    print("="*50)

    other_products = [p for p in products if p != promoted_product]
    other_docs = [d for i, d in enumerate(docs) if i != promoted_idx]

    adversarial_prompt = get_adversarial_prompt(
        user_query=user_query,
        promoted_product=promoted_product,
        promoted_doc=promoted_doc,
        other_products=other_products,
        other_docs=other_docs,
        include_ordering_prompt=True,
        shuffle_context_order=True,
        args=args
    )

    if adversarial_prompt:
        print(f"\nGenerated adversarial prompt:\n{adversarial_prompt[:300]}...")
    else:
        print("\nFailed to generate adversarial prompt")
        return

    # Step 3: Test with poisoned document
    print("\n" + "="*50)
    print("STEP 3: Ranking after attack")
    print("="*50)

    poisoned_doc = poison_doc(promoted_doc, adversarial_prompt)
    poisoned_docs = [poisoned_doc] + other_docs
    all_products = [promoted_product] + other_products

    adv_scores, _, adv_responses = run_target_and_evaluator(
        target_chat=target,
        user_query=user_query,
        products=all_products,
        docs=poisoned_docs,
        num_runs=1,
        include_ordering_prompt=True,
        shuffle_context_order=True
    )

    print("\nRanking after attack:")
    adv_avg = {p: np.mean(s) for p, s in adv_scores.items()}
    for p, s in sorted(adv_avg.items(), key=lambda x: x[1], reverse=True):
        marker = " <-- TARGET" if p == promoted_product else ""
        print(f"  {p.brand} {p.model}: {s:.1f}{marker}")

    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    old_score = avg_scores[promoted_product]
    new_score = adv_avg[promoted_product]
    print(f"Target product: {promoted_product.brand} {promoted_product.model}")
    print(f"Score before attack: {old_score:.1f}")
    print(f"Score after attack:  {new_score:.1f}")
    print(f"Improvement: +{new_score - old_score:.1f}")

if __name__ == "__main__":
    main()
