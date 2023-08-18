import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from api import test, auth

from env import APP_IP, APP_PORT


app = FastAPI()

app.include_router(auth.router, prefix='/api/auth')
app.include_router(test.router, prefix='/api/test')

@app.get('/', response_class=FileResponse, tags=['Site'])
async def serve_angular_app():
    return FileResponse('src-front/index.html')

app.mount('/', StaticFiles(directory='src-front', html=True))

if __name__ == '__main__':
    uvicorn.run(app, host=f'{APP_IP}', port=APP_PORT)
