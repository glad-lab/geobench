#!/usr/bin/env python3
import sys
import torch
import transformers
import nltk
import wandb
import os

def test_model_loading():
    """Test loading the actual model specified in config"""
    print("Testing model loading...")
    try:
        # Test the specific model from suffix.yaml
        model_name = "deepseek-ai/deepseek-llm-7b-chat"
        
        print(f"Attempting to load {model_name}...")
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
        
        # Try loading just the config first (lighter test)
        config = transformers.AutoConfig.from_pretrained(model_name)
        print(f"✓ Model config loaded successfully")
        
        # Test tokenization
        test_text = "This is a test"
        tokens = tokenizer(test_text, return_tensors="pt")
        print(f"✓ Tokenization works")
        
        return True
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        return False

def test_experiment_imports():
    """Test experiment-specific imports"""
    print("Testing experiment imports...")
    try:
        from experiment.process import process_bad_words, greedy_decode, init_prompt
        from experiment.main import main
        from experiment.get import get_model
        print("✓ All experiment modules imported")
        return True
    except ImportError as e:
        print(f"✗ Experiment import failed: {e}")
        return False

def test_cuda_and_gpu():
    """Test CUDA availability"""
    print("Testing CUDA...")
    available = torch.cuda.is_available()
    print(f"CUDA available: {available}")
    if available:
        print(f"GPU count: {torch.cuda.device_count()}")
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
        
        # Test basic GPU operation
        try:
            x = torch.randn(100, 100).cuda()
            y = torch.matmul(x, x)
            print("✓ Basic GPU operations work")
            return True
        except Exception as e:
            print(f"✗ GPU operation failed: {e}")
            return False
    return available

def test_dependencies():
    """Test critical dependencies"""
    print("Testing dependencies...")
    try:
        import yaml
        import numpy as np
        import pandas as pd
        from nltk.corpus import stopwords
        
        # Test NLTK data
        stops = stopwords.words('english')
        print(f"✓ NLTK working: {len(stops)} stopwords")
        
        # Test PyTorch/Torchvision compatibility
        import torchvision
        print(f"✓ PyTorch {torch.__version__} + Torchvision {torchvision.__version__}")
        
        return True
    except Exception as e:
        print(f"✗ Dependency test failed: {e}")
        return False

def test_config_file():
    """Test config file loading"""
    print("Testing config file...")
    try:
        import yaml
        with open('configs/suffix.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        model = config['parameters']['model']['value']
        print(f"✓ Config loaded, model: {model}")
        
        if model == 'deepseek-7b':
            print("✓ Using deepseek-7b (open model)")
            return True
        else:
            print(f"⚠ Warning: {model} may require authentication")
            return True
            
    except Exception as e:
        print(f"✗ Config file test failed: {e}")
        return False

def test_minimal_experiment():
    """Run a minimal version of the actual experiment"""
    print("Testing minimal experiment workflow...")
    try:
        # Test the actual get_model function with deepseek
        from experiment.get import get_model
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {device}")
        
        # Try to load the model (this is what failed before)
        model_name = "deepseek-ai/deepseek-llm-7b-chat"
        print(f"Loading {model_name} for real test...")
        
        model, tokenizer = get_model(model_name, 16, device)
        print("✓ Model loaded successfully via experiment.get")
        
        # Test basic inference
        test_input = tokenizer("Hello", return_tensors="pt").to(device)
        with torch.no_grad():
            output = model.generate(**test_input, max_length=10, do_sample=False)
        print("✓ Basic inference works")
        
        # Clean up memory
        del model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        return True
    except Exception as e:
        print(f"✗ Minimal experiment failed: {e}")
        print(f"Full error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Comprehensive Setup Verification ===")
    print("This test will actually try to load models and run experiment code.")
    print()
    
    tests = [
        ("Config File", test_config_file),
        ("Dependencies", test_dependencies), 
        ("Experiment Imports", test_experiment_imports),
        ("CUDA/GPU", test_cuda_and_gpu),
        ("Model Loading", test_model_loading),
        ("Minimal Experiment", test_minimal_experiment),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            result = test_func()
            results.append(result)
            print(f"Result: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"✗ {name} crashed: {e}")
            results.append(False)
    
    print(f"\n=== Final Results ===")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if all(results):
        print("🎉 ALL TESTS PASSED! Ready to submit SLURM job.")
    else:
        print("⚠️  Some tests failed. Fix issues before submitting job.")
        print("This comprehensive test caught issues the basic test missed.")
    
    if not torch.cuda.is_available():
        print("\nNote: CUDA tests will only pass on GPU compute nodes, not login nodes.")
