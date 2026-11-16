import httpx
from typing import Optional
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import get_settings


class RedditPlatform(BasePlatform):
    def __init__(self):
        super().__init__("Reddit")
        self.settings = get_settings()
        self.base_url = "https://oauth.reddit.com"
        self.auth_url = "https://www.reddit.com/api/v1/access_token"
        self._access_token: Optional[str] = None

    async def post(self, message: str) -> PlatformResult:
        if not self._is_configured():
            return self._create_result(
                status="failed",
                error="Reddit API credentials not configured"
            )

        try:
            token = await self._get_access_token()
            if not token:
                return self._create_result(status="failed", error="Failed to obtain Reddit access token")

            headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": self.settings.reddit_user_agent or "AutomatedPosting/1.0"
            }

            urls = __import__('re').findall(r'https?://[^\s]+', message)
            url = urls[0] if urls else ""
            text_content = message.replace(url, "").strip()

            payload = {
                "sr": "test",
                "kind": "link",
                "title": text_content[:300] if text_content else "Shared Link",
                "url": url,
                "resubmit": True,
                "sendreplies": True
            }

            response = await self.client.post(
                f"{self.base_url}/api/submit",
                headers=headers,
                data=payload
            )

            if response.status_code == 200:
                data = response.json()
                post_data = data.get("json", {}).get("data", {})
                post_id = post_data.get("id") or post_data.get("name")
                posted_url = f"https://reddit.com/{post_id}" if post_id else None
                return self._create_result(
                    status="success",
                    posted_url=posted_url,
                    public_access=True
                )
            else:
                error_msg = response.text
                return self._create_result(status="failed", error=f"HTTP {response.status_code}: {error_msg}")

        except httpx.RequestError as e:
            return self._create_result(status="failed", error=f"Network error: {str(e)}")
        except Exception as e:
            return self._create_result(status="failed", error=f"Unexpected error: {str(e)}")

    async def _get_access_token(self) -> Optional[str]:
        if self._access_token:
            return self._access_token

        try:
            auth = (self.settings.reddit_client_id, self.settings.reddit_client_secret)
            data = {
                "grant_type": "password",
                "username": self.settings.reddit_username,
                "password": self.settings.reddit_password
            }
            headers = {"User-Agent": self.settings.reddit_user_agent or "AutomatedPosting/1.0"}

            response = await self.client.post(
                self.auth_url,
                auth=auth,
                data=data,
                headers=headers
            )

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                return self._access_token
        except Exception:
            pass
        return None

    def _is_configured(self) -> bool:
        return bool(
            self.settings.reddit_client_id and
            self.settings.reddit_client_secret and
            self.settings.reddit_username and
            self.settings.reddit_password
        )