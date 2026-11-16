from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, field_validator
import re


class PostRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=200, description="Message to post (max 200 characters)")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        urls = re.findall(r'https?://[^\s]+', v)
        if len(urls) != 1:
            raise ValueError("Message must contain exactly one CTA link (URL)")
        url = urls[0]
        if not re.match(r'^https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?$', url):
            raise ValueError("Invalid URL format")
        return v


class PlatformResult(BaseModel):
    platform: str
    status: str = Field(..., pattern="^(success|failed)$")
    posted_url: Optional[HttpUrl] = None
    public_access: bool = False
    date: Optional[str] = None
    time: Optional[str] = None
    error: Optional[str] = None


class PostResponse(BaseModel):
    success: bool
    results: List[PlatformResult]