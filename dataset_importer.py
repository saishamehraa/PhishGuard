import requests
import mysql.connector
from datetime import datetime
from urllib.parse import urlparse

# MySQL connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="System123@",
    database="phishguard_db"
)
cursor = db.cursor()

# Logging function to insert into system_logs
def log_event(event_type, description, source_module="OpenPhish_Importer", status="Success"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO system_logs (event_type, description, source_module, status, timestamp) VALUES (%s, %s, %s, %s, %s)",
        (event_type, description, source_module, status, timestamp)
    )
    db.commit()

# Main function to import dataset
def import_dataset():
    try:
        print("🌐 Fetching dataset from OpenPhish...")
        url = "https://openphish.com/feed.txt"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch OpenPhish feed, status code: {response.status_code}")

        urls = response.text.strip().split('\n')
        new_count = 0

        for u in urls:
            cursor.execute("SELECT * FROM phishing_dataset WHERE url = %s", (u,))
            if not cursor.fetchone():
                domain = urlparse(u).netloc
                cursor.execute(
                    """
                    INSERT INTO phishing_dataset 
                    (url, date_added, is_phishing, source, domain) 
                    VALUES (%s, NOW(), %s, %s, %s)
                    """,
                    (u, 1, "OpenPhish", domain)  # ✅ Explicitly set is_phishing = 1
                )
                new_count += 1

        db.commit()
        log_event("Dataset Update", f"{new_count} new phishing URLs added from OpenPhish.")
        print(f"✅ Success: {new_count} new phishing URLs imported.")

    except Exception as e:
        log_event("Error", f"Dataset import failed: {str(e)}", status="Failure")
        print(f"❌ Error during dataset import: {str(e)}")

if __name__ == "__main__":
    import_dataset()