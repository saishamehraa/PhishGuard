import re
import tldextract
import whois
import requests
import datetime

def extract_features(url):
    """Extracts features from a URL for ML model input."""
    
    # URL-based Features
    url_length = len(url)
    num_hyphens = url.count('-')
    num_at_symbols = url.count('@')
    num_dots = url.count('.')
    
    # Domain Features
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    
    # Check HTTPS
    https = 1 if url.startswith("https") else 0
    
    # WHOIS Information (Domain Age)
    try:
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        domain_age_days = (datetime.datetime.now() - creation_date).days if creation_date else -1
    except:
        domain_age_days = -1  # Whois query failed
    
    # Keyword-based Features
    phishing_keywords = ["secure", "account", "banking", "login", "verify", "password"]
    keyword_count = sum([1 for word in phishing_keywords if word in url.lower()])
    
    # Return Features as Dictionary
    return {
        "url_length": url_length,
        "num_hyphens": num_hyphens,
        "num_at_symbols": num_at_symbols,
        "num_dots": num_dots,
        "https": https,
        "domain_age_days": domain_age_days,
        "keyword_count": keyword_count
    }
