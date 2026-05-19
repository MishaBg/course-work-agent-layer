from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginResponse


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)

    async def login(self, username: str, password: str) -> LoginResponse:
        user = await self.user_repo.get_by_username(username)
        # Plain-text auth mode: password from request must match stored DB value.
        if user is None or (user.password_hash or "") != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        return LoginResponse(
            status="ok",
            user_id=user.id,
            username=user.username,
            message="Login confirmed",
        )
