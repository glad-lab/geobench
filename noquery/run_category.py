"""
Simple script to run C-SEO benchmark on a category from unified_data.json.

This script:
1. Extracts the category from unified_data.json
2. Runs the sampling, cohort building, and method application steps
3. Provides instructions for running benchmarks

Usage:
    python noquery/run_category.py "Motorcycle Accessories" --method Authoritative
    python noquery/run_category.py "Flooring" --method Statistics --samples 15
"""

import argparse
import subprocess
import sys
from pathlib import Path


def sanitize_category(category: str) -> str:
    """Convert category name to safe filename."""
    return category.lower().replace(" ", "_").replace("/", "_")


def run_cmd(cmd: list, description: str):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n❌ ERROR: {description} failed with code {result.returncode}")
        sys.exit(1)
    print(f"\n✓ {description} completed successfully")


def main():
    ap = argparse.ArgumentParser(
        description="Run C-SEO benchmark on a category",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    ap.add_argument("category", help="Category name (e.g., 'Motorcycle Accessories')")
    ap.add_argument("--method", default="Authoritative", help="C-SEO method to apply")
    ap.add_argument("--samples", type=int, help="Number of documents to sample (default: auto)")
    ap.add_argument("--ratio", type=float, default=0.7, help="Sampling ratio if --samples not specified")
    ap.add_argument("--cohort-size", type=int, default=8, help="Documents per cohort")
    ap.add_argument("--cohorts-per-doc", type=int, default=2, help="Cohorts per document")
    ap.add_argument("--llm", default="gpt-4o-2024-11-20", help="LLM model name")
    ap.add_argument("--embedding-backend", default="openai", choices=["local", "openai"], help="Embedding backend")
    ap.add_argument("--embedding-model", default="text-embedding-3-large", help="Embedding model name")
    ap.add_argument("--list", action="store_true", help="List all categories and exit")

    args = ap.parse_args()

    # List categories
    if args.list:
        run_cmd([
            sys.executable,
            "noquery/scripts/1_extract_category.py",
            "--list"
        ], "Listing categories")
        return

    # Setup paths
    cat_safe = sanitize_category(args.category)
    cat_dir = Path("noquery/data/datasets") / cat_safe
    cat_file = cat_dir / f"{cat_safe}.json"
    need_improve = cat_dir / "need_improve.json"
    improved = cat_dir / f"improved_{args.method}.json"

    print("\n" + "="*80)
    print(f"C-SEO BENCHMARK PIPELINE")
    print("="*80)
    print(f"Category: {args.category}")
    print(f"Method: {args.method}")
    print(f"Output directory: {cat_dir}")
    print("="*80)

    # Step 1: Extract category
    run_cmd([
        sys.executable,
        "noquery/scripts/1_extract_category.py",
        "--category", args.category
    ], f"[1/4] Extract category '{args.category}'")

    # Step 2: Sample documents
    sample_args = [
        sys.executable,
        "noquery/scripts/2_gen_need_improve.py",
        "--changed_json", str(cat_file),
        "--out_json", str(need_improve),
        "--strategy", "random",
        "--seed", "42"
    ]

    if args.samples:
        sample_args.extend(["--num", str(args.samples)])
    else:
        sample_args.extend(["--ratio", str(args.ratio)])

    run_cmd(sample_args, "[2/4] Sample documents")

    # Step 3: Build cohorts
    run_cmd([
        sys.executable,
        "noquery/scripts/3_build_cohorts.py",
        "--changed_json", str(cat_file),
        "--need_improve_json", str(need_improve),
        "--backend", args.embedding_backend,
        "--model_name", args.embedding_model,
        "--out_dir", str(cat_dir),
        "--cohort_size", str(args.cohort_size),
        "--cohorts_per_doc", str(args.cohorts_per_doc)
    ], "[3/4] Build semantic cohorts")

    # Step 4: Apply method
    run_cmd([
        sys.executable,
        "noquery/scripts/4_improve_texts.py",
        "--changed_json", str(cat_file),
        "--need_improve_json", str(need_improve),
        "--out_json", str(improved),
        "--method", args.method,
        "--llm_name", args.llm,
        "--config", "config.json"
    ], f"[4/4] Apply {args.method} method")

    # Final summary
    print("\n" + "="*80)
    print("✓ PIPELINE SETUP COMPLETE!")
    print("="*80)
    print("\nGenerated files:")
    print(f"  • Category data: {cat_file}")
    print(f"  • Samples: {need_improve}")
    print(f"  • Cohorts: {cat_dir / 'cohorts.json'}")
    print(f"  • Boosted: {cat_dir / 'boosted.json'}")
    print(f"  • Improved texts: {improved}")
    print("\n" + "-"*80)
    print("NEXT STEPS:")
    print("-"*80)
    print("\n1. Wait for OpenAI batch job to complete")
    print("   (You can check status using fetch_batch_results.py)")
    print("\n2. Run baseline benchmark:")
    print(f"   python noquery/scripts/5_run_benchmark.py \\")
    print(f"       --domain {cat_safe} \\")
    print(f"       --changed_json {cat_file} \\")
    print(f"       --cohorts {cat_dir}/cohorts.json \\")
    print(f"       --boosted {cat_dir}/boosted.json \\")
    print(f"       --method baseline")
    print("\n3. Run method benchmark:")
    print(f"   python noquery/scripts/5_run_benchmark.py \\")
    print(f"       --domain {cat_safe} \\")
    print(f"       --changed_json {cat_file} \\")
    print(f"       --cohorts {cat_dir}/cohorts.json \\")
    print(f"       --boosted {cat_dir}/boosted.json \\")
    print(f"       --improved_json {improved} \\")
    print(f"       --method {args.method}")
    print("\n4. Evaluate results:")
    print(f"   python noquery/scripts/6_eval_wilcoxon.py \\")
    print(f"       --domain {cat_safe} \\")
    print(f"       --method {args.method} \\")
    print(f"       --llm_name {args.llm}")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
