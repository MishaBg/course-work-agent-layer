import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.minio_client import MinioStorageClient
from app.models.video import Video, VideoStatus
from app.models.video_fragment import VideoFragment
from app.repositories.user_repository import UserRepository
from app.repositories.video_fragment_repository import VideoFragmentRepository
from app.repositories.video_repository import VideoRepository
from app.schemas.video import VideoFragmentMeta, VideoIngestResponse


class VideoIngestService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.video_repo = VideoRepository(db)
        self.fragment_repo = VideoFragmentRepository(db)
        self.minio_client = MinioStorageClient()

    async def ingest_video(
        self,
        user_id: str,
        title: str,
        description: str | None,
        file: UploadFile,
    ) -> VideoIngestResponse:
        if file.content_type != "video/mp4":
            raise ValueError("Only video/mp4 uploads are supported")

        await self.user_repo.get_or_create(user_id=user_id, username=f"user_{user_id[:8]}")

        video = await self.video_repo.create(
            Video(
                title=title,
                description=description,
                original_filename=file.filename or "uploaded_video.mp4",
                content_type=file.content_type,
                status=VideoStatus.PROCESSING.value,
                uploaded_by_user_id=user_id,
            )
        )

        uploaded_keys: list[str] = []
        created_fragments: list[VideoFragment] = []

        try:
            with TemporaryDirectory(prefix="video_ingest_") as tmp_dir:
                tmp_dir_path = Path(tmp_dir)
                source_path = tmp_dir_path / (file.filename or "source.mp4")
                segments_dir = tmp_dir_path / "segments"
                segments_dir.mkdir(parents=True, exist_ok=True)

                await self._save_upload_file(file, source_path)
                duration = self._probe_duration_seconds(source_path)
                segment_paths = self._split_video_to_minute_segments(source_path, segments_dir)

                for index, segment_path in enumerate(segment_paths, start=1):
                    storage_key = f"videos/{video.id}/fragments/{index:04d}.mp4"
                    uploaded = await self.minio_client.upload_fragment_file(storage_key, segment_path)
                    uploaded_keys.append(storage_key)

                    fragment = VideoFragment(
                        video_id=video.id,
                        fragment_number=index,
                        storage_key=storage_key,
                        content_type=uploaded.content_type or "video/mp4",
                        size_bytes=uploaded.size,
                        duration_seconds=60,
                        etag=uploaded.etag,
                    )
                    created_fragments.append(fragment)

                await self.fragment_repo.create_many(created_fragments)

                video.duration_seconds = duration
                video.total_fragments = len(created_fragments)
                video.status = VideoStatus.READY.value
                await self.video_repo.update(video)

                await self.db.commit()

                return VideoIngestResponse(
                    video_id=video.id,
                    title=video.title,
                    description=video.description,
                    original_filename=video.original_filename,
                    content_type=video.content_type,
                    duration_seconds=video.duration_seconds,
                    total_fragments=video.total_fragments,
                    status=video.status,
                    created_at=video.created_at,
                    fragments=[
                        VideoFragmentMeta(
                            fragment_number=fragment.fragment_number,
                            storage_key=fragment.storage_key,
                            content_type=fragment.content_type,
                            size_bytes=fragment.size_bytes,
                            duration_seconds=fragment.duration_seconds,
                            etag=fragment.etag,
                        )
                        for fragment in created_fragments
                    ],
                )
        except Exception:
            video.status = VideoStatus.FAILED.value
            await self.video_repo.update(video)
            await self.db.commit()
            await self._cleanup_uploaded_fragments(uploaded_keys)
            raise

    async def _save_upload_file(self, upload_file: UploadFile, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        await upload_file.close()

    def _probe_duration_seconds(self, source_path: Path) -> int | None:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(source_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return None
        output = result.stdout.strip()
        if not output:
            return None
        return int(float(output))

    def _split_video_to_minute_segments(self, source_path: Path, segments_dir: Path) -> list[Path]:
        output_pattern = str(segments_dir / "fragment_%04d.mp4")
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source_path),
            "-map",
            "0",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-f",
            "segment",
            "-segment_time",
            "60",
            "-reset_timestamps",
            "1",
            output_pattern,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg split failed: {result.stderr.strip()}")

        segment_paths = sorted(segments_dir.glob("fragment_*.mp4"))
        if not segment_paths:
            raise RuntimeError("No fragments were produced by ffmpeg")
        return segment_paths

    async def _cleanup_uploaded_fragments(self, keys: list[str]) -> None:
        for key in keys:
            try:
                await self.minio_client.remove_fragment(key)
            except Exception:
                continue
