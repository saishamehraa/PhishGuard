import re

# Predefined intent keywords
INTENTS = {
     "greeting": ["hello", "hi", "hey", "good morning", "good evening"],
    "phishing_check": ["check this url", "is this safe", "verify this link", "phishing test", "is this a scam","safe?","phishing?"],
    "report_issue": ["report issue", "something is wrong", "error", "bug report"],
    "feedback": ["give feedback", "suggestion", "improvement", "i want to say"],
    "cybersecurity_tips": ["give me a tip", "cybersecurity advice", "how to stay safe", "internet safety"],
    "goodbye": ["bye", "goodbye", "see you", "later","goodnight"],
    "phishing_definition": ["what is phishing", "define phishing", "phishing meaning", "explain phishing","about phishing","phishing"],
    "ssl_info": ["ssl", "secure connection", "is it secure", "https"],
    "domain_age": ["domain age", "how old is this domain", "when was it registered"],
    "short_url": ["short url", "expand url", "shortened link", "unshorten","tinyurl"],
}

def classify_intent(user_input):
    """
    Classifies user input into a predefined intent category.
    Returns an intent string (e.g., "greeting", "phishing_check", etc.).
    """

    detected_intents = []
    user_input = user_input.lower()

    for intent, keywords in INTENTS.items():
        if any(kw in user_input for kw in keywords):
            detected_intents.append(intent)

    return detected_intents or ["unknown"]
