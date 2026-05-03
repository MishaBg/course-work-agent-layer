from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.fragment import FragmentAccessResponse
from app.services.fragment_service import FragmentService


router = APIRouter(prefix="/videos", tags=["fragments"])


@router.get(
    "/{video_id}/fragments/{fragment_number}",
    response_model=FragmentAccessResponse,
    summary="Запросить служебные данные о фрагменте",
    description=(
        "Проверяет наличие метаданных и объекта фрагмента в S3/MinIO, "
        "создает запись запроса в БД и вызывает producer-stub."
    ),
)
async def request_video_fragment(
    video_id: str = Path(..., description="Идентификатор видео"),
    fragment_number: int = Path(..., ge=1, description="Порядковый номер фрагмента, начиная с 1"),
    user_id: str = Query(..., description="Идентификатор пользователя"),
    db: AsyncSession = Depends(get_db_session),
) -> FragmentAccessResponse:
    """Возвращает служебные данные о доступности фрагмента и публикует запрос в producer-stub."""
    service = FragmentService(db)
    return await service.request_fragment(video_id=video_id, fragment_number=fragment_number, user_id=user_id)
