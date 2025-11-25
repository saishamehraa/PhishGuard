# ml_wrapper.py

import subprocess
from ml_model_runner import run_model_on_url

def predict_with_ml_script(url):
    try:
        label, confidence = run_model_on_url(url)
        return "phishing" if "phishing" in label.lower() else "legitimate"
    except Exception as e:
        print(f"[Error] ML Prediction failed: {e}")
        return "error"
