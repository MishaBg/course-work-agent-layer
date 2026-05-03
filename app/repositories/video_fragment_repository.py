from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.video_fragment import VideoFragment


class VideoFragmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_video_and_number(self, video_id: str, fragment_number: int) -> VideoFragment | None:
        query = select(VideoFragment).where(
            VideoFragment.video_id == video_id,
            VideoFragment.fragment_number == fragment_number,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_many(self, fragments: list[VideoFragment]) -> list[VideoFragment]:
        self.db.add_all(fragments)
        await self.db.flush()
        for fragment in fragments:
            await self.db.refresh(fragment)
        return fragments
