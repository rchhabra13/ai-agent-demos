from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.database import get_session
from app.crud.models import Item, User
from app.schemas.crud import ItemCreate, ItemRead, UserCreate, UserRead

router = APIRouter(prefix="/api", tags=["crud"])


@router.post("/users", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    user = User(name=payload.name, email=payload.email)
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    return user


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/items", response_model=ItemRead, status_code=201)
async def create_item(payload: ItemCreate, session: AsyncSession = Depends(get_session)):
    owner = await session.get(User, payload.owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    item = Item(name=payload.name, description=payload.description, owner_id=payload.owner_id)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("/items", response_model=list[ItemRead])
async def list_items(
    owner_id: int | None = None,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    query = select(Item)
    if owner_id is not None:
        query = query.where(Item.owner_id == owner_id)
    query = query.limit(limit)
    result = await session.exec(query)
    return result.all()
