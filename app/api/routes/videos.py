from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.video import VideoIngestResponse
from app.services.video_ingest_service import VideoIngestService


router = APIRouter(prefix="/videos", tags=["videos"])


@router.post(
    "",
    response_model=VideoIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить видео и подготовить минутные фрагменты",
    description=(
        "Принимает mp4-файл и метаданные видео, сохраняет запись в БД, "
        "разбивает видео на фрагменты по 60 секунд, загружает фрагменты в S3/MinIO "
        "и создает записи фрагментов в БД."
    ),
)
async def upload_video(
    user_id: str = Form(..., description="Идентификатор пользователя"),
    title: str = Form(..., description="Название видео"),
    description: str | None = Form(default=None, description="Описание видео"),
    file: UploadFile = File(..., description="MP4-файл видео"),
    db: AsyncSession = Depends(get_db_session),
) -> VideoIngestResponse:
    service = VideoIngestService(db)
    try:
        return await service.ingest_video(user_id=user_id, title=title, description=description, file=file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected ingestion error: {exc}") from exc
