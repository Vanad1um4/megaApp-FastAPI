from psycopg2.extras import DictCursor
from datetime import datetime, timedelta

# from schemas import Bank
from db.db import get_connection45
from db.db import get_connection
from env import FETCH_DAYS_RANGE_OFFSET
from utils.utils import stopwatch

connection45 = get_connection45()
connection = get_connection()


def dictify_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictify_fetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row is not None:
        return dict(zip(columns, row))
    else:
        return None


# @stopwatch
def db_get_diary_by_userid(date_iso_start: str, date_iso_end: str, user_id: int) -> list[dict[str, int | str]] | None | bool:
    try:
        with connection45.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT 
                    id, date, catalogue_id, food_weight
                FROM
                    diary
                WHERE
                    users_id=%s
                    AND date BETWEEN date %s AND date %s 
                ORDER BY
                    date ASC, id ASC;'''
            # AND date BETWEEN date %s - %s AND date %s + %s
            # values = (user_id, date_iso, FETCH_DAYS_RANGE_OFFSET, date_iso, FETCH_DAYS_RANGE_OFFSET)
            values = (user_id, date_iso_start, date_iso_end)
            cursor.execute(sql, values)
            res = dictify_fetchall(cursor)
        return res
    except Exception as exc:
        print(exc)
        return False


# @stopwatch
def db_get_users_weights_range(date_iso_start: str, date_iso_end: str, user_id: int):
    try:
        with connection45.cursor() as cursor:
            sql = '''
            SELECT
                date, weight
            FROM
                weights
            WHERE
                users_id=%s
                AND date BETWEEN date %s AND date %s 
            ORDER BY
                date;'''
            values = (user_id, date_iso_start, date_iso_end)
            cursor.execute(sql, values)
            res = cursor.fetchall()
            # res = [(date.strftime('%Y-%m-%d'), weight) for date, weight in res]
            # res = {date.isoformat(): weight for date, weight in res}

        return res
    except Exception as exc:
        print(exc)
        return False


# @stopwatch
def db_get_catalogue() -> tuple[str, list]:
    try:
        with connection45.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    id, name, kcals
                FROM
                    catalogue;'''
            cursor.execute(sql,)
            res = dictify_fetchall(cursor)
        return res
    except Exception as exc:
        print(exc)
        return False


def db_get_users_coefficients(user_id: int) -> tuple[str, list]:
    try:
        with connection45.cursor() as cursor:
            sql = '''
                SELECT
                    coefficients
                FROM
                    options
                WHERE
                    user_id=%s;'''
            values = (user_id,)
            cursor.execute(sql, values)
            res = cursor.fetchone()
        return res
    except Exception as exc:
        print(exc)
        return False


def db_get_users_cached_stats(user_id: int):
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    up_to_date, stats
                FROM
                    kcal_stats
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
                        kcal_stats (up_to_date, stats, user_id)
                    VALUES
                        (%s, %s, %s);'''
            else:
                sql = '''
                    UPDATE
                        kcal_stats
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


### BODY WEIGHT ########################################################################################################

def db_get_users_body_weight(date_iso: str, user_id: int) -> tuple[str, list]:
    try:
        with connection45.cursor() as cursor:
            sql = '''
                SELECT
                    weight
                FROM
                    weights
                WHERE
                    users_id=%s
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
        with connection45.cursor() as cursor:
            res0 = db_get_users_body_weight(date_iso, user_id)
            if not res0:
                sql = '''
                    INSERT INTO
                        weights (weight, users_id, date)
                    VALUES
                        (%s, %s, %s);'''
            else:
                sql = '''
                    UPDATE
                        weights
                    SET
                        weight=%s
                    WHERE
                        users_id=%s
                        AND date=%s;'''
            values = (weight, user_id, date_iso)
            cursor.execute(sql, values)
            connection45.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


########################################################################################################################
### OLD FUNCTIONS ######################################################################################################
########################################################################################################################

def db_get_use_coeffs_bool(user_id):
    try:
        with connection45.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT 
                    use_coeffs
                FROM
                    options
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
        with connection45.cursor() as cursor:
            sql = '''
                UPDATE
                    options
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


