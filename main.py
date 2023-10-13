import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from api import auth, account, bank

from env import APP_IP, APP_PORT


tags_metadata = [
    {"name": "Account -> Currency", "description": "Маршруты для работы со списком валют."},
    {"name": "Account -> Bank", "description": "Маршруты для работы со списком банков."},
    {"name": "Auth", "description": "Маршруты для работы с авторизацией."},
    {"name": "Site", "description": "Отдача приложения на Angular."},
]

app = FastAPI(
    openapi_tags=tags_metadata
)

app.include_router(auth.router, prefix='/api/auth')
app.include_router(account.router, prefix='/api/money')
app.include_router(bank.router, prefix='/api/money')


@app.get('/', response_class=FileResponse, tags=['Site'])
async def serve_angular_app():
    return FileResponse('src-front/index.html')

app.mount('/', StaticFiles(directory='src-front', html=True))

if __name__ == '__main__':
    uvicorn.run(app, host=f'{APP_IP}', port=APP_PORT)
