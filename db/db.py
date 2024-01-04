import psycopg2

from psycopg2.extras import DictCursor

from env import *


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


def dictify_fetchall(cursor: DictCursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictify_fetchone(cursor: DictCursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row is not None:
        return dict(zip(columns, row))
    else:
        return None
