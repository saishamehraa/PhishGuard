from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

# Load your phishing model
model = joblib.load("phishing_model.pkl")
scaler = joblib.load("scaler.pkl")

@app.get("/")
def home():
    return {"status": "PhishGuard API is live"}

@app.post("/predict")
def predict(url: str):
    # TODO: run your extraction logic here
    # For now, just return placeholder
    return {"prediction": "safe or phishing"}
    # features = extract_features(url)