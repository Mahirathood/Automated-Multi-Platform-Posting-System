import httpx
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import get_settings


class MastodonPlatform(BasePlatform):
    def __init__(self):
        super().__init__("Mastodon")
        self.settings = get_settings()

    async def post(self, message: str) -> PlatformResult:
        if not self._is_configured():
            return self._create_result(
                status="failed",
                error="Mastodon credentials not configured"
            )

        try:
            headers = {
                "Authorization": f"Bearer {self.settings.mastodon_access_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "status": message,
                "visibility": "public"
            }

            response = await self.client.post(
                f"{self.settings.mastodon_instance_url}/api/v1/statuses",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                post_url = data.get("url")
                return self._create_result(
                    status="success",
                    posted_url=post_url,
                    public_access=True
                )
            else:
                error_msg = response.text
                return self._create_result(status="failed", error=f"HTTP {response.status_code}: {error_msg}")

        except httpx.RequestError as e:
            return self._create_result(status="failed", error=f"Network error: {str(e)}")
        except Exception as e:
            return self._create_result(status="failed", error=f"Unexpected error: {str(e)}")

    def _is_configured(self) -> bool:
        return bool(self.settings.mastodon_instance_url and self.settings.mastodon_access_token)