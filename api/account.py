from fastapi import APIRouter, Depends

from utils.auth import AuthHandler
from schemas import Account
from db.bank import db_get_bank_list_by_userid
from db.currency import db_get_currency_list_by_userid
from db.account import db_get_account_list_by_userid, db_add_account, db_update_account, db_delete_account

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/account', tags=['Money -> Account'])
def get_account_list(user_id=Depends(auth_handler.auth_wrapper)):
    bank_list = db_get_bank_list_by_userid(user_id)
    currency_list = db_get_currency_list_by_userid(user_id)
    account_list = db_get_account_list_by_userid(user_id)
    res = {'bank_list': bank_list, 'currency_list': currency_list, 'account_list': account_list}
    return res


@router.post('/account', tags=['Money -> Account'])
def add_account(account: Account, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_add_account(account, user_id)
    return {'result: ': res}


@router.put('/account/{account_id}', tags=['Money -> Account'])
def edit_account(account: Account, account_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_update_account(account, account_id, user_id)
    return {'result: ': res}


@router.delete('/account/{account_id}', tags=['Money -> Account'])
def delete_account(account_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_delete_account(account_id, user_id)
    return {'result: ': res}
