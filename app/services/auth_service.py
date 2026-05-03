from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginResponse


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repo = UserRepository(db)

    async def login(self, username: str, password: str) -> LoginResponse:
        user = await self.user_repo.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
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
