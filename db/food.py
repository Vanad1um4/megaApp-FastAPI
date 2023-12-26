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


### DIARY ######################################################################

# @stopwatch
def db_get_diary_by_userid(date_iso_start: str, date_iso_end: str, user_id: int) -> list[dict[str, int | str]] | None | bool:
    """
    [{'catalogue_id': 166, 'date': datetime.date(2023, 12, 13), 'food_weight': 142, 'id': 65328},
     {'catalogue_id': 68, 'date': datetime.date(2023, 12, 13), 'food_weight': 71, 'id': 65329},
     ...
     {'catalogue_id': 103, 'date': datetime.date(2023, 12, 22), 'food_weight': 51, 'id': 65652},
     {'catalogue_id': 85, 'date': datetime.date(2023, 12, 22), 'food_weight': 170, 'id': 65653}]
    """
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
    """
    [(datetime.date(2023, 12, 13), Decimal('74.3')),
     (datetime.date(2023, 12, 14), Decimal('74.6')),
     ...
     (datetime.date(2023, 12, 21), Decimal('136.0')),
     (datetime.date(2023, 12, 22), Decimal('45.3'))]
    """
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


### BODY WEIGHT ################################################################

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


### CATALOGUE ##################################################################

# @stopwatch
def db_get_catalogue() -> tuple[str, list]:
    """
    [{'id': 188, 'kcals': 100, 'name': 'kcals1'},
     {'id': 192, 'kcals': 19, 'name': 'Айран'},
     ...
     {'id': 202, 'kcals': 237, 'name': 'Яйца жареные'},
     {'id': 166, 'kcals': 155, 'name': 'Яйцо'}]
    """
    try:
        # with connection45.cursor(cursor_factory=DictCursor) as cursor:
        #             catalogue
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
        with connection.cursor(cursor_factory=DictCursor) as cursor:
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
        with connection.cursor(cursor_factory=DictCursor) as cursor:
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


### USERS_CATALOGUE ############################################################

def db_get_users_food_catalogue_ids_list(user_id: int):
    """
    ['["77","66"]']
    """
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = '''
                SELECT
                    food_id_list
                FROM
                    food_users_catalogue
                WHERE
                    user_id=%s;'''
            values = (user_id,)
            cursor.execute(sql, values)
            # res = dictify_fetchone(cursor)
            res = cursor.fetchone()
        return res
    except Exception as exc:
        print(exc)
        return False


def db_add_users_food_catalogue_ids_list(food_ids_list: list[int], user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
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
        with connection.cursor(cursor_factory=DictCursor) as cursor:
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


################################################################################
### OLD FUNCTIONS ##############################################################
################################################################################

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
    """
    datetime.date(2020, 10, 14)
    """
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
        return first_date
    except Exception as exc:
        print(exc)
        return ('failure', [])


def db_get_users_weights_all(user_id):
    """
    [(datetime.date(2020, 10, 14), Decimal('97.7')),
     (datetime.date(2020, 10, 15), Decimal('97.5')),
     ...
     (datetime.date(2023, 12, 21), Decimal('136.0')),
     (datetime.date(2023, 12, 22), Decimal('45.3'))]
    """
    try:
        with connection45.cursor() as c:
            sql = 'select date, weight from weights where users_id=%s order by date;'
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchall()
        return res
    except Exception as exc:
        print(exc)
        return ('failure', [])


def db_get_all_diary_entries(user_id):
    """
    [(datetime.date(2020, 10, 14), 133, 11),
     (datetime.date(2020, 10, 14), 27, 153),
     ...
     (datetime.date(2023, 12, 22), 103, 51),
     (datetime.date(2023, 12, 22), 85, 170)]
    """
    try:
        with connection45.cursor() as c:
            sql = 'select date, catalogue_id, food_weight from diary where users_id=%s order by date;'
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchall()
        return res
    except Exception as exc:
        print(exc)
        return ('failure', [])


def db_get_all_catalogue_entries():
    """
    [(1, 212, 'Салат мимоза'),
     (2, 165, 'Салат колбаса капуста'),
     ...
     (357, 25, 'Ламинарии морская капуста'),
     (358, 20, 'Сок томатный')]
    """

    try:
        with connection45.cursor() as c:
            sql = 'select id, kcals, name from catalogue order by id;'
            c.execute(sql, )
            res = c.fetchall()
        return res
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
