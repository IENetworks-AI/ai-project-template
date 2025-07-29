import pandas as pd
import os

def feature_engineer():
    df = pd.read_csv("data/raw/procurement_data.csv")

    # Sample feature creation
    df['amount_log'] = df['amount'].apply(lambda x: 0 if x <= 0 else x).apply(lambda x: x ** 0.5)

    os.makedirs("data/features", exist_ok=True)
    df.to_csv("data/features/features.csv", index=False)

if __name__ == "__main__":
    feature_engineer()
