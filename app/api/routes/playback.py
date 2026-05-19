from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.schemas.playback import PlaybackStateResponse, PlaybackStateUpdateRequest


router = APIRouter(prefix="/users", tags=["playback"])


@router.get(
    "/{user_id}/playback",
    response_model=PlaybackStateResponse,
    summary="Получить сохраненную позицию воспроизведения",
)
async def get_playback_state(
    user_id: str = Path(..., description="Идентификатор пользователя"),
    db: AsyncSession = Depends(get_db_session),
) -> PlaybackStateResponse:
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return PlaybackStateResponse(
        user_id=user.id,
        video_id=user.last_video_id,
        position_seconds=user.last_position_seconds,
    )


@router.put(
    "/{user_id}/playback",
    response_model=PlaybackStateResponse,
    summary="Сохранить позицию воспроизведения",
)
async def update_playback_state(
    payload: PlaybackStateUpdateRequest,
    user_id: str = Path(..., description="Идентификатор пользователя"),
    db: AsyncSession = Depends(get_db_session),
) -> PlaybackStateResponse:
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user = await repo.set_playback_position(
        user=user,
        video_id=payload.video_id,
        position_seconds=payload.position_seconds,
    )
    await db.commit()

    return PlaybackStateResponse(
        user_id=user.id,
        video_id=user.last_video_id,
        position_seconds=user.last_position_seconds,
    )