def db_get_catalogue_ids() -> tuple[str, list]:
    try:
        with connection45.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    id
                FROM
                    catalogue;'''
            cursor.execute(sql,)
            res = cursor.fetchall()
        return res
        # return [row[0] for row in res]
    except Exception as exc:
        print(exc)
        return False


def db_get_food_from_diary(user_id, date_iso):
    try:
        if date_iso == None:
            today = datetime.today()
            date_iso = today.strftime('%Y-%m-%d')
        with connection45.cursor() as c:
            sql = '''
                SELECT
                    diary.id,
                    catalogue.name,
                    diary.food_weight,
                    cast(round(diary.food_weight / 100.0 * catalogue.kcals) as integer) as eaten_kcals,
                    catalogue.id,
                    catalogue.helth
                FROM
                    diary
                JOIN
                    catalogue on diary.catalogue_id=catalogue.id
                WHERE
                    diary.date=%s and diary.users_id=%s
                ORDER BY
                    diary.id;'''
            values = (date_iso, user_id)
            c.execute(sql, values)
            res = c.fetchall()
        return res
    except Exception as exc:
        print(exc)
        return []


def db_get_users_first_date(user_id):
    try:
        with connection45.cursor() as c:
            dates = []
            values = (user_id,)
            sql = 'select date from weights where users_id=%s order by date asc limit 1;'
            c.execute(sql, values)
            dates.append(c.fetchone()[0])
            sql = 'select date from diary where users_id=%s order by date asc limit 1;'
            c.execute(sql, values)
            dates.append(c.fetchone()[0])
            first_date = min(dates)
        return ('success', first_date)
    except Exception as exc:
        print(exc)
        return ('failure', [])


def db_get_users_weights_all(user_id):
    try:
        with connection45.cursor() as c:
            sql = 'select date, weight from weights where users_id=%s order by date;'
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchall()
        return ('success', res)
    except Exception as exc:
        print(exc)
        return ('failure', [])


def db_get_all_diary_entries(user_id):
    try:
        with connection45.cursor() as c:
            sql = 'select date, catalogue_id, food_weight from diary where users_id=%s order by date;'
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchall()
            return ('success', res)
    except Exception as exc:
        print(exc)
        return ('failure', [])


def db_get_all_catalogue_entries():
    try:
        with connection45.cursor() as c:
            sql = 'select id, kcals, name from catalogue order by id;'
            c.execute(sql, )
            res = c.fetchall()
        return ('success', res)
    except Exception as exc:
        print(exc)
        return ('failure', [])


def db_get_users_diary_entries_and_helth_values(user_id):
    try:
        with connection45.cursor() as c:
            sql = '''
                select d.date, d.catalogue_id, d.food_weight, c.kcals, c.helth
                from diary d join catalogue c on d.catalogue_id=c.id
                where d.users_id=%s
                order by d.date;'''
            values = (user_id,)
            c.execute(sql, values)
            # res = c.fetchall()
            res = dict_fetchall(c)
        return ('success', res)
    except Exception as exc:
        print(exc)
        return ('failure', [])


def dict_fetchall(cursor):
    """Returns all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def db_get_one_weight(user_id, date_iso):
    try:
        if date_iso == None:
            today = datetime.today()
            date_iso = today.strftime('%Y-%m-%d')
        with connection45.cursor() as c:
            sql = 'select weight from weights where users_id=%s and date=%s;'
            values = (user_id, date_iso)
            c.execute(sql, values)
            res = c.fetchone()
            if res:
                return ('success', res)
            else:
                return ('no_data', [])
    except Exception as exc:
        print(exc)
        return ('failure', [])


def db_get_all_food_names(user_id):
    try:
        with connection45.cursor() as c:
            sql = 'select id, name from catalogue where users_id=0 or users_id=%s order by name;'
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchall()
        return ('success', res)
    except Exception as exc:
        print(exc)
        return ('failure', [])


def db_get_height(user_id):
    try:
        with connection45.cursor() as c:
            sql = 'select height from options where user_id=%s'
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchone()
        return ('success', res)
    except Exception as exc:
        print(exc)
        return ('failure', [])
