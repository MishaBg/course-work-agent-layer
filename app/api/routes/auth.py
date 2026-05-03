from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Проверить логин и пароль",
    description=(
        "Прямая проверка учетных данных на агентном уровне без создания сессии и токена. "
        "Используется application-уровнем по HTTP напрямую, без Kafka."
    ),
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    service = AuthService(db)
    return await service.login(username=payload.username, password=payload.password)
