"""
Data Loading for Retail Sales Insight Pipeline
"""
import pandas as pd
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def save_processed_data(df: pd.DataFrame, output_path: str) -> bool:
    """
    Save processed data to CSV file
    
    Args:
        df: Processed DataFrame to save
        output_path: Path where to save the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Saving processed data to {output_path}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved {len(df)} rows to {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving processed data: {e}")
        return False

def load_processed_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Load processed data from CSV file
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame if successful, None otherwise
    """
    try:
        logger.info(f"Loading processed data from {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return None
        
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded {len(df)} rows from {file_path}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading processed data: {e}")
        return None 