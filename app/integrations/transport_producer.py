import base64
import logging
from datetime import datetime, timezone

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class TransportProducerGateway:
    async def publish_fragment_request(
        self,
        request_id: str,
        user_id: str,
        fragment_number: int,
        payload_bytes: bytes,
    ) -> None:
        payload = {
            "request_id": request_id,
            "username": user_id,
            "fragment_number": fragment_number,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "payload": base64.b64encode(payload_bytes).decode("utf-8"),
        }

        url = f"{settings.transport_service_url.rstrip('/')}{settings.transport_send_path}"
        timeout = httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        logger.info(
            "Transport publish ok: request_id=%s user_id=%s fragment=%s bytes=%s",
            request_id,
            user_id,
            fragment_number,
            len(payload_bytes),
        )
