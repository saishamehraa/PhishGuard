import os
import csv
import requests
import mysql.connector
from datetime import datetime
from urllib.parse import urlparse
from database import get_database_connection
from logging_system import log_event

DATASET_URL = 'https://openphish.com/feed.txt'
BACKUP_DIR = 'backups'

def fetch_dataset():
    response = requests.get(DATASET_URL)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        raise Exception("Failed to fetch dataset from source.")

def save_backup(dataset):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    filename = os.path.join(BACKUP_DIR, f"phishing_dataset_{timestamp}.csv")
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['url', 'source', 'timestamp'])
        for url in dataset:
            writer.writerow([url, 'OpenPhish', timestamp])
    print(f"📁 Backup saved to {filename}")

def archive_dataset(dataset, conn):
    cursor = conn.cursor()

    # Fetch existing URLs from the archive
    cursor.execute("SELECT url FROM archived_phishing_dataset")
    existing_urls = set(row[0] for row in cursor.fetchall())
    now = datetime.now()

    for url in dataset:
        if url not in existing_urls:
            cursor.execute("""
                INSERT INTO archived_phishing_dataset (url, type, source, first_seen, last_seen)
                VALUES (%s, %s, %s, %s, %s)
            """, (url, 'phishing', 'OpenPhish', now, now))
        else:
            cursor.execute("""
                UPDATE archived_phishing_dataset 
                SET last_seen = %s WHERE url = %s
            """, (now, url))

    conn.commit()
    cursor.close()

def update_phishing_dataset():
    try:
        print("🔄 Starting dataset update...")
        dataset = fetch_dataset()
        if not dataset:
            raise Exception("Empty dataset received")
        
        conn = get_database_connection()
        cursor = conn.cursor()

        # Get current URLs
        cursor.execute("SELECT url FROM phishing_dataset")
        existing_urls = {row[0] for row in cursor.fetchall()}

        new_urls = []
        updated_count = 0

        for url in dataset:
            if url not in existing_urls:
                domain = urlparse(url).netloc
                cursor.execute("""
                    INSERT INTO phishing_dataset 
                    (url, date_added, is_phishing, source, domain)
                    VALUES (%s, NOW(), %s, %s, %s)
                """, (url, 1, 'OpenPhish', domain))
                new_urls.append(url)
                updated_count += 1

        # Mark OpenPhish URLs no longer in feed as safe (but not manual ones!)
        cursor.execute("SELECT url FROM phishing_dataset WHERE source = 'OpenPhish'")
        openphish_urls = set(url for (url,) in cursor.fetchall())

        for url in openphish_urls:
            if url not in dataset:
                cursor.execute("""
                    UPDATE phishing_dataset 
                    SET is_phishing = FALSE 
                    WHERE url = %s
                """, (url,))
                updated_count += 1

        conn.commit()
        cursor.close()

        # Archive and backup
        archive_dataset(dataset, conn)
        save_backup(dataset)

        conn.close()

        log_event("Dataset Update", 
                  f"Added {len(new_urls)} new URLs, updated {updated_count} total",
                  "dataset_manager.py", "Success")

        print(f"✅ Dataset update complete. {len(new_urls)} new URLs added, {updated_count} updated.")

    except Exception as e:
        log_event("Dataset Error", 
                  f"Update failed: {str(e)}", 
                  "dataset_manager.py", "Failed")
        print(f"❌ Dataset update failed: {e}")
        raise
def refresh_dataset():
    update_phishing_dataset()

if __name__ == '__main__':
    update_phishing_dataset()
