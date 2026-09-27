from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime


class ItemCreate(BaseModel):
    name: str
    description: str = ""
    owner_id: int


class ItemRead(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: datetime
