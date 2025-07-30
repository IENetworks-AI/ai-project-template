"""
Data Pipeline Orchestration for Retail Sales Insight
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import yaml
import logging
from typing import Optional

# Import our modules
from etl.extract.extract_csv import extract_csv_files
from etl.transform.transform_sales import clean_and_aggregate_sales, get_top_categories
from etl.load.load_data import save_processed_data, load_processed_data
from src.validation.schema import validate_sales_schema
from src.utils.logging import get_logger
from src.utils.file_io import load_yaml_config, ensure_dir

logger = get_logger('data_pipeline')

def run_data_pipeline() -> bool:
    """
    Run the complete data pipeline for Retail Sales Insight
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Starting Retail Sales Insight data pipeline")
        
        # Load configuration
        config = load_yaml_config()
        if not config:
            logger.error("Failed to load configuration")
            return False
        
        # Get paths from config
        raw_data_path = config.get('data_paths', {}).get('raw_data_path', 'data/raw/')
        processed_data_path = config.get('data_paths', {}).get('processed_data_path', 'data/processed/')
        output_file = config.get('data_paths', {}).get('output_file', 'data/processed/sales_insights.csv')
        
        # Ensure directories exist
        ensure_dir(raw_data_path)
        ensure_dir(processed_data_path)
        
        # Step 1: Extract data
        logger.info("Step 1: Extracting data from CSV files")
        df = extract_csv_files(raw_data_path)
        
        if df is None or df.empty:
            logger.error("No data extracted from CSV files")
            return False
        
        logger.info(f"Extracted {len(df)} rows of data")
        
        # Step 2: Validate data
        logger.info("Step 2: Validating data schema")
        is_valid, validation_results = validate_sales_schema(df)
        
        if not is_valid:
            logger.error(f"Data validation failed: {validation_results.get('errors', [])}")
            return False
        
        logger.info("Data validation passed")
        
        # Step 3: Transform data
        logger.info("Step 3: Transforming and aggregating sales data")
        aggregated_df = clean_and_aggregate_sales(df)
        
        if aggregated_df is None or aggregated_df.empty:
            logger.error("Failed to aggregate sales data")
            return False
        
        logger.info(f"Successfully aggregated data into {len(aggregated_df)} categories")
        
        # Step 4: Save processed data
        logger.info("Step 4: Saving processed data")
        if not save_processed_data(aggregated_df, output_file):
            logger.error("Failed to save processed data")
            return False
        
        logger.info(f"Processed data saved to {output_file}")
        
        # Step 5: Generate insights (optional)
        logger.info("Step 5: Generating business insights")
        threshold = config.get('business_logic', {}).get('category_threshold', 1000)
        limit = config.get('business_logic', {}).get('top_categories_limit', 5)
        
        insights = get_top_categories(aggregated_df, threshold, limit)
        logger.info(f"Generated insights: {insights.get('message', 'No insights')}")
        
        logger.info("Data pipeline completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Data pipeline failed: {e}")
        return False

def get_sales_insights() -> Optional[dict]:
    """
    Get sales insights from processed data
    
    Returns:
        Dictionary with sales insights or None if failed
    """
    try:
        # Load configuration
        config = load_yaml_config()
        if not config:
            logger.error("Failed to load configuration")
            return None
        
        # Load processed data
        output_file = config.get('data_paths', {}).get('output_file', 'data/processed/sales_insights.csv')
        df = load_processed_data(output_file)
        
        if df is None or df.empty:
            logger.error("No processed data found")
            return None
        
        # Generate insights
        threshold = config.get('business_logic', {}).get('category_threshold', 1000)
        limit = config.get('business_logic', {}).get('top_categories_limit', 5)
        
        insights = get_top_categories(df, threshold, limit)
        return insights
        
    except Exception as e:
        logger.error(f"Error getting sales insights: {e}")
        return None

if __name__ == "__main__":
    success = run_data_pipeline()
    if success:
        print("✅ Data pipeline completed successfully")
    else:
        print("❌ Data pipeline failed")
        sys.exit(1) 