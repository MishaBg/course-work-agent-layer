from dataclasses import dataclass
from pathlib import Path

from fastapi.concurrency import run_in_threadpool
from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class FragmentObjectNotFoundError(Exception):
    pass


@dataclass
class FragmentObjectInfo:
    key: str
    content_type: str | None
    size: int
    etag: str | None


class MinioStorageClient:
    def __init__(self) -> None:
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket = settings.minio_bucket

    async def upload_fragment_file(self, object_key: str, file_path: Path) -> FragmentObjectInfo:
        await self._ensure_bucket()
        await run_in_threadpool(
            self.client.fput_object,
            self.bucket,
            object_key,
            str(file_path),
            "video/mp4",
        )
        return await self.stat_fragment(object_key)

    async def remove_fragment(self, object_key: str) -> None:
        try:
            await run_in_threadpool(self.client.remove_object, self.bucket, object_key)
        except S3Error as exc:
            if exc.code == "NoSuchKey":
                return
            raise

    async def get_fragment_bytes(self, object_key: str) -> bytes:
        def _read() -> bytes:
            obj = self.client.get_object(self.bucket, object_key)
            try:
                return obj.read()
            finally:
                obj.close()
                obj.release_conn()

        try:
            return await run_in_threadpool(_read)
        except S3Error as exc:
            if exc.code == "NoSuchKey":
                raise FragmentObjectNotFoundError(f"Object {object_key} not found") from exc
            raise

    async def stat_fragment(self, object_key: str) -> FragmentObjectInfo:
        try:
            stat = await run_in_threadpool(self.client.stat_object, self.bucket, object_key)
        except S3Error as exc:
            if exc.code == "NoSuchKey":
                raise FragmentObjectNotFoundError(f"Object {object_key} not found") from exc
            raise

        return FragmentObjectInfo(
            key=object_key,
            content_type=stat.content_type,
            size=stat.size,
            etag=getattr(stat, "etag", None),
        )

    async def _ensure_bucket(self) -> None:
        exists = await run_in_threadpool(self.client.bucket_exists, self.bucket)
        if not exists:
            await run_in_threadpool(self.client.make_bucket, self.bucket)
