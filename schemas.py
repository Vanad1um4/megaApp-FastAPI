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


class Category(BaseModel):
    title: str
    kind: str


class Transaction(BaseModel):
    date: str
    amount: float
    account_id: int
    category_id: int
    kind: str
    is_gift: bool
    notes: str | None
    twin_transaction_id: int | None
    target_account_id: int | None
    target_account_amount: int | None
