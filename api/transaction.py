from pprint import pprint
from fastapi import APIRouter, Depends
from utils.auth import AuthHandler

from schemas import Transaction
from db.transaction import db_get_transaction_list_by_user_id, db_add_one_transaction, db_add_two_transactions, db_update_one_transaction, db_update_two_transactions, db_delete_transaction

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/transaction/{day}', tags=['Money -> Transaction'])
def get_transaction_list(day: str, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_get_transaction_list_by_user_id(user_id, day)
    return {'transactions_list': res}


@router.post('/transaction', tags=['Money -> Transaction'])
def add_transaction(transaction: Transaction, user_id=Depends(auth_handler.auth_wrapper)):
    # pprint(transaction)
    if transaction.kind == 'expense' or transaction.kind == 'income':
        res = db_add_one_transaction(transaction, user_id)
    if transaction.kind == 'transfer':
        # pprint(transaction)
        res = db_add_two_transactions(transaction, user_id)
    return {'result: ': res if res else 'error'}


@router.put('/transaction/{transaction_id}', tags=['Money -> Transaction'])
def edit_transaction(transaction_id: int, transaction: Transaction, user_id=Depends(auth_handler.auth_wrapper)):
    # pprint(transaction_id)
    # pprint(transaction)
    if transaction.kind == 'expense' or transaction.kind == 'income':
        res = db_update_one_transaction(transaction, transaction_id, user_id)
    if transaction.kind == 'transfer':
        res = db_update_two_transactions(transaction, transaction_id, user_id)
    return {'result: ': res if res else 'error'}


@router.delete('/transaction/{transaction_id}', tags=['Money -> Transaction'])
def delete_transaction(transaction_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    # pprint(transaction_id)
    res = db_delete_transaction(transaction_id, user_id)
    return {'result: ': res}
