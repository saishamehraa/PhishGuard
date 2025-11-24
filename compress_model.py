import joblib
from sklearn.tree import DecisionTreeClassifier

model = joblib.load("phishing_model_compressed.pkl")

joblib.dump(model, "phishing_model_compressed.pkl", compress=3)
print("Compression complete → phishing_model_compressed.pkl")
