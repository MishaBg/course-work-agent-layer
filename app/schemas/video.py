from datetime import datetime

from pydantic import BaseModel, Field


class VideoFragmentMeta(BaseModel):
    fragment_number: int = Field(description="Порядковый номер минутного фрагмента", examples=[1])
    storage_key: str = Field(description="Ключ объекта фрагмента в S3/MinIO")
    content_type: str = Field(description="MIME-тип фрагмента", examples=["video/mp4"])
    size_bytes: int | None = Field(default=None, description="Размер фрагмента в байтах")
    duration_seconds: int | None = Field(default=None, description="Длительность фрагмента в секундах")
    etag: str | None = Field(default=None, description="ETag объекта в S3/MinIO")


class VideoIngestResponse(BaseModel):
    video_id: str = Field(description="Идентификатор загруженного видео")
    title: str = Field(description="Название видео")
    description: str | None = Field(default=None, description="Описание видео")
    original_filename: str = Field(description="Оригинальное имя загруженного файла")
    content_type: str = Field(description="MIME-тип исходного файла")
    duration_seconds: int | None = Field(default=None, description="Общая длительность видео в секундах")
    total_fragments: int = Field(description="Количество созданных минутных фрагментов")
    status: str = Field(description="Статус обработки видео")
    created_at: datetime = Field(description="Дата и время создания записи")
    fragments: list[VideoFragmentMeta] = Field(default_factory=list, description="Метаданные созданных фрагментов")
