# To find the categories with at least 8 products in the

import os

ROOT = "benchmark_data/rewrite_to_rank"
MIN_PRODUCTS = 8

def main():
    if not os.path.isdir(ROOT):
        raise SystemExit(f"Directory not found: {ROOT}")

    ok_categories = []

    for fname in sorted(os.listdir(ROOT)):
        if not fname.endswith(".jsonl"):
            continue

        path = os.path.join(ROOT, fname)
        with open(path, "r") as f:
            # count non-empty lines = products
            n_products = sum(1 for line in f if line.strip())

        catalog = os.path.splitext(fname)[0]

        if n_products >= MIN_PRODUCTS:
            ok_categories.append((catalog, n_products))

    print(f"Categories with >= {MIN_PRODUCTS} products:\n")
    for catalog, n_products in ok_categories:
        print(f"{catalog}\t{n_products}")

    # Optional: write to a file for easy copy into YAML
    out_path = "rewrite_to_rank_at_least_8.txt"
    with open(out_path, "w") as out:
        for catalog, n_products in ok_categories:
            out.write(f"{catalog}\t{n_products}\n")
    print(f"\nSaved list to {out_path}")

if __name__ == "__main__":
    main()
