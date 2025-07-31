import os
import pytest
import pandas as pd
from src.utils.file_io import save_data, load_data
from src.utils.logging import get_logger

def test_logger_creation():
    """Test that logger can be created"""
    logger = get_logger('test_logger')
    assert logger is not None
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'debug')

def test_save_and_load_data():
    """Test data saving and loading functionality"""
    # Create test data
    test_data = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c']
    })
    
    # Test save - use a path in the current directory
    test_file = './test_data.csv'
    try:
        save_data(test_data, test_file)
        assert os.path.exists(test_file), "File was not saved"
        
        # Test load
        loaded_data = load_data(test_file)
        assert loaded_data is not None, "Data was not loaded"
        assert loaded_data.shape == test_data.shape, "Data shape changed"
        assert loaded_data.equals(test_data), "Data content changed"
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

def test_file_io_with_nonexistent_file():
    """Test file I/O with non-existent file"""
    with pytest.raises(FileNotFoundError):
        load_data('nonexistent_file.csv')

def test_project_structure():
    """Test that project has required ML pipeline structure"""
    required_files = [
        'requirements.txt',
        'config/config.yaml',
        'pipelines/ai_pipeline.py',
        'data/Sales Dataset.csv',
        'src/__init__.py',
        'src/utils/__init__.py',
        'etl/extract/extract_data.py',
        'etl/transform/transform_data.py',
        'etl/load/load_data.py'
    ]
    
    for file_path in required_files:
        assert os.path.exists(file_path), f"Required file {file_path} does not exist"
