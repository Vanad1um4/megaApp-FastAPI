from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from utils.auth import AuthHandler

from schemas import Currency
from db.user import db_get_user_id_by_email
from db.account import db_get_currency_list_by_userid, db_add_currency, db_update_currency, db_delete_currency

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/currency', tags=['Account -> Currency'])
def get_currency_list(email=Depends(auth_handler.auth_wrapper)):
    user_id = db_get_user_id_by_email(email)
    # print(user_id)
    res = db_get_currency_list_by_userid(user_id)
    # print(res)
    return {'currency_list': res}


@router.post('/currency', tags=['Account -> Currency'])
def add_currency(currency: Currency, email=Depends(auth_handler.auth_wrapper)):
    user_id = db_get_user_id_by_email(email)
    # print(user_id)
    res = db_add_currency(currency, user_id)
    # print(res)
    return {'result: ': res}


@router.put('/currency/{currency_id}', tags=['Account -> Currency'])
def edit_currency(currency_id: int, currency: Currency, email=Depends(auth_handler.auth_wrapper)):
    user_id = db_get_user_id_by_email(email)
    res = db_update_currency(currency, currency_id, user_id)
    # print(res)
    return {'result: ': res}


@router.delete('/currency/{currency_id}', tags=['Account -> Currency'])
def edit_currency(currency_id: int, email=Depends(auth_handler.auth_wrapper)):
    user_id = db_get_user_id_by_email(email)
    # print(user_id, currency_id)
    res = db_delete_currency(currency_id, user_id)
    # print(res)
    return {'result: ': res}
