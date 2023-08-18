import psycopg2
from psycopg2.extras import DictCursor

from env import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS


with psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
) as connection:

    def db_create_user(user_email, hashed_password):
        try:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                sql = 'insert into users (email, hashed_password) values (%s, %s);'
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
                sql = 'select id from users where email=%s;'
                values = (user_email,)
                cursor.execute(sql, values)
                res = cursor.fetchone()
                return res
        except Exception as exc:
            print(exc)
            return False

    def db_get_user_hashed_pass_by_email(user_email):
        try:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                sql = 'select hashed_password from users where email=%s;'
                values = (user_email,)
                cursor.execute(sql, values)
                res = cursor.fetchone()
                return res
        except Exception as exc:
            print(exc)
            return False

    def db_get_a_user_by_email(user_email):
        try:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                sql = 'select * from users where email=%s;'
                values = (user_email,)
                cursor.execute(sql, values)
                res = cursor.fetchone()
                return dict(res) if res else None
        except Exception as exc:
            print(exc)
            return False

    # def db_get_a_user_by_email(user_email):
    #     try:
    #         with connection.cursor() as conn:
    #             sql = 'select * from users where email=%s;'
    #             values = (user_email,)
    #             conn.execute(sql, values)
    #             res = conn.fetchone()
    #             return res
    #     except Exception as exc:
    #         print(exc)
    #         return False

    def db_get_all_users():
        try:
            with connection.cursor() as c:
                sql = 'select user_id from options order by user_id;'
                c.execute(sql,)
                res = c.fetchall()
                return ('success', res)
        except Exception as exc:
            print(exc)
            return ('failure', [])

    def db_get_all_diary_entries(user_id):
        try:
            with connection.cursor() as c:
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
            with connection.cursor() as c:
                sql = 'select id, kcals, name from catalogue order by id;'
                c.execute(sql)
                res = c.fetchall()
                return ('success', res)
        except Exception as exc:
            print(exc)
            return ('failure', [])

    def db_get_all_weight_entries(user_id):
        try:
            with connection.cursor() as c:
                sql = 'select date, weight from weights where users_id=%s order by date;'
                values = (user_id,)
                c.execute(sql, values)
                res = c.fetchall()
                return ('success', res)
        except Exception as exc:
            print(exc)
            return ('failure', [])

    def db_get_catalogue_ids():
        try:
            with connection.cursor() as c:
                sql = 'select id from catalogue'
                c.execute(sql,)
                res = c.fetchall()
            return ('success', res)
        except Exception as exc:
            print(exc)
            return ('failure', [])

    def db_get_users_coefficients(user_id):
        try:
            with connection.cursor() as c:
                sql = 'select coefficients from options where user_id=%s'
                values = (user_id,)
                c.execute(sql, values)
                res = c.fetchone()
                # print(user_id, res)
            return ('success', res)
        except Exception as exc:
            print(exc)
            return ('failure', [])

    def db_set_users_coefficients(user_id, user_coeffs):
        try:
            with connection.cursor() as c:
                sql = 'update options set coefficients=%s where user_id=%s'
                values = (user_coeffs, user_id)
                c.execute(sql, values)
            connection.commit()
            return ('success', [])
        except Exception as exc:
            print(exc)
            return ('failure', [])
