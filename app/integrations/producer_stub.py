import logging

logger = logging.getLogger(__name__)


class ProducerGatewayStub:
    async def publish_fragment_request(
        self,
        request_id: str,
        user_id: str,
        video_id: str,
        fragment_number: int,
        storage_key: str,
    ) -> None:
        logger.info(
            "Producer stub publish: request_id=%s user_id=%s video_id=%s fragment=%s key=%s",
            request_id,
            user_id,
            video_id,
            fragment_number,
            storage_key,
        )
