import os
import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn.model_selection import train_test_split

def train_model():
    print("Loading example dataset (Iris)...")
    data = load_iris()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = pd.Series(data.target)

    print("Training model...")
    model = RandomForestClassifier()
    model.fit(X, y)

    print("Saving model...")
    # Create directory if not exists
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/model.pkl")

if __name__ == "__main__":
    train_model()
