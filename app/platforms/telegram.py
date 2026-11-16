import httpx
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult
from app.config import get_settings


class TelegramPlatform(BasePlatform):
    def __init__(self):
        super().__init__("Telegram")
        self.settings = get_settings()
        self.base_url = "https://api.telegram.org/bot"

    async def post(self, message: str) -> PlatformResult:
        if not self._is_configured():
            return self._create_result(
                status="failed",
                error="Telegram Bot credentials not configured"
            )

        try:
            payload = {
                "chat_id": self.settings.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }

            response = await self.client.post(
                f"{self.base_url}{self.settings.telegram_bot_token}/sendMessage",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    message_id = data.get("result", {}).get("message_id")
                    posted_url = f"https://t.me/c/{str(self.settings.telegram_chat_id).replace('-100', '')}/{message_id}" if message_id else None
                    return self._create_result(
                        status="success",
                        posted_url=posted_url,
                        public_access=False
                    )
                else:
                    error_msg = data.get("description", "Unknown Telegram error")
                    return self._create_result(status="failed", error=error_msg)
            else:
                return self._create_result(status="failed", error=f"HTTP {response.status_code}")

        except httpx.RequestError as e:
            return self._create_result(status="failed", error=f"Network error: {str(e)}")
        except Exception as e:
            return self._create_result(status="failed", error=f"Unexpected error: {str(e)}")

    def _is_configured(self) -> bool:
        return bool(self.settings.telegram_bot_token and self.settings.telegram_chat_id)