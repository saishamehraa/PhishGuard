from database import get_database_connection
from datetime import datetime

def log_chatbot_message(user_input, bot_response):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chatbot_logs (user_input, bot_response, timestamp)
            VALUES (%s, %s, NOW())
        """, (user_input, bot_response))
        conn.commit()
    except Exception as e:
        print(f"[!] Failed to log chatbot message: {e}")
    finally:
        cursor.close()
        conn.close()

def log_user_url(url, status, confidence):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_urls (url, status, confidence, date_added)
            VALUES (%s, %s, %s, NOW())
        """, (url, status, confidence))
        conn.commit()
    except Exception as e:
        print(f"[!] Failed to log user URL: {e}")
    finally:
        cursor.close()
        conn.close()

def log_analyzed_url(url, result):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analyzed_urls (url, result, analyzed_on)
            VALUES (%s, %s, NOW())
        """, (url, result))
        conn.commit()
    except Exception as e:
        print(f"[!] Failed to log analyzed URL: {e}")
    finally:
        cursor.close()
        conn.close()

def log_user_feedback(user_ip, url, feedback, rating):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_feedback (user_ip, url, feedback, rating, submitted_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (user_ip, url, feedback, rating))
        conn.commit()
    except Exception as e:
        print(f"[!] Failed to log feedback: {e}")
    finally:
        cursor.close()
        conn.close()

def log_model_training(model_name, accuracy, training_duration):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ml_training_logs (model_name, accuracy, training_duration, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (model_name, accuracy, training_duration))
        conn.commit()
    except Exception as e:
        print(f"[!] Failed to log ML training: {e}")
    finally:
        cursor.close()
        conn.close()


