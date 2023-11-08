from psycopg2.extras import DictCursor

from schemas import Bank
from db.db import get_connection

connection = get_connection()


def db_get_bank_list_by_userid(user_id: int) -> list[dict[str, int | str]] | None | bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''SELECT id, title
                     FROM bank
                     WHERE user_id=%s
                     ORDER BY title;'''
            values = (user_id,)
            cursor.execute(sql, values)
            res = cursor.fetchall()
        if res:
            column_names = [desc[0] for desc in cursor.description]
            result_list = [dict(zip(column_names, row)) for row in res]
            return result_list
        else:
            return None
    except Exception as exc:
        print(exc)
        return False


def db_add_bank(bank: Bank, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''INSERT INTO bank (title, user_id)
                     VALUES (%s, %s);'''
            values = (bank.title, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_update_bank(bank: Bank, bank_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''UPDATE bank
                     SET title=%s
                     WHERE id=%s AND user_id=%s;'''
            values = (bank.title, bank_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_delete_bank(bank_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''DELETE FROM bank
                     WHERE id=%s AND user_id=%s;'''
            values = (bank_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False
