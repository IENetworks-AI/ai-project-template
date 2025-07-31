import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment by creating required directories"""
    required_dirs = ["data/raw", "data/processed", "data/features"]
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    yield
    
    # Cleanup can be added here if needed 