from datetime import datetime

from pydantic import BaseModel, Field


class FragmentAccessResponse(BaseModel):
    request_id: str = Field(description="Идентификатор запроса фрагмента")
    status: str = Field(description="Текущий статус запроса: accepted/found/not_found/failed")
    video_id: str = Field(description="Идентификатор видео")
    fragment_number: int = Field(description="Номер фрагмента")
    storage_key: str | None = Field(default=None, description="Ключ фрагмента в S3/MinIO")
    content_type: str | None = Field(default=None, description="MIME-тип фрагмента")
    object_size: int | None = Field(default=None, description="Размер объекта в байтах")
    etag: str | None = Field(default=None, description="ETag объекта в S3/MinIO")
    message: str | None = Field(default=None, description="Описание ошибки/состояния")
    created_at: datetime = Field(description="Дата и время создания запроса")
