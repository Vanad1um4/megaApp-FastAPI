from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class Currency(BaseModel):
    name: str
    ticker: str
    symbol: str
    symbol_pos: str
    whitespace: bool


class Bank(BaseModel):
    name: str
