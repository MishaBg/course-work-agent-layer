from pydantic import BaseModel, Field


class PlaybackStateResponse(BaseModel):
    user_id: str = Field(description="Идентификатор пользователя")
    video_id: str | None = Field(default=None, description="Идентификатор текущего видео")
    position_seconds: int = Field(default=0, ge=0, description="Позиция воспроизведения в секундах")


class PlaybackStateUpdateRequest(BaseModel):
    video_id: str | None = Field(default=None, description="Идентификатор видео для сохранения позиции")
    position_seconds: int = Field(ge=0, description="Позиция воспроизведения в секундах")
