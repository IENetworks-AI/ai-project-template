#!/usr/bin/env python3
"""
Dependency Checker Script
Verifies all required packages are installed and accessible
"""

import sys
import importlib

def check_package(package_name, import_name=None):
    """Check if a package is installed and importable"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - NOT INSTALLED")
        return False

def main():
    """Check all required dependencies"""
    print("🔍 Checking Dependencies")
    print("=" * 40)
    
    # Core ML/AI packages
    print("\n📊 Core ML/AI Packages:")
    core_packages = [
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("joblib", "joblib"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn")
    ]
    
    core_missing = []
    for package, import_name in core_packages:
        if not check_package(package, import_name):
            core_missing.append(package)
    
    # Web API and configuration
    print("\n🌐 Web API and Configuration:")
    web_packages = [
        ("flask", "flask"),
        ("PyYAML", "yaml"),
        ("requests", "requests")
    ]
    
    web_missing = []
    for package, import_name in web_packages:
        if not check_package(package, import_name):
            web_missing.append(package)
    
    # Testing and development
    print("\n🧪 Testing and Development:")
    test_packages = [
        ("pytest", "pytest")
    ]
    
    test_missing = []
    for package, import_name in test_packages:
        if not check_package(package, import_name):
            test_missing.append(package)
    
    # Optional packages
    print("\n🔧 Optional Packages:")
    optional_packages = [
        ("cx_Oracle", "cx_Oracle")
    ]
    
    optional_missing = []
    for package, import_name in optional_packages:
        if not check_package(package, import_name):
            optional_missing.append(package)
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Summary:")
    
    all_missing = core_missing + web_missing + test_missing
    
    if not all_missing:
        print("✅ All required dependencies are installed!")
        print("✅ Project is ready to run")
    else:
        print(f"❌ Missing {len(all_missing)} required dependencies:")
        for package in all_missing:
            print(f"   - {package}")
        
        print("\n🔧 To install missing dependencies:")
        print("   pip install -r requirements.txt")
    
    if optional_missing:
        print(f"\n⚠️  Missing {len(optional_missing)} optional dependencies:")
        for package in optional_missing:
            print(f"   - {package}")
        print("   (These are optional and won't prevent basic functionality)")
    
    print("\n🚀 Next Steps:")
    if not all_missing:
        print("1. Run tests: python -m pytest tests/ -v")
        print("2. Run training: python src/train.py")
        print("3. Run pipeline: python pipelines/ai_pipeline.py")
    else:
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run this check again: python check_dependencies.py")

if __name__ == "__main__":
    main() 