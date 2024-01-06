from psycopg2.extras import DictCursor

from schemas import Transaction
from db.db import get_connection
from env import FETCH_DAYS_RANGE_OFFSET

connection = get_connection()


def db_get_transaction_list_by_user_id(user_id: int, date_iso: str) -> list[dict[str, int | str]] | None | bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT 
                    id, date, amount, account_id, category_id, kind, is_gift, notes, twin_transaction_id
                FROM 
                    money_transaction
                WHERE 
                    user_id = %s
                    AND date BETWEEN date %s - %s AND date %s + %s 
                ORDER BY 
                    id;'''
            values = (user_id, date_iso, FETCH_DAYS_RANGE_OFFSET, date_iso, FETCH_DAYS_RANGE_OFFSET)
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


def db_add_one_transaction(transaction: Transaction, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            amount_signed = transaction.amount if transaction.kind == 'income' else -transaction.amount
            sql = '''
                INSERT INTO
                    money_transaction (date, amount, account_id, category_id, kind, is_gift, notes, user_id)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s);'''
            values = (transaction.date, amount_signed, transaction.account_id, transaction.category_id,
                      transaction.kind, transaction.is_gift, transaction.notes, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_add_two_transactions(transaction: Transaction, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            # Making two linked transactions:
            # Adding the first transaction with a negative amount value and getting its id
            sql = '''
                INSERT INTO
                    money_transaction (date, amount, account_id, category_id, kind, is_gift, notes, user_id)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING
                    id;'''
            values = (transaction.date, -transaction.amount, transaction.account_id, transaction.category_id,
                      transaction.kind, False, transaction.notes, user_id)
            cursor.execute(sql, values)
            id1 = cursor.fetchone()[0]

            # Adding the second transaction, using target_account_id and target_account_amount and the id of the first transaction
            sql = '''
                INSERT INTO
                    money_transaction (date, amount, account_id, category_id, kind, is_gift, notes, user_id, twin_transaction_id)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING
                    id;'''
            values = (transaction.date, transaction.target_account_amount, transaction.target_account_id,
                      transaction.category_id, transaction.kind, False, transaction.notes, user_id, id1)
            cursor.execute(sql, values)
            id2 = cursor.fetchone()[0]

            # Updating the first transaction with the id of the second transaction
            sql = '''
                UPDATE
                    money_transaction
                SET
                    twin_transaction_id = %s
                WHERE
                    id = %s;'''
            values = (id2, id1)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_update_one_transaction(transaction: Transaction, transaction_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            amount_signed = transaction.amount if transaction.kind == 'income' else -transaction.amount
            sql = '''
                UPDATE 
                    money_transaction 
                SET
                    amount=%s, account_id=%s, category_id=%s, kind=%s, is_gift=%s, notes=%s
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (amount_signed, transaction.account_id, transaction.category_id,
                      transaction.kind, transaction.is_gift, transaction.notes, transaction_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_update_two_transactions(transaction: Transaction, transaction_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            # Обновление первой транзакции с отрицательным значением суммы
            sql = '''
                UPDATE 
                    money_transaction 
                SET
                    amount=%s, account_id=%s, category_id=%s, notes=%s
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (-transaction.amount, transaction.account_id,
                      transaction.category_id, transaction.notes, transaction_id, user_id)
            cursor.execute(sql, values)

            # Обновление второй транзакции, используя target_account_id и target_account_amount
            sql = '''
                UPDATE 
                    money_transaction 
                SET
                    amount=%s, account_id=%s, category_id=%s, notes=%s
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (transaction.target_account_amount, transaction.target_account_id,
                      transaction.category_id, transaction.notes, transaction.twin_transaction_id, user_id)
            cursor.execute(sql, values)

            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_delete_transaction(transaction_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            # Получение twin_transaction_id для данной транзакции
            sql = '''
                SELECT
                    twin_transaction_id
                FROM
                    money_transaction
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (transaction_id, user_id)
            cursor.execute(sql, values)
            twin_transaction_id = cursor.fetchone()[0]

            # Если twin_transaction_id не равно Null, удаление связанной транзакции
            if twin_transaction_id is not None:
                sql = '''
                    DELETE FROM
                        money_transaction
                    WHERE
                        id=%s
                        AND user_id=%s;'''
                values = (twin_transaction_id, user_id)
                cursor.execute(sql, values)

            # Удаление исходной транзакции
            sql = '''
                DELETE FROM
                    money_transaction
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (transaction_id, user_id)
            cursor.execute(sql, values)

            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False
