from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user_id: str, username: str) -> User:
        user = User(id=user_id, username=username)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_or_create(self, user_id: str, username: str) -> User:
        user = await self.get_by_id(user_id)
        if user is None:
            user = await self.create(user_id=user_id, username=username)
        return user

    async def set_playback_position(self, user: User, video_id: str | None, position_seconds: int) -> User:
        user.last_video_id = video_id
        user.last_position_seconds = max(0, int(position_seconds))
        await self.db.flush()
        await self.db.refresh(user)
        return user
