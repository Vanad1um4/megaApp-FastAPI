import psycopg2
from env import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )