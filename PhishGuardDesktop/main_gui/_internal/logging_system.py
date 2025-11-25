import logging
import os
import mysql.connector
from datetime import datetime

# Ensure logs directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure local logging with daily rotating files
log_filename = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_to_mysql(event_type, description, source_module, status):
    """Logs events to MySQL database."""
    try:
        conn = mysql.connector.connect(
             host="localhost",
        user="root",
        password="System123@",
        database="phishguard_db"
        )
        cursor = conn.cursor()
        query = """
        INSERT INTO system_logs (event_type, description, source_module, status, timestamp)
        VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (event_type, description, source_module, status))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        logging.error(f"Database logging failed: {str(e)}")

def log_event(event_type, description, source_module, status):
    """Logs events both locally and to MySQL."""
    log_message = f"{event_type} - {description} - {source_module} - {status}"
    logging.info(log_message)
    log_to_mysql(event_type, description, source_module, status)

# Example usage
if __name__ == "__main__":
    log_event("INFO", "Logging system initialized", "logging_system.py", "Success")

