from psycopg2.extras import DictCursor

from db.db import get_connection

connection = get_connection()


def db_create_user(user_email, hashed_password):
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                INSERT INTO
                    "user" (email, hashed_password)
                VALUES
                    (%s, %s);'''
            values = (user_email, hashed_password)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_get_user_id_by_email(user_email):
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    id
                FROM
                    "user"
                WHERE
                    email=%s;'''
            values = (user_email,)
            cursor.execute(sql, values)
            res = cursor.fetchone()[0]
            return res
    except Exception as exc:
        print(exc)
        return False


def db_get_a_user_by_email(user_email):
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    *
                FROM
                    "user"
                WHERE
                    email=%s;'''
            values = (user_email,)
            cursor.execute(sql, values)
            res = cursor.fetchone()
            return dict(res) if res else None
    except Exception as exc:
        print(exc)
        return False
