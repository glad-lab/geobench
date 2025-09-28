#!/usr/bin/env python3
import sys
import torch
import transformers
import nltk
import wandb

def test_basic_imports():
    print("Testing basic imports...")
    try:
        from experiment.process import process_bad_words, greedy_decode, init_prompt
        print("✓ Experiment modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_cuda():
    print("Testing CUDA...")
    available = torch.cuda.is_available()
    print(f"CUDA available: {available}")
    if available:
        print(f"GPU count: {torch.cuda.device_count()}")
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
    return available

def test_nltk():
    print("Testing NLTK...")
    try:
        from nltk.corpus import stopwords
        stops = stopwords.words('english')
        print(f"✓ NLTK working: {len(stops)} stopwords loaded")
        return True
    except Exception as e:
        print(f"✗ NLTK error: {e}")
        return False

if __name__ == "__main__":
    print("=== Setup Verification ===")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("CUDA", test_cuda),
        ("NLTK", test_nltk)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            results.append(False)
    
    print(f"\n=== Results ===")
    if all(results):
        print("✓ All tests passed!")
    else:
        print("⚠ Some tests failed.")
        
    print("Note: CUDA will only be True on GPU compute nodes, not login nodes.")
