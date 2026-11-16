import httpx
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import get_settings


class DiscordPlatform(BasePlatform):
    def __init__(self):
        super().__init__("Discord")
        self.settings = get_settings()

    async def post(self, message: str) -> PlatformResult:
        if not self._is_configured():
            return self._create_result(
                status="failed",
                error="Discord Webhook URL not configured"
            )

        try:
            payload = {
                "content": message,
                "username": "Automated Posting Bot"
            }

            response = await self.client.post(
                self.settings.discord_webhook_url,
                json=payload
            )

            if response.status_code in (200, 204):
                return self._create_result(
                    status="success",
                    posted_url=self.settings.discord_webhook_url,
                    public_access=False
                )
            else:
                error_msg = response.text
                return self._create_result(status="failed", error=f"HTTP {response.status_code}: {error_msg}")

        except httpx.RequestError as e:
            return self._create_result(status="failed", error=f"Network error: {str(e)}")
        except Exception as e:
            return self._create_result(status="failed", error=f"Unexpected error: {str(e)}")

    def _is_configured(self) -> bool:
        return bool(self.settings.discord_webhook_url)