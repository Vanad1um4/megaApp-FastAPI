from pprint import pprint
from fastapi import APIRouter, Depends
from utils.auth import AuthHandler

from schemas import Transaction
from db.transaction import db_get_transaction_list_by_user_id, db_add_transaction, db_update_transaction, db_delete_transaction

router = APIRouter()
auth_handler = AuthHandler()


@router.get('/transaction', tags=['Money -> Transaction'])
def get_transaction_list(user_id=Depends(auth_handler.auth_wrapper)):
    res = db_get_transaction_list_by_user_id(user_id)
    # pprint(res)
    prepped_transactions = prep_transactions(res)
    # pprint(prepped_transactions)
    return {'transaction_list': prepped_transactions}


@router.post('/transaction', tags=['Money -> Transaction'])
def add_transaction(transaction: Transaction, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_add_transaction(transaction, user_id)
    return {'result: ': res}


@router.put('/transaction/{transaction_id}', tags=['Money -> Transaction'])
def edit_transaction(transaction_id: int, transaction: Transaction, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_update_transaction(transaction, transaction_id, user_id)
    return {'result: ': res}


@router.delete('/transaction/{transaction_id}', tags=['Money -> Transaction'])
def delete_transaction(transaction_id: int, user_id=Depends(auth_handler.auth_wrapper)):
    res = db_delete_transaction(transaction_id, user_id)
    return {'result: ': res}

def prep_transactions(transactions_list):
    result = {}

    for transaction in transactions_list:
        if transaction['date'] in result.keys():
            result[transaction['date']].append(transaction)
        else:
            result[transaction['date']] = [transaction]
    
    return result