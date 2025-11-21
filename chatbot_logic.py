import re
import logging
import random
import socket
from phishing_check import analyze_url, interpret_risk
from feedback_handler import save_feedback
from intent_recognition import classify_intent
from utils import normalize_url
from database import log_chatbot_response, update_feedback_rating
from chatbot_logger import log_chatbot_message, log_user_url, log_analyzed_url

def get_user_ip():
    """Get the local machine's IP address."""
    return socket.gethostbyname(socket.gethostname())

# Logging setup
LOG_FILENAME = "logs/chatbot.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format="%(asctime)s - %(message)s")

def chatbot_response(user_id, user_input, user_ip):
    try:
        user_input = user_input.strip().lower()
        url = extract_url(user_input)

        if url:
            url = normalize_url(url)
            analysis = analyze_url(url)

            if 'status' in analysis and 'confidence' in analysis:
                confidence = analysis['confidence'] if analysis['confidence'] != 'unknown' else None
                log_user_url(url, analysis['status'], confidence)
            else:
                logging.error(f"Missing expected keys in analysis for URL: {url}")
                log_user_url(url, 'unknown', None)
            
            response = generate_analysis_response(analysis)
            log_analyzed_url(url, analysis.get('status', 'unknown'))
            response += "\n\n💬 Was this information helpful? Let us know by typing: 'feedback: your message here, rating: 1 to 5'"

        elif user_input.startswith("feedback:"):
            feedback_text = None
            rating = None

            # Try to extract feedback and rating using regex in one go
            match = re.search(r"feedback\s*:\s*(.*?)(?:,\s*rating\s*:\s*(\d))?$", user_input, re.IGNORECASE)
            if match:
                feedback_text = match.group(1).strip()  # Capture feedback text
                rating_str = match.group(2)  # Capture rating if available
            
                # If rating exists, ensure it's a valid number between 1 and 5
                if rating_str and rating_str.isdigit():
                    rating = int(rating_str)
                    if rating < 1 or rating > 5:
                        rating = None  # Invalid rating, set to None

            # If feedback and rating are both present, save them
            if feedback_text and rating is not None:
                feedback_id = save_feedback(user_ip=user_ip, url=None, feedback=feedback_text, rating=rating)
                response = f"📝 Thanks for your feedback and rating of {rating}! We appreciate it."
            elif feedback_text:  # If only feedback is provided, ask for the rating
                feedback_id = save_feedback(user_ip=user_ip, url=None, feedback=feedback_text, rating=None)
                response = "📝 Thanks for your feedback! Now, please rate the experience from 1 (bad) to 5 (excellent) by typing: rating: [1-5]"
            elif rating is not None:  # If only rating is provided, ask for the feedback
                response = "❗ Please provide your feedback along with the rating."
            else:
                response = "❗ Please provide both your feedback and a rating (1 to 5)."

        else:
            intents = classify_intent(user_input)
            responses = []
            for intent in intents:
                if intent == "greeting":
                    responses.append("Hello! I'm PhishGuard 🛡. Send me a URL to check or ask me about cybersecurity.")
                elif intent == "phishing_check":
                    responses.append("Please provide a valid URL for phishing detection.")
                elif intent == "report_issue":
                    responses.append("You can report an issue by emailing techieiinterns@gmail.com or providing details here.")
                elif intent == "feedback":
                    responses.append("I appreciate your feedback! Let me know what you'd like to improve.")
                elif intent == "cybersecurity_tips":
                    responses.append(get_cybersecurity_tip())
                elif intent == "phishing_definition":
                    responses.append("🎣 *Phishing* is a cyber attack where attackers pretend to be trusted sources to trick you into revealing personal info like passwords or OTPs.\n\nStay sharp. Think before you click. 🧠🔐")
                elif intent == "ssl_info":
                    responses.append("🔐 SSL (Secure Sockets Layer) encrypts your connection to a website. Always look for HTTPS before entering sensitive information.")
                elif intent == "domain_age_info":
                    responses.append("📅 Domain age tells you how long a website has existed. Phishing sites often use newly registered domains.")
                elif intent == "short_url_info":
                    responses.append("🔗 Short URLs (like bit.ly or tinyurl) hide the real destination. Always expand them using an unshortening tool before clicking.")
                elif intent == "goodbye":
                    responses.append("Goodbye! Stay safe online. 🌐🔒")
                elif intent == "unknown":
                    responses.append("I'm not sure I understand. Ask about phishing or submit a URL for analysis.")

            response = "\n\n".join(responses)

        log_chat(user_ip, user_input, response)
        log_chatbot_message(user_input, response)
        return response

    except Exception as e:
        logging.error(f"Error in chatbot_response: {str(e)}")
        return "⚠️ Something went wrong. Please try again later."

def extract_url(text):
    """Improved URL extraction: finds any valid domain or link."""
    match = re.search(r'(https?://)?(www\.)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/\S*)?', text)
    if match:
        url = match.group(0)
        return url if url.startswith("http") else "http://" + url
    return None

def generate_analysis_response(analysis):
    """Formats the phishing analysis result into a user-friendly message."""
    if not analysis or "is_phishing" not in analysis:
        return analysis.get("response", "⚠️ Unable to analyze the URL or unrecognized input.")

    if analysis["is_phishing"]:
        return (
            f"🚨 WARNING! This URL appears to be a phishing site.\n"
            f"🔍 SSL Secure: {analysis.get('is_ssl_secure', 'Unknown')}\n"
            f"📅 Domain Age: {analysis.get('domain_age_days', 'Unknown')} days\n"
            f"⚠ Risk Score: {analysis.get('keyword_risk_score', 'N/A')}"
        )

    return (
        interpret_risk(analysis.get('keyword_risk_score', 0)) + "\n"
        f"🔍 SSL Secure: {analysis.get('is_ssl_secure', 'Unknown')}\n"
        f"📅 Domain Age: {analysis.get('domain_age_days', 'Unknown')} days\n"
        f"⚠ Risk Score: {analysis.get('keyword_risk_score', 'N/A')}"
    )

def get_cybersecurity_tip():
    """Provides a random cybersecurity tip."""
    tips = [
        "🔒 Always check the URL before clicking. Phishing sites mimic real ones!",
        "🛡 Use two-factor authentication (2FA) for extra security.",
        "📧 Don’t open suspicious email attachments or links.",
        "🔍 Hover over links before clicking to see their actual destination.",
        "🛑 If a site asks for sensitive info unexpectedly, verify its authenticity!"
    ]
    return random.choice(tips)

def log_chat(user_ip, user_input, bot_response):
    """Logs chatbot conversation to a file."""
    logging.info(f"User {user_ip}: {user_input} | Chatbot: {bot_response}")

from phishing_check import check_url_with_model

def handle_user_input(url):
    result = check_url_with_model(url)
    return f"The URL is predicted to be: {result.upper()}"