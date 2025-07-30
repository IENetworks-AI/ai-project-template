"""
Tests for utility functions in Retail Sales Insight Pipeline
"""
import pytest
import pandas as pd
import os
import tempfile
import shutil

from src.utils.logging import get_logger
from src.utils.file_io import ensure_dir, load_yaml_config, save_data, load_data

class TestUtils:
    """Test class for utility functions"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_logger_creation(self):
        """Test that logger can be created"""
        logger = get_logger('test_logger')
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'debug')
    
    def test_ensure_dir(self, temp_dir):
        """Test directory creation"""
        new_dir = os.path.join(temp_dir, 'test_subdir')
        
        # Directory should not exist initially
        assert not os.path.exists(new_dir)
        
        # Create directory
        success = ensure_dir(new_dir)
        
        assert success is True
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
    
    def test_load_yaml_config(self):
        """Test YAML configuration loading"""
        config = load_yaml_config('config/config.yaml')
        
        assert isinstance(config, dict)
        assert 'data_paths' in config
        assert 'business_logic' in config
        assert 'api' in config
    
    def test_save_and_load_data_csv(self, temp_dir):
        """Test saving and loading CSV data"""
        # Create test data
        test_data = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        })
        
        # Save data
        csv_path = os.path.join(temp_dir, 'test_data.csv')
        success = save_data(test_data, csv_path)
        
        assert success is True
        assert os.path.exists(csv_path)
        
        # Load data
        loaded_data = load_data(csv_path)
        
        assert loaded_data is not None
        assert len(loaded_data) == len(test_data)
        assert list(loaded_data.columns) == list(test_data.columns)
        assert loaded_data.equals(test_data)
    
    def test_save_and_load_data_json(self, temp_dir):
        """Test saving and loading JSON data"""
        # Create test data
        test_data = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        })
        
        # Save data
        json_path = os.path.join(temp_dir, 'test_data.json')
        success = save_data(test_data, json_path)
        
        assert success is True
        assert os.path.exists(json_path)
        
        # Load data
        loaded_data = load_data(json_path)
        
        assert loaded_data is not None
        assert len(loaded_data) == len(test_data)
        assert list(loaded_data.columns) == list(test_data.columns)
    
    def test_load_data_nonexistent_file(self):
        """Test loading data from non-existent file"""
        with pytest.raises(FileNotFoundError):
            load_data('nonexistent_file.csv')
    
    def test_save_data_unsupported_format(self, temp_dir):
        """Test saving data with unsupported format"""
        test_data = pd.DataFrame({'A': [1, 2, 3]})
        txt_path = os.path.join(temp_dir, 'test_data.txt')
        
        with pytest.raises(ValueError):
            save_data(test_data, txt_path)
    
    def test_project_structure(self):
        """Test that project has required structure"""
        required_files = [
            'requirements.txt',
            'config/config.yaml',
            'api/app.py',
            'src/__init__.py',
            'src/utils/__init__.py'
        ]
        
        for file_path in required_files:
            assert os.path.exists(file_path), f"Required file {file_path} does not exist"
