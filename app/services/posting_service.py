from typing import List
import asyncio
from app.platforms import (
    TwitterPlatform,
    LinkedInPlatform,
    FacebookPlatform,
    RedditPlatform,
    TelegramPlatform,
    DiscordPlatform,
    MastodonPlatform,
    BlueskyPlatform,
)
from app.schemas import PlatformResult
from app.config import get_settings


class PostingService:
    def __init__(self):
        self.settings = get_settings()
        self.platforms = self._initialize_platforms()

    def _initialize_platforms(self) -> List:
        return [
            TwitterPlatform(),
            LinkedInPlatform(),
            FacebookPlatform(),
            RedditPlatform(),
            TelegramPlatform(),
            DiscordPlatform(),
            MastodonPlatform(),
            BlueskyPlatform(),
        ]

    async def post_to_all_platforms(self, message: str) -> List[PlatformResult]:
        tasks = [platform.post(message) for platform in self.platforms]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    PlatformResult(
                        platform=self.platforms[i].name,
                        status="failed",
                        posted_url=None,
                        public_access=False,
                        date=None,
                        time=None,
                        error=f"Exception: {str(result)}"
                    )
                )
            else:
                processed_results.append(result)

        for platform in self.platforms:
            await platform.close()

        return processed_results

    def get_configured_platforms(self) -> List[str]:
        return [p.name for p in self.platforms if p._is_configured()]

    def get_all_platforms(self) -> List[str]:
        return [p.name for p in self.platforms]