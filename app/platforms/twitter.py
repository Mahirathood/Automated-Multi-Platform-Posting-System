import httpx
from typing import Optional
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import get_settings


class TwitterPlatform(BasePlatform):
    def __init__(self):
        super().__init__("Twitter/X")
        self.settings = get_settings()
        self.base_url = "https://api.twitter.com/2"

    async def post(self, message: str) -> PlatformResult:
        if not self._is_configured():
            return self._create_result(
                status="failed",
                error="Twitter API credentials not configured"
            )

        try:
            headers = {
                "Authorization": f"Bearer {self.settings.twitter_bearer_token}",
                "Content-Type": "application/json"
            }
            payload = {"text": message}

            response = await self.client.post(
                f"{self.base_url}/tweets",
                headers=headers,
                json=payload
            )

            if response.status_code == 201:
                data = response.json()
                tweet_id = data.get("data", {}).get("id")
                posted_url = f"https://twitter.com/user/status/{tweet_id}" if tweet_id else None
                return self._create_result(
                    status="success",
                    posted_url=posted_url,
                    public_access=True
                )
            else:
                error_data = response.json()
                error_msg = error_data.get("detail", f"HTTP {response.status_code}")
                return self._create_result(status="failed", error=error_msg)

        except httpx.RequestError as e:
            return self._create_result(status="failed", error=f"Network error: {str(e)}")
        except Exception as e:
            return self._create_result(status="failed", error=f"Unexpected error: {str(e)}")

    def _is_configured(self) -> bool:
        return bool(self.settings.twitter_bearer_token)