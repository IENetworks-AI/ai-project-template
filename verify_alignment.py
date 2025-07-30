#!/usr/bin/env python3
"""
Project Alignment Verification Script
Checks for common misalignments and configuration issues
"""

import os
import sys
import yaml
import pandas as pd
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists and print status"""
    if os.path.exists(dir_path):
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} - MISSING")
        return False

def check_config_alignment():
    """Check configuration file alignment"""
    print("\n🔧 Checking Configuration Alignment...")
    
    config_file = "config/config.yaml"
    if check_file_exists(config_file, "Config file"):
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check target directory
            target_dir = config.get('oracle_server', {}).get('target_dir')
            if target_dir == "/home/ubuntu/ai-project-template":
                print("✅ Target directory correctly configured")
            else:
                print(f"❌ Target directory misconfigured: {target_dir}")
            
            # Check data paths
            data_paths = [
                config.get('raw_data_path'),
                config.get('processed_data_path'),
                config.get('features_path'),
                config.get('models_path')
            ]
            
            for path in data_paths:
                if path:
                    print(f"✅ Data path configured: {path}")
                else:
                    print(f"❌ Missing data path configuration")
                    
        except Exception as e:
            print(f"❌ Error reading config file: {e}")

def check_data_files():
    """Check data file alignment"""
    print("\n📊 Checking Data Files...")
    
    # Check main dataset
    main_data = "data/Sales Dataset.csv"
    if check_file_exists(main_data, "Main dataset"):
        try:
            df = pd.read_csv(main_data)
            print(f"✅ Dataset loaded successfully: {len(df)} rows, {len(df.columns)} columns")
            
            # Check for date column
            if 'Date' in df.columns:
                print("✅ Date column found in dataset")
            else:
                print("❌ Date column not found in dataset")
                
        except Exception as e:
            print(f"❌ Error reading dataset: {e}")
    
    # Check required directories
    required_dirs = [
        ("data/raw", "Raw data directory"),
        ("data/processed", "Processed data directory"),
        ("data/features", "Features directory")
    ]
    
    for dir_path, description in required_dirs:
        check_directory_exists(dir_path, description)

def check_workflow_files():
    """Check GitHub Actions workflow files"""
    print("\n🔄 Checking GitHub Actions Workflows...")
    
    workflow_dir = ".github/workflows"
    if check_directory_exists(workflow_dir, "Workflows directory"):
        workflow_files = [
            "data_pipeline.yml",
            "deploy.yml", 
            "train.yml",
            "preprocess.yml",
            "ssh-test.yml"
        ]
        
        for workflow in workflow_files:
            workflow_path = os.path.join(workflow_dir, workflow)
            check_file_exists(workflow_path, f"Workflow: {workflow}")

def check_service_files():
    """Check service and deployment files"""
    print("\n🚀 Checking Service Files...")
    
    service_files = [
        ("aiapp.service", "Systemd service file"),
        ("deploy.sh", "Deployment script"),
        ("start.sh", "Startup script"),
        ("run_tests.sh", "Test runner script")
    ]
    
    for file_path, description in service_files:
        check_file_exists(file_path, description)

def check_python_modules():
    """Check Python module structure"""
    print("\n🐍 Checking Python Modules...")
    
    modules = [
        ("src/__init__.py", "Source package init"),
        ("src/utils/__init__.py", "Utils package init"),
        ("src/utils/file_io.py", "File I/O utilities"),
        ("src/utils/logging.py", "Logging utilities"),
        ("src/data/train_model.py", "Training module"),
        ("src/data/evaluate_model.py", "Evaluation module"),
        ("etl/extract/extract_data.py", "Data extraction"),
        ("etl/transform/transform_data.py", "Data transformation"),
        ("etl/load/load_data.py", "Data loading"),
        ("pipelines/ai_pipeline.py", "Main pipeline")
    ]
    
    for file_path, description in modules:
        check_file_exists(file_path, description)

def check_test_files():
    """Check test files"""
    print("\n🧪 Checking Test Files...")
    
    test_files = [
        ("tests/__init__.py", "Tests package init"),
        ("tests/test_preprocess.py", "Preprocessing tests"),
        ("tests/test_utils.py", "Utilities tests"),
        ("tests/conftest.py", "Pytest configuration"),
        ("pytest.ini", "Pytest settings")
    ]
    
    for file_path, description in test_files:
        check_file_exists(file_path, description)

def check_dependencies():
    """Check dependency files"""
    print("\n📦 Checking Dependencies...")
    
    dep_files = [
        ("requirements.txt", "Python dependencies"),
        ("README.md", "Project documentation"),
        ("SERVER_DEPLOYMENT.md", "Server deployment guide"),
        ("PROJECT_ALIGNMENT.md", "Alignment documentation")
    ]
    
    for file_path, description in dep_files:
        check_file_exists(file_path, description)

def main():
    """Main verification function"""
    print("🔍 Project Alignment Verification")
    print("=" * 50)
    
    checks = [
        check_config_alignment,
        check_data_files,
        check_workflow_files,
        check_service_files,
        check_python_modules,
        check_test_files,
        check_dependencies
    ]
    
    for check in checks:
        try:
            check()
        except Exception as e:
            print(f"❌ Error during {check.__name__}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Verification completed!")
    print("\n📋 Next Steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run tests: python -m pytest tests/ -v")
    print("3. Test pipeline: python pipelines/ai_pipeline.py")
    print("4. Deploy to server: ./deploy.sh")

if __name__ == "__main__":
    main() 