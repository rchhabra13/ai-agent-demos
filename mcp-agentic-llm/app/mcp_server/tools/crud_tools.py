from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.models import Item, User


def register(mcp: FastMCP, get_session) -> None:

    @mcp.tool(description="Create a new user in the internal database.")
    async def create_user(
        name: Annotated[str, "User's full name"],
        email: Annotated[str, "User's email address (must be unique)"],
    ) -> dict:
        async with get_session() as session:
            user = User(name=name, email=email)
            session.add(user)
            try:
                await session.commit()
                await session.refresh(user)
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Could not create user: {e}")
            return {"id": user.id, "name": user.name, "email": user.email}

    @mcp.tool(description="Get a user by ID from the internal database.")
    async def get_user(
        user_id: Annotated[int, "User ID to look up"],
    ) -> dict:
        async with get_session() as session:
            user = await session.get(User, user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            return {"id": user.id, "name": user.name, "email": user.email}

    @mcp.tool(description="Create a new item owned by a user.")
    async def create_item(
        name: Annotated[str, "Item name"],
        description: Annotated[str, "Item description"] = "",
        owner_id: Annotated[int, "ID of the owning user"] = 0,
    ) -> dict:
        async with get_session() as session:
            owner = await session.get(User, owner_id)
            if not owner:
                raise ValueError(f"User {owner_id} not found")
            item = Item(name=name, description=description, owner_id=owner_id)
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return {"id": item.id, "name": item.name, "description": item.description, "owner_id": item.owner_id}

    @mcp.tool(description="List items from the internal database, optionally filtered by owner.")
    async def list_items(
        owner_id: Annotated[Optional[int], "Filter by owner user ID (optional)"] = None,
        limit: Annotated[int, "Max items to return"] = 20,
    ) -> list[dict]:
        async with get_session() as session:
            query = select(Item)
            if owner_id is not None:
                query = query.where(Item.owner_id == owner_id)
            query = query.limit(limit)
            result = await session.exec(query)
            items = result.all()
            return [{"id": i.id, "name": i.name, "description": i.description, "owner_id": i.owner_id} for i in items]
