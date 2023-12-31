from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse

from utils.auth import AuthHandler
from schemas import UserLogin
from db.user import db_get_user_id_by_username, db_get_a_user_by_username, db_create_user

router = APIRouter()

auth_handler = AuthHandler()


@router.post('/register', tags=['Auth'])
def register(auth_creds: UserLogin):
    user_id = db_get_user_id_by_username(auth_creds.username)
    if user_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username is taken')

    hashed_password = auth_handler.get_password_hash(auth_creds.password)
    res = db_create_user(auth_creds.username, hashed_password)
    if not res:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Something went wrong')

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={'message': 'User created successfully'})


@router.post('/login', tags=['Auth'])
def login(auth_creds: UserLogin):
    user = db_get_a_user_by_username(auth_creds.username)
    if (
        user is None
        or not auth_handler.verify_password(auth_creds.password, user['hashed_password'])
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username and/or password')

    token = auth_handler.encode_token(user['username'])
    return {'token': token}


@router.get('/test-unprotected', tags=['Auth'])
def unprotected():
    return {'hello': 'world'}


@router.get('/test-protected', tags=['Auth'])
def protected(user_id=Depends(auth_handler.auth_wrapper)):
    return {'user_id': user_id}
