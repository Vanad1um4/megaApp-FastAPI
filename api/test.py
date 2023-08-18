from fastapi import APIRouter

router = APIRouter()


@router.get('/test', tags=['Test'])
async def test():
    return {'message': 'Hello World'}
