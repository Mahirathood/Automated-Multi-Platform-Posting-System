import httpx
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import get_settings


class FacebookPlatform(BasePlatform):
    def __init__(self):
        super().__init__("Facebook")
        self.settings = get_settings()
        self.base_url = "https://graph.facebook.com/v19.0"

    async def post(self, message: str) -> PlatformResult:
        if not self._is_configured():
            return self._create_result(
                status="failed",
                error="Facebook API credentials not configured"
            )

        try:
            payload = {
                "message": message,
                "access_token": self.settings.facebook_access_token
            }

            response = await self.client.post(
                f"{self.base_url}/{self.settings.facebook_page_id}/feed",
                data=payload
            )

            if response.status_code == 200:
                data = response.json()
                post_id = data.get("id")
                posted_url = f"https://www.facebook.com/{post_id}" if post_id else None
                return self._create_result(
                    status="success",
                    posted_url=posted_url,
                    public_access=True
                )
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                return self._create_result(status="failed", error=error_msg)

        except httpx.RequestError as e:
            return self._create_result(status="failed", error=f"Network error: {str(e)}")
        except Exception as e:
            return self._create_result(status="failed", error=f"Unexpected error: {str(e)}")

    def _is_configured(self) -> bool:
        return bool(self.settings.facebook_access_token and self.settings.facebook_page_id)