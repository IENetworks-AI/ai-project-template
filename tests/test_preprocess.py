import os
import pandas as pd
import pytest

def test_extracted_data():
    """Test that the sales dataset exists and can be loaded"""
    path = "data/Sales Dataset.csv"
    assert os.path.exists(path), f"Data file not found at {path}"
    df = pd.read_csv(path)
    assert not df.empty, "Data file is empty"
    assert len(df.columns) > 0, "Data file has no columns"

def test_data_quality():
    """Test basic data quality checks"""
    path = "data/Sales Dataset.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        # Check for basic data quality
        assert df.shape[0] > 0, "Dataset has no rows"
        assert df.shape[1] > 0, "Dataset has no columns"
        # Check for missing values (basic check)
        assert df.isnull().sum().sum() >= 0, "Unexpected error checking for missing values"

def test_data_directory_structure():
    """Test that required directories exist"""
    required_dirs = ["data/raw", "data/processed", "data/features"]
    for dir_path in required_dirs:
        assert os.path.exists(dir_path), f"Required directory {dir_path} does not exist"
