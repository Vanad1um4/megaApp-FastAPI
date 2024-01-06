from psycopg2.extras import DictCursor

from schemas import Account
from db.db import get_connection

connection = get_connection()


def db_get_account_list_by_userid(user_id: int) -> list[dict[str, int | str | bool]] | None | bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    id, title, currency_id, bank_id, invest, kind
                FROM
                    money_account
                WHERE
                    user_id = %s
                ORDER BY
                    title;'''
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


def db_add_account(account: Account, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                INSERT INTO
                    money_account (title, currency_id, bank_id, invest, kind, user_id)
                VALUES
                    (%s, %s, %s, %s, %s, %s);'''
            values = (account.title, account.currency_id, account.bank_id,
                      account.invest, account.kind, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_update_account(account: Account, account_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                UPDATE
                    money_account
                SET
                    title=%s, currency_id=%s, bank_id=%s, invest=%s, kind=%s
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (account.title, account.currency_id, account.bank_id,
                      account.invest, account.kind, account_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_delete_account(account_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                DELETE FROM
                    money_account
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (account_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False
