import logging
import sys

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
    force=True,
)

app = FastAPI(
    title="Agent Layer Service",
    version="0.2.0",
    description=(
        "API агентного уровня видеохостинга. "
        "Сервис принимает видео, режет его на минутные фрагменты, "
        "сохраняет фрагменты в S3/MinIO и выдает служебную информацию по запросу фрагментов."
    ),
    openapi_tags=[
        {
            "name": "health",
            "description": "Проверка доступности сервиса.",
        },
        {
            "name": "auth",
            "description": "Прямая проверка логина и пароля без токенов и сессий.",
        },
        {
            "name": "videos",
            "description": "Операции загрузки и обработки видео.",
        },
        {
            "name": "fragments",
            "description": "Операции запроса подготовленных фрагментов.",
        },
    ],
)
app.include_router(api_router)
