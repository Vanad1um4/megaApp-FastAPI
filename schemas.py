from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class Currency(BaseModel):
    title: str
    ticker: str
    symbol: str
    symbol_pos: str
    whitespace: bool


class Bank(BaseModel):
    title: str


class Account(BaseModel):
    title: str
    currency_id: int
    bank_id: int
    invest: bool
    kind: str
