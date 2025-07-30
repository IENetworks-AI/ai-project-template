"""
Sales Data Transformation for Retail Sales Insight Pipeline
"""
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def clean_and_aggregate_sales(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Clean and aggregate sales data to compute top categories
    
    Args:
        df: Raw sales DataFrame
        
    Returns:
        Aggregated sales data with top categories
    """
    try:
        logger.info("Starting sales data transformation")
        
        # Check required columns
        required_columns = ['Product Category', 'Total Amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return None
        
        # Clean the data
        logger.info("Cleaning sales data")
        
        # Remove rows with missing values in key columns
        df_clean = df.dropna(subset=['Product Category', 'Total Amount'])
        logger.info(f"Removed {len(df) - len(df_clean)} rows with missing values")
        
        # Convert Total Amount to numeric, handling any non-numeric values
        df_clean['Total Amount'] = pd.to_numeric(df_clean['Total Amount'], errors='coerce')
        df_clean = df_clean.dropna(subset=['Total Amount'])
        logger.info(f"Cleaned Total Amount column, {len(df_clean)} rows remaining")
        
        # Aggregate by Product Category
        logger.info("Aggregating sales by category")
        aggregated_sales = df_clean.groupby('Product Category')['Total Amount'].agg([
            'sum', 'count', 'mean'
        ]).reset_index()
        
        # Rename columns for clarity
        aggregated_sales.columns = ['category', 'total_sales', 'transaction_count', 'avg_transaction']
        
        # Sort by total sales (descending)
        aggregated_sales = aggregated_sales.sort_values('total_sales', ascending=False)
        
        logger.info(f"Aggregation complete. Found {len(aggregated_sales)} categories")
        logger.info(f"Top category: {aggregated_sales.iloc[0]['category']} with ${aggregated_sales.iloc[0]['total_sales']:,.2f}")
        
        return aggregated_sales
        
    except Exception as e:
        logger.error(f"Error in sales transformation: {e}")
        return None

def get_top_categories(agg_df: pd.DataFrame, threshold: float = 1000, limit: int = 5) -> dict:
    """
    Get top performing categories based on sales threshold
    
    Args:
        agg_df: Aggregated sales DataFrame
        threshold: Minimum sales amount to be considered "top"
        limit: Maximum number of categories to return
        
    Returns:
        Dictionary with top categories and their metrics
    """
    try:
        logger.info(f"Identifying top categories with threshold ${threshold:,.2f}")
        
        # Filter categories above threshold
        top_categories = agg_df[agg_df['total_sales'] >= threshold].head(limit)
        
        if top_categories.empty:
            logger.warning(f"No categories found above threshold ${threshold:,.2f}")
            return {
                'top_categories': [],
                'total_categories': len(agg_df),
                'threshold': threshold,
                'message': f"No categories found above ${threshold:,.2f}"
            }
        
        # Prepare response
        categories_data = []
        for _, row in top_categories.iterrows():
            categories_data.append({
                'category': row['category'],
                'total_sales': float(row['total_sales']),
                'transaction_count': int(row['transaction_count']),
                'avg_transaction': float(row['avg_transaction'])
            })
        
        result = {
            'top_categories': categories_data,
            'total_categories': len(agg_df),
            'categories_above_threshold': len(top_categories),
            'threshold': threshold,
            'total_sales': float(agg_df['total_sales'].sum()),
            'message': f"Found {len(top_categories)} categories above ${threshold:,.2f}"
        }
        
        logger.info(f"Identified {len(top_categories)} top categories")
        return result
        
    except Exception as e:
        logger.error(f"Error getting top categories: {e}")
        return {
            'top_categories': [],
            'error': str(e)
        } 