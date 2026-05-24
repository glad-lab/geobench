"""
Simple test script to verify the project works with a single category.
Usage: python test_single.py
"""

import dataset
from attack import load_target, run_target_and_evaluator
import os

# Fix dataset path (nested dataset/dataset structure)
DATASET_PATH = './dataset/dataset'

class Args:
    target_model = 'gpt-3.5'
    target_temp = 0.3
    target_top_p = 1.0
    target_max_tokens = 1500

def main():
    # Check API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY not set!")
        print("Run: set OPENAI_API_KEY=your-key-here")
        return

    print("Loading model...")
    args = Args()
    target = load_target(args)

    # Test with 'tablet' category (or change to another)
    category = 'tablet'

    print(f"\nLoading products for category: {category}")
    products, docs = [], []
    for product, doc, _ in dataset.get_products(
        category,
        dataset_dir=DATASET_PATH,
        returned_doc='content_truncate'
    ):
        products.append(product)
        docs.append(doc)

    user_query = dataset.user_query(category)

    print(f"Query: {user_query}")
    print(f"Number of products: {len(products)}")
    print("\nProducts:")
    for p in products:
        print(f"  - {p.brand} {p.model}")

    print("\n" + "="*50)
    print("Running evaluation (this calls the OpenAI API)...")
    print("="*50 + "\n")

    # Run single evaluation
    scores, orderings, responses = run_target_and_evaluator(
        target_chat=target,
        user_query=user_query,
        products=products,
        docs=docs,
        num_runs=1,
        include_ordering_prompt=True,
        shuffle_context_order=True
    )

    print("=== Ranking Scores ===")
    sorted_scores = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)
    for product, score_list in sorted_scores:
        print(f"  {product.brand} {product.model}: {score_list[0]}")

    print("\n=== LLM Response (first 800 chars) ===")
    print(responses[0][:800])

    print("\n" + "="*50)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("="*50)

if __name__ == "__main__":
    main()
