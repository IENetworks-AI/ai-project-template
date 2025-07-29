# src/evaluate.py
import joblib
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score

def evaluate_model():
    iris = load_iris(as_frame=True)
    df = iris.frame
    X = df.drop(columns=["target"])
    y = df["target"]

    model = joblib.load("models/model.pkl")
    y_pred = model.predict(X)
    accuracy = accuracy_score(y, y_pred)
    print(f"Accuracy on Iris dataset: {accuracy:.2f}")

if __name__ == "__main__":
    evaluate_model()
