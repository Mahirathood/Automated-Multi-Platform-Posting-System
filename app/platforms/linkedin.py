import httpx
from typing import Optional
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import get_settings


class LinkedInPlatform(BasePlatform):
    def __init__(self):
        super().__init__("LinkedIn")
        self.settings = get_settings()
        self.base_url = "https://api.linkedin.com/v2"

    async def post(self, message: str) -> PlatformResult:
        if not self._is_configured():
            return self._create_result(
                status="failed",
                error="LinkedIn API credentials not configured"
            )

        try:
            headers = {
                "Authorization": f"Bearer {self.settings.linkedin_access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            person_urn = await self._get_person_urn(headers)
            if not person_urn:
                return self._create_result(status="failed", error="Could not retrieve LinkedIn person URN")

            payload = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": message},
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
            }

            response = await self.client.post(
                f"{self.base_url}/ugcPosts",
                headers=headers,
                json=payload
            )

            if response.status_code == 201:
                data = response.json()
                post_id = data.get("id")
                posted_url = f"https://www.linkedin.com/feed/update/{post_id}" if post_id else None
                return self._create_result(
                    status="success",
                    posted_url=posted_url,
                    public_access=True
                )
            else:
                error_data = response.json()
                error_msg = error_data.get("message", f"HTTP {response.status_code}")
                return self._create_result(status="failed", error=error_msg)

        except httpx.RequestError as e:
            return self._create_result(status="failed", error=f"Network error: {str(e)}")
        except Exception as e:
            return self._create_result(status="failed", error=f"Unexpected error: {str(e)}")

    async def _get_person_urn(self, headers: dict) -> Optional[str]:
        try:
            response = await self.client.get(
                f"{self.base_url}/userinfo",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                return f"urn:li:person:{data.get('sub')}"
        except Exception:
            pass
        return None

    def _is_configured(self) -> bool:
        return bool(self.settings.linkedin_access_token)