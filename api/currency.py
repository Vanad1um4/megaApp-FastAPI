from fastapi import APIRouter, Depends
from utils.auth import AuthHandler

from schemas import Currency
from db.currency import db_get_currency_list_by_userid, db_add_currency, db_update_currency, db_delete_currency

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/currency', tags=['Money -> Currency'])
def get_currency_list(user_id=Depends(auth_handler.auth_wrapper)):
    res = db_get_currency_list_by_userid(user_id)
    return {'currencies_list': res}


@router.post('/currency', tags=['Money -> Currency'])
def add_currency(currency: Currency, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_add_currency(currency, user_id)
    return {'result: ': res}


@router.put('/currency/{currency_id}', tags=['Money -> Currency'])
def edit_currency(currency_id: int, currency: Currency, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_update_currency(currency, currency_id, user_id)
    return {'result: ': res}


@router.delete('/currency/{currency_id}', tags=['Money -> Currency'])
def edit_currency(currency_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_delete_currency(currency_id, user_id)
    return {'result: ': res}
