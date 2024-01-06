from psycopg2.extras import DictCursor

from schemas import Currency
from db.db import get_connection

connection = get_connection()


def db_get_currency_list_by_userid(user_id: int) -> list[dict[str, int | str | bool]] | None | bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    id, title, ticker, symbol, symbol_pos, whitespace 
                FROM
                    money_currency
                WHERE
                    user_id=%s
                ORDER BY
                    title;'''
            values = (user_id,)
            cursor.execute(sql, values)
            res = cursor.fetchall()
        if res:
            column_names = [desc[0] for desc in cursor.description]
            result_list = [dict(zip(column_names, row)) for row in res]  # I ❤️ gpt!
            return result_list
        else:
            return None
    except Exception as exc:
        print(exc)
        return False


def db_add_currency(currency: Currency, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                INSERT INTO
                    money_currency (title, ticker, symbol, symbol_pos, whitespace, user_id)
                VALUES
                    (%s, %s, %s, %s, %s, %s);'''
            values = (currency.title, currency.ticker, currency.symbol,
                      currency.symbol_pos, currency.whitespace, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_update_currency(currency: Currency, currency_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                UPDATE
                    money_currency
                SET
                    title=%s, ticker=%s, symbol=%s, symbol_pos=%s, whitespace=%s
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (currency.title, currency.ticker, currency.symbol, currency.symbol_pos, currency.whitespace,
                      currency_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_delete_currency(currency_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                DELETE FROM
                    money_currency
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (currency_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False
