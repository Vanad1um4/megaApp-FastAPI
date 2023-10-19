from pprint import pprint
from psycopg2.extras import DictCursor

from schemas import Category
from db.db import get_connection

connection = get_connection()


def db_get_category_list_by_user_id(user_id: int) -> list[dict[str, int | str]] | None | bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = 'SELECT id, title, parent_id, kind FROM category WHERE user_id=%s ORDER BY id;'
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


def db_add_category(category: Category, user_id: int) -> bool:
    pprint(category)
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = 'INSERT INTO category (title, parent_id, kind, user_id) VALUES (%s, %s, %s, %s);'
            values = (category.title, category.parent_id, category.kind, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_update_category(category: Category, category_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = 'UPDATE category SET title=%s, parent_id=%s, kind=%s WHERE id=%s AND user_id=%s;'
            values = (category.title, category.parent_id, category.kind, category_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False


def db_delete_category(category_id: int, user_id: int) -> bool:
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            sql = 'DELETE FROM category WHERE id=%s AND user_id=%s;'
            values = (category_id, user_id)
            cursor.execute(sql, values)
            connection.commit()
            return True
    except Exception as exc:
        print(exc)
        return False
