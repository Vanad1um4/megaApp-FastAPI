from fastapi import APIRouter, Depends
from utils.auth import AuthHandler
from pprint import pprint

from schemas import Bank
from db.bank import db_get_bank_list_by_userid, db_add_bank, db_update_bank, db_delete_bank

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/bank', tags=['Money -> Bank'])
def get_bank_list(user_id=Depends(auth_handler.auth_wrapper)):
    res = db_get_bank_list_by_userid(user_id)
    return {'banks_list': res}


@router.post('/bank', tags=['Money -> Bank'])
def add_bank(bank: Bank, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_add_bank(bank, user_id)
    return {'result: ': res}


@router.put('/bank/{bank_id}', tags=['Money -> Bank'])
def edit_bank(bank: Bank, bank_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_update_bank(bank, bank_id, user_id)
    return {'result: ': res}


@router.delete('/bank/{bank_id}', tags=['Money -> Bank'])
def delete_bank(bank_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_delete_bank(bank_id, user_id)
    return {'result: ': res}
