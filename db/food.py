from datetime import datetime, timedelta, date
from psycopg2.extras import DictCursor

from db.db import get_connection, dictify_fetchall, dictify_fetchone
from utils.utils import stopwatch


connection = get_connection()


### DIARY #############################################################################################################

def db_get_all_users_diary_entries(user_id):
    try:
        with connection.cursor() as c:
            sql = '''
                SELECT
                    date, food_catalogue_id, food_weight
                FROM
                    food_diary
                WHERE
                    user_id=%s
                ORDER BY
                    date;'''
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchall()
        return res
    except Exception as exc:
        print(exc)
        return False


def db_get_range_of_users_diary_entries(date_iso_start: str, date_iso_end: str, user_id: int) -> list[dict[str, int | date | float]] | None | bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT 
                    id, date, food_catalogue_id, food_weight
                FROM
                    food_diary
                WHERE
                    user_id=%s
                    AND date BETWEEN date %s AND date %s 
                ORDER BY
                    date ASC, id ASC;'''
            values = (user_id, date_iso_start, date_iso_end)
            cursor.execute(sql, values)
            res = dictify_fetchall(cursor)
        return res
    except Exception as exc:
        print(exc)
        return False


def db_add_diary_entry(date_iso: str, food_catalogue_id: int, food_weight: int, user_id: int):
    try:
        with connection.cursor() as cursor:
            sql = '''
                INSERT INTO 
                    food_diary (date, food_catalogue_id, food_weight, user_id)
                VALUES
                    (%s, %s, %s, %s)
                RETURNING
                    id;'''
            values = (date_iso, food_catalogue_id, food_weight, user_id)
            cursor.execute(sql, values)
            id = cursor.fetchone()
            connection.commit()
        return id
    except Exception as exc:
        print(exc)
        return False


def db_edit_diary_entry(food_weight: int, diary_id: int, user_id: int):
    try:
        with connection.cursor() as cursor:
            sql = '''
                UPDATE 
                    food_diary 
                SET
                    food_weight=%s
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (food_weight, diary_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
        return True
    except Exception as exc:
        print(exc)
        return False


def db_delete_diary_entry(diary_id: int, user_id: int):
    try:
        with connection.cursor() as cursor:
            sql = '''
                DELETE FROM
                    food_diary
                WHERE
                    id=%s
                    AND user_id=%s;'''
            values = (diary_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
        return True
    except Exception as exc:
        print(exc)
        return False


### WEIGHTS ###########################################################################################################

def db_get_all_users_body_weights(user_id):
    try:
        with connection.cursor() as c:
            sql = '''
                SELECT
                    date, weight
                FROM
                    food_body_weight
                WHERE
                    user_id=%s
                ORDER BY
                    date;'''
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchall()
        return res
    except Exception as exc:
        print(exc)
        return False


def db_get_range_of_users_body_weights(date_iso_start: str, date_iso_end: str, user_id: int):
    try:
        with connection.cursor() as cursor:
            sql = '''
                SELECT
                    date, weight
                FROM
                    food_body_weight
                WHERE
                    user_id=%s
                    AND date BETWEEN date %s AND date %s 
                ORDER BY
                    date;'''
            values = (user_id, date_iso_start, date_iso_end)
            cursor.execute(sql, values)
            res = cursor.fetchall()
        return res
    except Exception as exc:
        print(exc)
        return False


def db_get_a_single_users_body_weight(date_iso: str, user_id: int):
    try:
        with connection.cursor() as cursor:
            sql = '''
                SELECT
                    weight
                FROM
                    food_body_weight
                WHERE
                    user_id=%s
                    AND date=%s;'''
            values = (user_id, date_iso)
            cursor.execute(sql, values)
            res = cursor.fetchone()
        return res
    except Exception as exc:
        print(exc)
        return False


def db_save_users_body_weight(date_iso: str, weight: float, user_id: int):
    try:
        with connection.cursor() as cursor:
            res0 = db_get_a_single_users_body_weight(date_iso, user_id)
            if not res0:
                sql = '''
                    INSERT INTO
                        food_body_weight (weight, user_id, date)
                    VALUES
                        (%s, %s, %s);'''
            else:
                sql = '''
                    UPDATE
                        food_body_weight
                    SET
                        weight=%s
                    WHERE
                        user_id=%s
                        AND date=%s;'''
            values = (weight, user_id, date_iso)
            cursor.execute(sql, values)
            connection.commit()
        return True
    except Exception as exc:
        print(exc)
        return False


### COEFFICIENTS ######################################################################################################

def db_get_use_coeffs_bool(user_id):
    try:
        with connection.cursor() as cursor:
            sql = '''
                SELECT 
                    use_coeffs
                FROM
                    food_settings
                WHERE
                    user_id=%s;'''
            values = (user_id,)
            cursor.execute(sql, values)
            res = cursor.fetchone()
        return res
    except Exception as exc:
        print(exc)
        return False


def db_get_users_coefficients(user_id: int) -> tuple[str, list]:
    try:
        with connection.cursor() as cursor:
            sql = '''
                SELECT
                    coefficients
                FROM
                    food_settings
                WHERE
                    user_id=%s;'''
            values = (user_id,)
            cursor.execute(sql, values)
            res = cursor.fetchone()
        return res
    except Exception as exc:
        print(exc)
        return False


def db_set_users_coefficients(user_id: int, user_coeffs: str) -> tuple[str, list]:
    try:
        with connection.cursor() as cursor:
            sql = '''
                UPDATE
                    food_settings
                SET
                    coefficients=%s
                WHERE
                    user_id=%s;'''
            values = (user_coeffs, user_id)
            cursor.execute(sql, values)
        return True
    except Exception as exc:
        print(exc)
        return False


### STATS ######################################################################################################

def db_get_users_cached_stats(user_id: int):
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    up_to_date, stats
                FROM
                    food_stats
                WHERE
                    user_id=%s;'''
            values = (user_id,)
            cursor.execute(sql, values)
            res = dictify_fetchone(cursor)
        return res
    except Exception as exc:
        print(exc)
        return False


def db_save_users_stats(date_iso: str, stats: str, user_id: int):
    try:
        with connection.cursor() as cursor:
            res0 = db_get_users_cached_stats(user_id)
            if not res0:
                sql = '''
                    INSERT INTO
                        food_stats (up_to_date, stats, user_id)
                    VALUES
                        (%s, %s, %s);'''
            else:
                sql = '''
                    UPDATE
                        food_stats
                    SET
                        up_to_date=%s, stats=%s
                    WHERE
                        user_id=%s;'''
            values = (date_iso, stats, user_id,)
            cursor.execute(sql, values)
            connection.commit()
        return True
    except Exception as exc:
        print(exc)
        return False


### CATALOGUE #########################################################################################################

def db_get_all_catalogue_entries() -> tuple[str, list]:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    id, name, kcals
                FROM
                    food_catalogue
                ORDER BY
                    name ASC;'''
            cursor.execute(sql,)
            res = dictify_fetchall(cursor)
        return res
    except Exception as exc:
        print(exc)
        return False


def db_add_new_catalogue_entry(food_name: str, food_kcals: int):
    try:
        with connection.cursor() as cursor:
            sql = '''
                INSERT INTO
                    food_catalogue (name, kcals)
                VALUES
                    (%s, %s)
                RETURNING
                    id;'''
            values = (food_name, food_kcals)
            cursor.execute(sql, values)
            id = cursor.fetchone()
            connection.commit()
        return id
    except Exception as exc:
        print(exc)
        return False


def db_update_catalogue_entry(food_id: int, food_name: str, food_kcals: int) -> bool:
    try:
        with connection.cursor() as cursor:
            sql = '''
                UPDATE 
                    food_catalogue 
                SET
                    name=%s, kcals=%s
                WHERE
                    id=%s;'''
            values = (food_name, food_kcals, food_id)
            cursor.execute(sql, values)
            connection.commit()
        return True
    except Exception as exc:
        print(exc)
        return False


### USERS_CATALOGUE ###################################################################################################

def db_get_users_food_catalogue_ids_list(user_id: int):
    try:
        with connection.cursor() as cursor:
            sql = '''
                SELECT
                    food_id_list
                FROM
                    food_users_catalogue
                WHERE
                    user_id=%s;'''
            values = (user_id,)
            cursor.execute(sql, values)
            res = cursor.fetchone()
        return res
    except Exception as exc:
        print(exc)
        return False


def db_add_users_food_catalogue_ids_list(food_ids_list: list[int], user_id: int) -> bool:
    try:
        with connection.cursor() as cursor:
            sql = '''
                INSERT INTO
                    food_users_catalogue (food_id_list, user_id)
                VALUES
                    (%s, %s);'''
            values = (food_ids_list, user_id)
            cursor.execute(sql, values)
            connection.commit()
        return True
    except Exception as exc:
        print(exc)
        return False


def db_update_users_food_catalogue_ids_list(food_ids_list: list[int], user_id: int) -> bool:
    try:
        with connection.cursor() as cursor:
            sql = '''
                UPDATE 
                    food_users_catalogue 
                SET
                    food_id_list=%s
                WHERE
                    user_id=%s;'''
            values = (food_ids_list, user_id)
            cursor.execute(sql, values)
            connection.commit()
        return True
    except Exception as exc:
        print(exc)
        return False


def db_get_catalogue_ids() -> tuple[str, list]:
    try:
        with connection.cursor() as cursor:
            sql = '''
                SELECT
                    id
                FROM
                    food_catalogue;'''
            cursor.execute(sql,)
            res = cursor.fetchall()
        return res
    except Exception as exc:
        print(exc)
        return False


### MISC ##############################################################################################################

def db_get_users_first_date(user_id):
    try:
        with connection.cursor() as c:
            dates = []
            values = (user_id,)
            sql = '''
                SELECT
                    MIN(date)
                FROM
                    food_body_weight
                WHERE
                    user_id=%s;'''
            c.execute(sql, values)
            dates.append(c.fetchone()[0])
            sql = '''
                SELECT
                    MIN(date)
                FROM
                    food_diary
                WHERE
                    user_id=%s;'''
            c.execute(sql, values)
            dates.append(c.fetchone()[0])
            first_date = min(dates)
        return first_date
    except Exception as exc:
        print(exc)
        return False


def db_get_users_height(user_id):
    try:
        with connection.cursor() as cursor:
            sql = '''
                SELECT
                    height
                FROM
                    food_settings
                WHERE
                    user_id=%s'''
            values = (user_id,)
            cursor.execute(sql, values)
            res = cursor.fetchone()
        return res
    except Exception as exc:
        print(exc)
        return False
