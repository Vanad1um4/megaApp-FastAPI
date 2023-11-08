from psycopg2.extras import DictCursor

from schemas import Transaction
from db.db import get_connection

connection = get_connection()


def db_get_transaction_list_by_user_id(user_id: int) -> list[dict[str, int | str]] | None | bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''SELECT id, date, amount, account_id, category_id, kind
                     FROM transaction
                     WHERE user_id=%s
                     ORDER BY id;'''
            values = (user_id,)
            cursor.execute(sql, values)
            res = cursor.fetchall()
        if res:
            column_names = [desc[0] for desc in cursor.description]
            result_list = [dict(zip(column_names, row)) for row in res]
            return result_list
        else:
            return []
    except Exception as exc:
        print(exc)
        return False


def db_add_transaction(transaction: Transaction, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''INSERT INTO transaction (date, amount, account_id, category_id, kind, user_id)
                     VALUES (%s, %s, %s, %s, %s, %s);'''
            values = (transaction.date, transaction.amount, transaction.account_id,
                      transaction.category_id, transaction.kind, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_update_transaction(transaction: Transaction, transaction_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''UPDATE transaction 
                     SET date=%s, amount=%s, account_id=%s, category_id=%s, kind=%s
                     WHERE id=%s AND user_id=%s;'''
            values = (transaction.date, transaction.amount, transaction.account_id, transaction.category_id, transaction.kind,
                      transaction_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_delete_transaction(transaction_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''DELETE FROM transaction
                     WHERE id=%s AND user_id=%s;'''
            values = (transaction_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False
