import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import yaml
from src.utils.logging import get_logger

logger = get_logger('transform_data')

def load_config():
    """Load configuration from config.yaml"""
    with open('config/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def preprocess_data(df):
    """Basic data preprocessing"""
    config = load_config()
    
    # Handle missing values
    df = df.dropna()
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Reset index
    df = df.reset_index(drop=True)
    
    logger.info(f"Preprocessed data: {len(df)} records remaining")
    return df

def engineer_features(df):
    """Feature engineering based on existing logic"""
    config = load_config()
    
    # Handle date columns first
    date_columns = []
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to convert to datetime to identify date columns
            try:
                pd.to_datetime(df[col], errors='raise')
                date_columns.append(col)
            except:
                pass
    
    # Convert date columns to numerical features
    for col in date_columns:
        df[col] = pd.to_datetime(df[col])
        df[f'{col}_year'] = df[col].dt.year
        df[f'{col}_month'] = df[col].dt.month
        df[f'{col}_day'] = df[col].dt.day
        df[f'{col}_dayofweek'] = df[col].dt.dayofweek
        # Drop original date column
        df = df.drop(columns=[col])
    
    # Create numerical features from remaining categorical columns
    categorical_columns = df.select_dtypes(include=['object']).columns
    
    for col in categorical_columns:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
        # Drop original categorical column
        df = df.drop(columns=[col])
    
    # Add interaction features for numerical columns
    numerical_columns = df.select_dtypes(include=[np.number]).columns
    if len(numerical_columns) >= 2:
        for i, col1 in enumerate(numerical_columns):
            for col2 in numerical_columns[i+1:]:
                df[f'{col1}_{col2}_interaction'] = df[col1] * df[col2]
    
    logger.info(f"Feature engineering completed. Total features: {len(df.columns)}")
    return df

def split_data(df, target_column=None):
    """Split data into train/test sets"""
    config = load_config()
    
    if target_column and target_column in df.columns:
        X = df.drop(columns=[target_column])
        y = df[target_column]
        logger.info(f"Using '{target_column}' as target variable")
    else:
        # If no target specified, use last column as target
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
        logger.info(f"No target column specified, using last column '{df.columns[-1]}' as target")
    
    # Ensure X and y are properly aligned
    if len(X) != len(y):
        logger.error(f"X and y have different lengths: X={len(X)}, y={len(y)}")
        raise ValueError("X and y must have the same length")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=config['model']['test_size'],
        random_state=config['model']['random_state']
    )
    
    logger.info(f"Data split: Train={len(X_train)}, Test={len(X_test)}")
    logger.info(f"X shape: {X.shape}, y shape: {y.shape}")
    return X_train, X_test, y_train, y_test

def scale_features(X_train, X_test):
    """Scale numerical features"""
    # Ensure we only scale numerical columns
    numerical_columns = X_train.select_dtypes(include=[np.number]).columns
    
    if len(numerical_columns) == 0:
        logger.warning("No numerical columns found for scaling")
        return X_train, X_test, None
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train[numerical_columns])
    X_test_scaled = scaler.transform(X_test[numerical_columns])
    
    # Convert back to DataFrame with column names
    X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=numerical_columns, index=X_train.index)
    X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=numerical_columns, index=X_test.index)
    
    logger.info(f"Features scaled successfully. Scaled {len(numerical_columns)} numerical columns")
    return X_train_scaled_df, X_test_scaled_df, scaler

def transform_data(df, target_column=None):
    """Main transformation pipeline"""
    logger.info("Starting data transformation pipeline")
    
    # Preprocess
    df = preprocess_data(df)
    
    # Feature engineering
    df = engineer_features(df)
    
    # Split data
    X_train, X_test, y_train, y_test = split_data(df, target_column)
    
    # Scale features
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'X_train_scaled': X_train_scaled,
        'X_test_scaled': X_test_scaled,
        'scaler': scaler,
        'feature_names': X_train.columns.tolist()
    } 