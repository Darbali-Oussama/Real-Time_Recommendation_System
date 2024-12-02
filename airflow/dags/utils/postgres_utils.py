import psycopg2
import os

POSTGRES_HOST = os.environ.get("POSTGRES_RATING_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_RATING_PORT")
POSTGRES_DB = os.environ.get("POSTGRES_RATING_DB")
POSTGRES_USER = os.environ.get("POSTGRES_RATING_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_RATING_PASSWORD")

def fetch_data_from_postgres():
    connection = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )
    cursor = connection.cursor()

    # Query for new data in the last hour
    query = """
    SELECT id, user_id, book, rating, "timeQuestion" 
    FROM user_rating 
    WHERE "timeQuestion" >= NOW() - INTERVAL '1 HOUR';
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows
