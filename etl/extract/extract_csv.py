"""
CSV Data Extraction for Retail Sales Insight Pipeline
"""
import pandas as pd
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def extract_csv_files(raw_data_path: str) -> Optional[pd.DataFrame]:
    """
    Extract CSV files from the raw data directory
    
    Args:
        raw_data_path: Path to raw data directory
        
    Returns:
        Combined DataFrame from all CSV files
    """
    try:
        logger.info(f"Extracting CSV files from {raw_data_path}")
        
        if not os.path.exists(raw_data_path):
            logger.error(f"Raw data path does not exist: {raw_data_path}")
            return None
        
        # Get all CSV files in the directory
        csv_files = [f for f in os.listdir(raw_data_path) if f.endswith('.csv')]
        
        if not csv_files:
            logger.error(f"No CSV files found in {raw_data_path}")
            return None
        
        # Read and combine all CSV files
        dataframes = []
        for csv_file in csv_files:
            file_path = os.path.join(raw_data_path, csv_file)
            logger.info(f"Reading {csv_file}")
            
            try:
                df = pd.read_csv(file_path)
                dataframes.append(df)
                logger.info(f"Successfully read {csv_file} with {len(df)} rows")
            except Exception as e:
                logger.error(f"Error reading {csv_file}: {e}")
                continue
        
        if not dataframes:
            logger.error("No valid CSV files could be read")
            return None
        
        # Combine all dataframes
        combined_df = pd.concat(dataframes, ignore_index=True)
        logger.info(f"Combined {len(dataframes)} files into {len(combined_df)} total rows")
        
        return combined_df
        
    except Exception as e:
        logger.error(f"Error in CSV extraction: {e}")
        return None

def extract_single_csv(file_path: str) -> Optional[pd.DataFrame]:
    """
    Extract a single CSV file
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame from the CSV file
    """
    try:
        logger.info(f"Extracting single CSV file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return None
        
        df = pd.read_csv(file_path)
        logger.info(f"Successfully read {file_path} with {len(df)} rows")
        
        return df
        
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {e}")
        return None 