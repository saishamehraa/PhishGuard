import mysql.connector
from datetime import datetime

def get_db_connection():
    """Returns a new database connection."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="System123@",
        database="phishguard_db"
    )

def save_feedback(user_ip, url, feedback, rating=None):
    """
    Saves user feedback into the database, including the URL and user's IP address.
    :param user_ip: IP address of the user providing feedback.
    :param url: The URL that the feedback pertains to.
    :param feedback: The feedback content.
    :param rating: Optional rating (1-5 scale).
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # SQL query to insert feedback
        query = """
        INSERT INTO user_feedback (user_ip, url, feedback, rating, submitted_at)
        VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (user_ip, url, feedback, rating))
        connection.commit()

        print(f"Feedback saved successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def save_rating(user_ip, rating):
    """
    Updates the rating of the most recent feedback (preferring NULL rating) for the given user.
    Uses subquery with feedback_id to ensure compatibility and reliability.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # First try: update the most recent feedback with NULL rating
        cursor.execute("""
            UPDATE user_feedback 
            SET rating = %s 
            WHERE feedback_id = (
                SELECT feedback_id FROM (
                    SELECT feedback_id FROM user_feedback 
                    WHERE user_ip = %s AND rating IS NULL 
                    ORDER BY submitted_at DESC 
                    LIMIT 1
                ) AS subquery
            )
        """, (rating, user_ip))
        connection.commit()

        if cursor.rowcount == 0:
            # Second try: update the latest feedback regardless of rating
            cursor.execute("""
                UPDATE user_feedback 
                SET rating = %s 
                WHERE feedback_id = (
                    SELECT feedback_id FROM (
                        SELECT feedback_id FROM user_feedback 
                        WHERE user_ip = %s 
                        ORDER BY submitted_at DESC 
                        LIMIT 1
                    ) AS subquery
                )
            """, (rating, user_ip))
            connection.commit()

            if cursor.rowcount == 0:
                return "❌ No recent feedback found to update rating."
            else:
                return f"⚠️ Overwrote existing rating with: {rating} (user: {user_ip})"
        else:
            return f"✅ Rating {rating} saved for user {user_ip}."

    except mysql.connector.Error as err:
        return f"❗ Database error: {err}"

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Example usage
if __name__ == "__main__":
    user_ip = "192.168.1.1"
    url = "http://example.com"
    feedback = "App was smooth, minor bugs but solid overall."

    save_feedback(user_ip=user_ip, url=url, feedback=feedback, rating=None)
    result = save_rating(user_ip=user_ip, rating=3)
    print(result)
