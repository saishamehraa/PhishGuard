import logging
import os
import mysql.connector
from datetime import datetime
from decimal import Decimal
from ml_model_runner import extract_features_from_url

# ------------------------------ Setup & Configuration ------------------------------ #

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Logging setup
LOG_FILENAME = os.path.join(LOG_DIR, "database.log")
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("📦 Database module initialized.")

# MySQL database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "System123@",
    "database": "phishguard_db"
}

def get_database_connection():
    """Establish and return a new database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logging.info("✅ Database connection established.")
        return conn
    except mysql.connector.Error as e:
        logging.error(f"❌ Database connection failed: {str(e)}")
        return None

# ------------------------------ System Logs ------------------------------ #

def log_system_event(event_type, description, status):
    """Insert system event into system_logs table."""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs (event_type, description, status)
                VALUES (%s, %s, %s)
            """, (event_type, description, status))
            conn.commit()
            logging.info(f"📌 System log saved: {event_type} - {description} - {status}")
        except Exception as e:
            logging.error(f"❌ Failed to log system event: {str(e)}")
        finally:
            cursor.close()
            conn.close()

# ------------------------------ Feedback Management ------------------------------ #

def save_user_feedback(user_ip, feedback, rating, url=None):
    """Save user feedback to user_feedback table."""
    rating = rating if isinstance(rating, int) and 1 <= rating <= 5 else None
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_feedback (user_ip, feedback, rating, url)
                VALUES (%s, %s, %s, %s)
            """, (user_ip, feedback, rating, url))
            conn.commit()
            logging.info(f"✅ Feedback saved for IP {user_ip}, Rating: {rating}")
        except mysql.connector.Error as e:
            logging.error(f"❌ Error saving feedback: {str(e)}")
        finally:
            cursor.close()
            conn.close()

def update_feedback_rating(user_ip, rating):
    """Update rating for latest feedback where rating is missing."""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_feedback
                SET rating = %s
                WHERE user_ip = %s AND rating IS NULL
                ORDER BY submitted_at DESC
                LIMIT 1
            """, (rating, user_ip))
            conn.commit()
            logging.info(f"⭐️ Rating updated for {user_ip}: {rating}")
        except mysql.connector.Error as e:
            logging.error(f"❌ Error updating feedback: {str(e)}")
        finally:
            cursor.close()
            conn.close()

def update_feedback_by_id(feedback_id, rating):
    """Update feedback rating by specific feedback ID."""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_feedback
                SET rating = %s
                WHERE feedback_id = %s
            """, (rating, feedback_id))
            conn.commit()
            logging.info(f"🔧 Feedback ID {feedback_id} rating set to {rating}")
        except mysql.connector.Error as e:
            logging.error(f"❌ Error updating feedback by ID: {str(e)}")
        finally:
            cursor.close()
            conn.close()

# ------------------------------ Phishing Dataset ------------------------------ #

def add_phishing_dataset_entry(url, is_phishing):
    """Add a new phishing dataset entry."""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO phishing_dataset (url, date_added, is_phishing)
                VALUES (%s, NOW(), %s)
            """, (url, is_phishing))
            conn.commit()
            logging.info(f"✅ Phishing dataset updated: {url} -> {is_phishing}")
        except mysql.connector.Error as e:
            logging.error(f"❌ Error inserting phishing dataset: {str(e)}")
        finally:
            cursor.close()
            conn.close()

def get_all_phishing_urls():
    """Get list of phishing URLs."""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM phishing_dataset WHERE is_phishing = 1")
            urls = [row[0] for row in cursor.fetchall()]
            logging.info(f"🔍 Retrieved {len(urls)} phishing URLs.")
            return urls
        except mysql.connector.Error as e:
            logging.error(f"❌ Error fetching phishing URLs: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    return []

# ------------------------------ Chatbot Logs ------------------------------ #

def log_chatbot_response(user_query, bot_response):
    """Store chatbot interaction in chatbot_logs."""
    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chatbot_logs (user_query, bot_response)
                VALUES (%s, %s)
            """, (user_query, bot_response))
            conn.commit()
            logging.info(f"💬 Chatbot log saved: {user_query} => {bot_response}")
        except mysql.connector.Error as e:
            logging.error(f"❌ Failed to log chatbot interaction: {str(e)}")
        finally:
            cursor.close()
            conn.close()

# ------------------------------ User URL Logs ------------------------------ #

def log_user_url_entry(url, status, confidence):
    """Log user-submitted URLs with status & confidence score."""
    #status = status or "unknown"
     # Fetch model predictions and confidence from preprocessing.py
    status, confidence = extract_features_from_url(url)
    try:
        confidence = float(confidence) if confidence is not None else 0.0
    except (ValueError, TypeError):
        confidence = 0.0

    conn = get_database_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_urls (url, status, confidence, date_added)
                VALUES (%s, %s, %s, NOW())
            """, (url, status, confidence))
            conn.commit()
            logging.info(f"📦 URL logged: {url} | Status: {status} | Confidence: {confidence}")
        except mysql.connector.Error as e:
            logging.error(f"❌ URL log failed: {str(e)}")
        finally:
            cursor.close()
            conn.close()
