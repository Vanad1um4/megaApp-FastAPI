import psycopg2

from env import *


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


def get_connection45():
    return psycopg2.connect(
        host=DB_HOST45,
        port=DB_PORT45,
        database=DB_NAME45,
        user=DB_USER45,
        password=DB_PASS45
    )
