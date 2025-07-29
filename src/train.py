# src/train.py
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_model():
    print("Loading example dataset (Iris)...")
    iris = load_iris(as_frame=True)
    df = iris.frame
    X = df.drop(columns=["target"])
    y = df["target"]

    print("Training model...")
    model = RandomForestClassifier()
    model.fit(X, y)

    print("Saving model...")
    joblib.dump(model, "models/model.pkl")

if __name__ == "__main__":
    train_model()
