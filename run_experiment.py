#!/usr/bin/env python3
"""
Main entrypoint for running adversarial SEO experiments.

This script provides a simple interface to run experiments without
navigating the examples directory.

Usage:
    python run_experiment.py --help
    python run_experiment.py --type single_attack
    python run_experiment.py --type prisoner_dilemma
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point"""
    print("Adversarial SEO Research Framework")
    print("=" * 50)
    print()
    print("Available examples:")
    print("  1. python examples/experiment_usage.py")
    print("  2. python examples/rag_example.py")
    print("  3. python examples/experiments_evaluation_integration.py")
    print()
    print("Database setup:")
    print("  python scripts/repopulate_db.py --reset --verify")
    print()
    print("For detailed usage, see README.md")
    print()

if __name__ == "__main__":
    main()
