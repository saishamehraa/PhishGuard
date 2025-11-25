import re
import math
import joblib
from urllib.parse import urlparse
from collections import Counter
import pandas as pd
import sys,os

# === Load model and scaler only once ===
#model = joblib.load("phishing_model_compressed.pkl")
#scaler = joblib.load("scaler.pkl")
def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

def shannon_entropy(string):
    prob = [n_x / len(string) for x, n_x in Counter(string).items()]
    entropy = -sum([p * math.log2(p) for p in prob])
    return entropy

def extract_features_from_url(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path
    query = parsed.query
    fragment = parsed.fragment

    subdomains = domain.split('.')[:-2] if len(domain.split('.')) > 2 else []
    subdomain_str = '.'.join(subdomains)

    features = {
        "url_length": len(url),
        "number_of_dots_in_url": url.count('.'),
        "having_repeated_digits_in_url": int(any(url.count(d) > 1 for d in '0123456789')),
        "number_of_digits_in_url": sum(c.isdigit() for c in url),
        "number_of_special_char_in_url": len(re.findall(r"[^a-zA-Z0-9]", url)),
        "number_of_hyphens_in_url": url.count('-'),
        "number_of_underline_in_url": url.count('_'),
        "number_of_slash_in_url": url.count('/'),
        "number_of_questionmark_in_url": url.count('?'),
        "number_of_equal_in_url": url.count('='),
        "number_of_at_in_url": url.count('@'),
        "number_of_dollar_in_url": url.count('$'),
        "number_of_exclamation_in_url": url.count('!'),
        "number_of_hashtag_in_url": url.count('#'),
        "number_of_percent_in_url": url.count('%'),
        "domain_length": len(domain),
        "number_of_dots_in_domain": domain.count('.'),
        "number_of_hyphens_in_domain": domain.count('-'),
        "having_special_characters_in_domain": int(bool(re.search(r"[^a-zA-Z0-9.-]", domain))),
        "number_of_special_characters_in_domain": len(re.findall(r"[^a-zA-Z0-9]", domain)),
        "having_digits_in_domain": int(any(char.isdigit() for char in domain)),
        "number_of_digits_in_domain": sum(char.isdigit() for char in domain),
        "having_repeated_digits_in_domain": int(any(domain.count(d) > 1 for d in '0123456789')),
        "number_of_subdomains": len(subdomains),
        "having_dot_in_subdomain": int('.' in subdomain_str),
        "having_hyphen_in_subdomain": int('-' in subdomain_str),
        "average_subdomain_length": len(subdomain_str) / len(subdomains) if subdomains else 0,
        "average_number_of_dots_in_subdomain": sum(sd.count('.') for sd in subdomains) / len(subdomains) if subdomains else 0,
        "average_number_of_hyphens_in_subdomain": sum(sd.count('-') for sd in subdomains) / len(subdomains) if subdomains else 0,
        "having_special_characters_in_subdomain": int(bool(re.search(r"[^a-zA-Z0-9.-]", subdomain_str))),
        "number_of_special_characters_in_subdomain": len(re.findall(r"[^a-zA-Z0-9]", subdomain_str)),
        "having_digits_in_subdomain": int(any(char.isdigit() for char in subdomain_str)),
        "number_of_digits_in_subdomain": sum(char.isdigit() for char in subdomain_str),
        "having_repeated_digits_in_subdomain": int(any(subdomain_str.count(d) > 1 for d in '0123456789')),
        "having_path": int(bool(path)),
        "path_length": len(path),
        "having_query": int(bool(query)),
        "having_fragment": int(bool(fragment)),
        "having_anchor": int('#' in url),
        "entropy_of_url": shannon_entropy(url),
        "entropy_of_domain": shannon_entropy(domain),
    }

    return list(features.values())

def run_model_on_url(url):
    features = extract_features_from_url(url)

    feature_names = [  # all 42 features
        "url_length", "number_of_dots_in_url", "having_repeated_digits_in_url", "number_of_digits_in_url", 
        "number_of_special_char_in_url", "number_of_hyphens_in_url", "number_of_underline_in_url", 
        "number_of_slash_in_url", "number_of_questionmark_in_url", "number_of_equal_in_url", 
        "number_of_at_in_url", "number_of_dollar_in_url", "number_of_exclamation_in_url", 
        "number_of_hashtag_in_url", "number_of_percent_in_url", "domain_length", "number_of_dots_in_domain", 
        "number_of_hyphens_in_domain", "having_special_characters_in_domain", "number_of_special_characters_in_domain", 
        "having_digits_in_domain", "number_of_digits_in_domain", "having_repeated_digits_in_domain", 
        "number_of_subdomains", "having_dot_in_subdomain", "having_hyphen_in_subdomain", 
        "average_subdomain_length", "average_number_of_dots_in_subdomain", "average_number_of_hyphens_in_subdomain", 
        "having_special_characters_in_subdomain", "number_of_special_characters_in_subdomain", 
        "having_digits_in_subdomain", "number_of_digits_in_subdomain", "having_repeated_digits_in_subdomain", 
        "having_path", "path_length", "having_query", "having_fragment", "having_anchor", 
        "entropy_of_url", "entropy_of_domain"
    ]

    df = pd.DataFrame([features], columns=feature_names)
    scaled = scaler.transform(df)

    prediction = model.predict(scaled)[0]
    probability = model.predict_proba(scaled)[0][prediction]

    label = "Phishing" if prediction == 1 else "Legitimate"
    return label, round(probability * 100, 2)

# Only runs if this file is run directly
if __name__ == "__main__":
    url = input("🌐 Enter a URL to check: ")
    label, confidence = run_model_on_url(url)
    print(f"📊 Prediction: {label}")
    print(f"📈 Confidence: {confidence}%")
