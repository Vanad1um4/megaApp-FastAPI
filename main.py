import uvicorn

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api import auth, bank, currency, account

from env import APP_IP, APP_PORT


tags_metadata = [
    {'name': 'Money -> Currency', 'description': 'Маршруты для работы со списком валют.'},
    {'name': 'Money -> Bank', 'description': 'Маршруты для работы со списком банков.'},
    {'name': 'Money -> Account', 'description': 'Маршруты для работы со списком счетов.'},
    {'name': 'Auth', 'description': 'Маршруты для работы с авторизацией.'},
    {'name': 'Site', 'description': 'Отдача приложения на Angular.'},
]

app = FastAPI(title='megaApp', openapi_tags=tags_metadata)

app.include_router(auth.router, prefix='/api/auth')
app.include_router(currency.router, prefix='/api/money')
app.include_router(bank.router, prefix='/api/money')
app.include_router(account.router, prefix='/api/money')


@app.get('/', response_class=FileResponse, tags=['Site'])
async def serve_angular_app():
    return FileResponse('src-front/index.html')

app.mount('/', StaticFiles(directory='src-front', html=True))

if __name__ == '__main__':
    uvicorn.run(app, host=f'{APP_IP}', port=APP_PORT)
