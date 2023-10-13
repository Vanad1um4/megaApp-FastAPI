from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from utils.auth import AuthHandler

from schemas import Bank
from db.user import db_get_user_id_by_email
from db.bank import db_get_bank_list_by_userid, db_add_bank, db_update_bank, db_delete_bank

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/bank', tags=['Account -> Bank'])
def get_bank_list(email=Depends(auth_handler.auth_wrapper)):
    user_id = db_get_user_id_by_email(email)
    res = db_get_bank_list_by_userid(user_id)
    return {'bank_list': res}


@router.post('/bank', tags=['Account -> Bank'])
def add_bank(bank: Bank, email=Depends(auth_handler.auth_wrapper)):
    user_id = db_get_user_id_by_email(email)
    res = db_add_bank(bank, user_id)
    return {'result: ': res}


@router.put('/bank/{bank_id}', tags=['Account -> Bank'])
def edit_bank(bank: Bank, bank_id: int, email=Depends(auth_handler.auth_wrapper)):
    user_id = db_get_user_id_by_email(email)
    res = db_update_bank(bank, bank_id, user_id)
    return {'result: ': res}


@router.delete('/bank/{bank_id}', tags=['Account -> Bank'])
def delete_bank(bank_id: int, email=Depends(auth_handler.auth_wrapper)):
    user_id = db_get_user_id_by_email(email)
    res = db_delete_bank(bank_id, user_id)
    return {'result: ': res}
