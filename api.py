from fastapi import FastAPI
from ml_model_runner import run_model_on_url

app = FastAPI()

@app.get("/")
def home():
    return {"status": "PhishGuard API is live"}

@app.post("/predict")
def predict(url: str):
    label, confidence = run_model_on_url(url)
    return {
        "prediction": label,
        "confidence": confidence
    }
