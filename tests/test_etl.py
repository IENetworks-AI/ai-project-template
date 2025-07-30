"""
Tests for ETL components of Retail Sales Insight Pipeline
"""
import pytest
import pandas as pd
import os
import tempfile
import shutil

from etl.extract.extract_csv import extract_csv_files, extract_single_csv
from etl.transform.transform_sales import clean_and_aggregate_sales, get_top_categories
from etl.load.load_data import save_processed_data, load_processed_data
from src.validation.schema import validate_sales_schema

class TestETL:
    """Test class for ETL components"""
    
    @pytest.fixture
    def sample_sales_data(self):
        """Create sample sales data for testing"""
        return pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
            'Product Category': ['Electronics', 'Clothing', 'Electronics', 'Beauty'],
            'Total Amount': [1500.0, 800.0, 2000.0, 600.0],
            'Customer ID': ['C001', 'C002', 'C003', 'C004']
        })
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_extract_single_csv(self, sample_sales_data, temp_data_dir):
        """Test single CSV extraction"""
        # Save sample data to CSV
        csv_path = os.path.join(temp_data_dir, 'test_sales.csv')
        sample_sales_data.to_csv(csv_path, index=False)
        
        # Extract the CSV
        result = extract_single_csv(csv_path)
        
        assert result is not None
        assert len(result) == len(sample_sales_data)
        assert list(result.columns) == list(sample_sales_data.columns)
    
    def test_extract_csv_files(self, sample_sales_data, temp_data_dir):
        """Test multiple CSV extraction"""
        # Save multiple CSV files
        csv1_path = os.path.join(temp_data_dir, 'sales1.csv')
        csv2_path = os.path.join(temp_data_dir, 'sales2.csv')
        
        sample_sales_data.to_csv(csv1_path, index=False)
        sample_sales_data.to_csv(csv2_path, index=False)
        
        # Extract all CSV files
        result = extract_csv_files(temp_data_dir)
        
        assert result is not None
        assert len(result) == len(sample_sales_data) * 2  # Two files
        assert 'Product Category' in result.columns
        assert 'Total Amount' in result.columns
    
    def test_clean_and_aggregate_sales(self, sample_sales_data):
        """Test sales data cleaning and aggregation"""
        result = clean_and_aggregate_sales(sample_sales_data)
        
        assert result is not None
        assert len(result) == 3  # 3 unique categories
        assert 'category' in result.columns
        assert 'total_sales' in result.columns
        assert 'transaction_count' in result.columns
        
        # Check that Electronics has highest sales
        electronics_row = result[result['category'] == 'Electronics'].iloc[0]
        assert electronics_row['total_sales'] == 3500.0  # 1500 + 2000
    
    def test_get_top_categories(self, sample_sales_data):
        """Test top categories identification"""
        # First aggregate the data
        agg_data = clean_and_aggregate_sales(sample_sales_data)
        
        # Get top categories
        result = get_top_categories(agg_data, threshold=1000, limit=2)
        
        assert result is not None
        assert 'top_categories' in result
        assert len(result['top_categories']) == 2
        
        # Check that Electronics is first (highest sales)
        assert result['top_categories'][0]['category'] == 'Electronics'
        assert result['top_categories'][0]['total_sales'] == 3500.0
    
    def test_save_and_load_processed_data(self, sample_sales_data, temp_data_dir):
        """Test saving and loading processed data"""
        # Process the data
        processed_data = clean_and_aggregate_sales(sample_sales_data)
        
        # Save to file
        output_path = os.path.join(temp_data_dir, 'processed_sales.csv')
        success = save_processed_data(processed_data, output_path)
        
        assert success is True
        assert os.path.exists(output_path)
        
        # Load the data
        loaded_data = load_processed_data(output_path)
        
        assert loaded_data is not None
        assert len(loaded_data) == len(processed_data)
        assert list(loaded_data.columns) == list(processed_data.columns)
    
    def test_validate_sales_schema(self, sample_sales_data):
        """Test sales data schema validation"""
        is_valid, results = validate_sales_schema(sample_sales_data)
        
        assert is_valid is True
        assert 'valid' in results
        assert results['valid'] is True
    
    def test_validate_sales_schema_missing_columns(self):
        """Test schema validation with missing columns"""
        invalid_data = pd.DataFrame({
            'Date': ['2023-01-01'],
            'Customer ID': ['C001']
            # Missing Product Category and Total Amount
        })
        
        is_valid, results = validate_sales_schema(invalid_data)
        
        assert is_valid is False
        assert 'errors' in results
        assert len(results['errors']) > 0
    
    def test_validate_sales_schema_invalid_data_types(self):
        """Test schema validation with invalid data types"""
        invalid_data = pd.DataFrame({
            'Product Category': ['Electronics'],
            'Total Amount': ['not_a_number']  # Should be numeric
        })
        
        is_valid, results = validate_sales_schema(invalid_data)
        
        assert is_valid is False
        assert 'errors' in results
        assert len(results['errors']) > 0 