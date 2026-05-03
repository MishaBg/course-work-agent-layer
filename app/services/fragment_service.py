from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.minio_client import FragmentObjectNotFoundError, MinioStorageClient
from app.integrations.transport_producer import TransportProducerGateway
from app.models.fragment_request import FragmentRequest, FragmentRequestStatus
from app.repositories.fragment_request_repository import FragmentRequestRepository
from app.repositories.user_repository import UserRepository
from app.repositories.video_fragment_repository import VideoFragmentRepository
from app.schemas.fragment import FragmentAccessResponse


class FragmentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.fragment_repo = VideoFragmentRepository(db)
        self.request_repo = FragmentRequestRepository(db)
        self.user_repo = UserRepository(db)
        self.minio_client = MinioStorageClient()
        self.producer = TransportProducerGateway()

    async def request_fragment(
        self,
        video_id: str,
        fragment_number: int,
        user_id: str,
    ) -> FragmentAccessResponse:
        await self.user_repo.get_or_create(user_id=user_id, username=f"user_{user_id[:8]}")
        fragment = await self.fragment_repo.get_by_video_and_number(video_id, fragment_number)

        request = FragmentRequest(
            user_id=user_id,
            requested_video_id=video_id,
            video_id=fragment.video_id if fragment else None,
            fragment_number=fragment_number,
            status=FragmentRequestStatus.ACCEPTED.value,
            storage_key=fragment.storage_key if fragment else None,
        )
        request = await self.request_repo.create(request)

        if fragment is None:
            request.status = FragmentRequestStatus.NOT_FOUND.value
            request.error_message = "Fragment metadata not found"
            request = await self.request_repo.update(request)
            await self.db.commit()
            return FragmentAccessResponse(
                request_id=request.id,
                status=request.status,
                video_id=video_id,
                fragment_number=fragment_number,
                message=request.error_message,
                created_at=request.created_at,
            )

        try:
            object_info = await self.minio_client.stat_fragment(fragment.storage_key)
            payload_bytes = await self.minio_client.get_fragment_bytes(fragment.storage_key)
            request.status = FragmentRequestStatus.FOUND.value
            request.error_message = None
            await self.producer.publish_fragment_request(
                request_id=request.id,
                user_id=user_id,
                fragment_number=fragment_number,
                payload_bytes=payload_bytes,
            )
        except FragmentObjectNotFoundError:
            request.status = FragmentRequestStatus.NOT_FOUND.value
            request.error_message = "Fragment object not found in MinIO"
            object_info = None
        except Exception as exc:
            request.status = FragmentRequestStatus.FAILED.value
            request.error_message = f"Failed to prepare fragment request: {exc}"
            object_info = None

        request = await self.request_repo.update(request)
        await self.db.commit()

        return FragmentAccessResponse(
            request_id=request.id,
            status=request.status,
            video_id=video_id,
            fragment_number=fragment_number,
            storage_key=fragment.storage_key,
            content_type=object_info.content_type if object_info else None,
            object_size=object_info.size if object_info else None,
            etag=object_info.etag if object_info else None,
            message=request.error_message,
            created_at=request.created_at,
        )
