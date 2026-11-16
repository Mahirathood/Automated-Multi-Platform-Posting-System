from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from app.schemas import PlatformResult
import httpx


class BasePlatform(ABC):
    def __init__(self, name: str):
        self.name = name
        self.client = httpx.AsyncClient(timeout=30.0)

    @abstractmethod
    async def post(self, message: str) -> PlatformResult:
        pass

    def _create_result(
        self,
        status: str,
        posted_url: Optional[str] = None,
        public_access: bool = False,
        error: Optional[str] = None
    ) -> PlatformResult:
        now = datetime.now()
        return PlatformResult(
            platform=self.name,
            status=status,
            posted_url=posted_url,
            public_access=public_access,
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            error=error
        )

    async def close(self):
        await self.client.aclose()