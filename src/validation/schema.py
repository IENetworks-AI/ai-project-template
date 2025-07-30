"""
Data validation for Retail Sales Insight Pipeline
"""
import pandas as pd
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

def validate_sales_schema(df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate sales data schema
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Tuple of (is_valid, validation_results)
    """
    try:
        logger.info("Validating sales data schema")
        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required columns
        required_columns = ['Product Category', 'Total Amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Missing required columns: {missing_columns}")
            logger.error(f"Missing required columns: {missing_columns}")
        
        # Check data types
        if 'Total Amount' in df.columns:
            try:
                pd.to_numeric(df['Total Amount'], errors='raise')
            except:
                validation_results['valid'] = False
                validation_results['errors'].append("Total Amount column contains non-numeric values")
                logger.error("Total Amount column contains non-numeric values")
        
        # Check for empty dataframe
        if df.empty:
            validation_results['valid'] = False
            validation_results['errors'].append("DataFrame is empty")
            logger.error("DataFrame is empty")
        
        # Check for missing values in key columns
        if 'Product Category' in df.columns and 'Total Amount' in df.columns:
            missing_count = df[['Product Category', 'Total Amount']].isnull().sum().sum()
            if missing_count > 0:
                validation_results['warnings'].append(f"Found {missing_count} missing values in key columns")
                logger.warning(f"Found {missing_count} missing values in key columns")
        
        logger.info(f"Schema validation completed. Valid: {validation_results['valid']}")
        return validation_results['valid'], validation_results
        
    except Exception as e:
        logger.error(f"Error in schema validation: {e}")
        return False, {'valid': False, 'errors': [str(e)]} 