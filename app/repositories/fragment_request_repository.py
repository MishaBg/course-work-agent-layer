from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fragment_request import FragmentRequest


class FragmentRequestRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, request: FragmentRequest) -> FragmentRequest:
        self.db.add(request)
        await self.db.flush()
        await self.db.refresh(request)
        return request

    async def update(self, request: FragmentRequest) -> FragmentRequest:
        self.db.add(request)
        await self.db.flush()
        await self.db.refresh(request)
        return request
