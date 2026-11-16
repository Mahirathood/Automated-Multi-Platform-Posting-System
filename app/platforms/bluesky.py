import httpx
from typing import Optional
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import get_settings


class BlueskyPlatform(BasePlatform):
    def __init__(self):
        super().__init__("Bluesky")
        self.settings = get_settings()
        self.base_url = "https://bsky.social/xrpc"
        self._access_token: Optional[str] = None
        self._did: Optional[str] = None

    async def post(self, message: str) -> PlatformResult:
        if not self._is_configured():
            return self._create_result(
                status="failed",
                error="Bluesky credentials not configured"
            )

        try:
            if not await self._authenticate():
                return self._create_result(status="failed", error="Bluesky authentication failed")

            urls = __import__('re').findall(r'https?://[^\s]+', message)
            url = urls[0] if urls else ""

            payload = {
                "repo": self._did,
                "collection": "app.bsky.feed.post",
                "record": {
                    "$type": "app.bsky.feed.post",
                    "text": message,
                    "createdAt": __import__('datetime').datetime.now().isoformat() + "Z",
                    "facets": self._create_facets(message, url) if url else []
                }
            }

            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json"
            }

            response = await self.client.post(
                f"{self.base_url}/com.atproto.repo.createRecord",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                uri = data.get("uri")
                post_url = f"https://bsky.app/profile/{self._did}/post/{uri.split('/')[-1]}" if uri else None
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

    async def _authenticate(self) -> bool:
        if self._access_token:
            return True

        try:
            payload = {
                "identifier": self.settings.bluesky_identifier,
                "password": self.settings.bluesky_password
            }
            response = await self.client.post(
                f"{self.base_url}/com.atproto.server.createSession",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                self._access_token = data.get("accessJwt")
                self._did = data.get("did")
                return True
        except Exception:
            pass
        return False

    def _create_facets(self, text: str, url: str) -> list:
        byte_start = text.encode().find(url.encode())
        if byte_start == -1:
            return []
        byte_end = byte_start + len(url.encode())
        return [{
            "index": {"byteStart": byte_start, "byteEnd": byte_end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}]
        }]

    def _is_configured(self) -> bool:
        return bool(self.settings.bluesky_identifier and self.settings.bluesky_password)