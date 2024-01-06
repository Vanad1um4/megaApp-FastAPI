from psycopg2.extras import DictCursor

from db.db import get_connection

connection = get_connection()


def db_create_user(username, hashed_password):
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                INSERT INTO
                    users (username, hashed_password)
                VALUES
                    (%s, %s);'''
            values = (username, hashed_password)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_get_user_id_by_username(username):
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    id
                FROM
                    users
                WHERE
                    username=%s;'''
            values = (username,)
            cursor.execute(sql, values)
            res = cursor.fetchone()
            return res
    except Exception as exc:
        print(exc)
        return False


def db_get_a_user_by_username(username):
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    *
                FROM
                    users
                WHERE
                    username=%s;'''
            values = (username,)
            cursor.execute(sql, values)
            res = cursor.fetchone()
            return dict(res) if res else None
    except Exception as exc:
        print(exc)
        return False
