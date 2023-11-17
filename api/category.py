from fastapi import APIRouter, Depends
from utils.auth import AuthHandler
from pprint import pprint

from schemas import Category
from db.category import db_get_category_list_by_user_id, db_add_category, db_update_category, db_delete_category

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/category', tags=['Money -> Category'])
def get_category_list(user_id=Depends(auth_handler.auth_wrapper)):
    res = db_get_category_list_by_user_id(user_id)
    return {'categories_list': res}


@router.post('/category', tags=['Money -> Category'])
def add_category(category: Category, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_add_category(category, user_id)
    return {'result: ': res}


@router.put('/category/{category_id}', tags=['Money -> Category'])
def edit_category(category: Category, category_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_update_category(category, category_id, user_id)
    return {'result: ': res}


@router.delete('/category/{category_id}', tags=['Money -> Category'])
def delete_category(category_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_delete_category(category_id, user_id)
    return {'result: ': res}
