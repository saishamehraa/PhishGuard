# auto_refresh.py
from dataset_manager import refresh_dataset
from datetime import datetime
import mysql.connector

# Connect to DB for system logging
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="System123@",
    database="phishguard_db"
)
cursor = db.cursor()

def log_event(event_type, description, source_module, status):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO system_logs (event_type, description, source_module, status, timestamp) VALUES (%s, %s, %s, %s, %s)",
        (event_type, description, source_module, status, timestamp)
    )
    db.commit()

try:
    refresh_dataset()
    log_event("Auto Dataset Refresh", "Phishing dataset auto-refreshed via Task Scheduler.", "auto_refresh.py", "Success")
except Exception as e:
    log_event("Auto Refresh Error", f"Failed to refresh dataset: {str(e)}", "auto_refresh.py", "Failed")
