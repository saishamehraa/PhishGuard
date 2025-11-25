import logging
import requests
import whois
import ssl
import socket
import tldextract
from datetime import datetime
from urllib.parse import urlparse
from database import get_database_connection
from utils import normalize_url
import chatbot_logger
from ml_wrapper import predict_with_ml_script


# Logging Configuration
LOG_FILENAME = "logs/phishing.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Common phishing keywords
PHISHING_KEYWORDS = ["login", "verify", "update", "secure", "account", "banking", "free", "password", "confirm"]

def check_phishing_url(url):
    """
    Checks if the given URL exists in the phishing dataset.
    Returns True (phishing) or False (legitimate).
    """
    conn = get_database_connection()
    if not conn:
        logging.error("❌ Database connection failed! Cannot check URL.")
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT is_phishing FROM phishing_dataset WHERE url = %s", (url,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            is_phishing = bool(result[0])
            logging.info(f"🔍 Checked URL: {url} -> {'Phishing' if is_phishing else 'Legitimate'}")
            return is_phishing
        else:
            logging.info(f"ℹ URL not found in dataset: {url}")
            return False  # Always return False if not found
    except Exception as e:
        logging.error(f"❌ Error checking phishing URL: {e}")
        return None

def interpret_risk(risk_score):
    if risk_score >= 75:
        return "❌ This URL is likely PHISHING. Proceed with extreme caution."
    elif 40 <= risk_score < 75:
        return "⚠️ This URL is SUSPICIOUS. Be cautious."
    elif 1 <= risk_score < 40:
        return "🟡 This URL is somewhat risky. Review before clicking."
    else:
        return "✅ This URL appears to be safe."

def get_domain_age(url):
    try:
        domain = tldextract.extract(url).registered_domain
        if not domain:
            logging.warning(f"⚠ Could not extract domain from URL: {url}")
            return -1

        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date is None:
            logging.warning(f"⚠ No creation date found for domain: {domain}")
            return -1

        # Calculate domain age
        age = (datetime.now() - creation_date).days
        logging.info(f"📅 Domain age of {domain}: {age} days")
        return age
    except Exception as e:
        logging.error(f"❌ Error fetching domain age for {url}: {e}")
        return -1

def check_ssl_certificate(url):
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or parsed_url.path.split('/')[0]

        context = ssl.create_default_context()

        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    logging.info(f"✅ SSL Certificate valid for {hostname}")
                    return True
    except Exception as e:
        logging.warning(f"❌ SSL check failed for {url}: {e}")
        return False

    return False

def keyword_based_detection(url):
    risk_score = 0
    lower_url = url.lower()

    # Skip trusted domains
    trusted_domains = ["google.com", "facebook.com", "twitter.com"]
    if any(trusted_domain in lower_url for trusted_domain in trusted_domains):
        return 0  # Set risk score to 0 for trusted domains

    # Check for phishing keywords
    for keyword in PHISHING_KEYWORDS:
        if keyword in lower_url:
            risk_score += 10

    # Additional content-based checks
    try:
        response = requests.get(url, timeout=5)
        content = response.text.lower()
        for keyword in PHISHING_KEYWORDS:
            if keyword in content:
                risk_score += 5
    except Exception as e:
        logging.warning(f"⚠️ Could not fetch content for keyword scan: {e}")

    return min(risk_score, 100)  # Cap the score to 100

def log_phishing_detection(url, is_phishing):
    """
    Logs phishing checks into the phishing_logs table.
    """
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO phishing_logs (url, is_phishing, date_checked) VALUES (%s, %s, NOW())",
                (url, is_phishing)
            )
            conn.commit()
            cursor.close()
            conn.close()
            logging.info(f"🛑 Phishing check logged: {url} -> {is_phishing}")
        except Exception as e:
            logging.error(f"❌ Error logging phishing detection: {e}")

def analyze_url(url):
    """
    Performs a full phishing analysis on the given URL.
    Returns a dictionary with all checks.
    """
    url = normalize_url(url)
    domain_age = get_domain_age(url)
    is_ssl_secure = check_ssl_certificate(url)
    keyword_risk = keyword_based_detection(url)
    is_phishing = check_phishing_url(url)

    analysis_result = {
        "original_url": url,
        "domain_age_days": domain_age,
        "is_ssl_secure": is_ssl_secure,
        "keyword_risk_score": keyword_risk,
        "is_phishing": is_phishing
    }

    logging.info(
        f"🔍 Analysis result for {url}: Domain Age={domain_age}, "
        f"SSL Secure={is_ssl_secure}, Keyword Risk={keyword_risk}, Is Phishing={is_phishing}"
    )

    # Log the phishing detection result
    log_phishing_detection(url, is_phishing)
    return analysis_result

# Example usage of the phishing analysis
if __name__ == "__main__":
    url = input("Enter a URL to check: ")
    result = analyze_url(url)
    print(f"Phishing Analysis: {result}")

# Call the ML script for prediction
from ml_wrapper import predict_with_ml_script
from database import log_user_url_entry

def check_url_with_model(url):
    result = predict_with_ml_script(url)
    log_user_url_entry(url, result, source="ML_Predictor")
    return result