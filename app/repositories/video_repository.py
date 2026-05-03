from sqlalchemy.ext.asyncio import AsyncSession

from app.models.video import Video


class VideoRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, video: Video) -> Video:
        self.db.add(video)
        await self.db.flush()
        await self.db.refresh(video)
        return video

    async def update(self, video: Video) -> Video:
        self.db.add(video)
        await self.db.flush()
        await self.db.refresh(video)
        return video
