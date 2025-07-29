import pandas as pd
import joblib
from sklearn.metrics import mean_absolute_error
import os

def evaluate_model():
    df = pd.read_csv("data/features/features.csv")
    model = joblib.load("models/model.pkl")
    
    X = df[['amount_log']]
    y = df['amount']

    preds = model.predict(X)
    mae = mean_absolute_error(y, preds)
    print(f"MAE: {mae:.2f}")

if __name__ == "__main__":
    evaluate_model()
