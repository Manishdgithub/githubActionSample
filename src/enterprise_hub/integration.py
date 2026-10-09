import httpx
from enterprise_hub.config import settings

async def dispatch_webhook_event(event_type: str, payload: dict) -> bool:
    """Dispatches external webhook integration events with timeout protection."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.post(
                settings.third_party_payment_webhook_url,
                json={"event": event_type, "data": payload},
            )
            return resp.status_code in (200, 201, 202)
        except httpx.HTTPError:
            return False
