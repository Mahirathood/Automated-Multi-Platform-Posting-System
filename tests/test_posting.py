import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import PostRequest, PlatformResult
from app.services.posting_service import PostingService
from app.platforms.base import BasePlatform


client = TestClient(app)


class MockPlatform(BasePlatform):
    def __init__(self, name: str, should_succeed: bool = True):
        super().__init__(name)
        self.should_succeed = should_succeed

    async def post(self, message: str) -> PlatformResult:
        if self.should_succeed:
            return self._create_result(
                status="success",
                posted_url=f"https://{self.name.lower()}.com/post/123",
                public_access=True
            )
        else:
            return self._create_result(
                status="failed",
                error="Mock error"
            )

    def _is_configured(self) -> bool:
        return True


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_valid_post_request():
    response = client.post("/posting", json={"message": "Check out our platform! https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0


def test_invalid_message_too_long():
    long_message = "a" * 201 + " https://example.com"
    response = client.post("/posting", json={"message": long_message})
    assert response.status_code == 422


def test_invalid_message_no_url():
    response = client.post("/posting", json={"message": "This message has no URL"})
    assert response.status_code == 422


def test_invalid_message_multiple_urls():
    response = client.post("/posting", json={"message": "Check https://example.com and https://another.com"})
    assert response.status_code == 422


def test_invalid_message_invalid_url():
    response = client.post("/posting", json={"message": "Check out https://not-a-valid-url"})
    assert response.status_code == 422


def test_empty_message():
    response = client.post("/posting", json={"message": ""})
    assert response.status_code == 422


def test_post_request_schema_validation():
    valid_request = PostRequest(message="Hello world https://example.com")
    assert valid_request.message == "Hello world https://example.com"

    with pytest.raises(ValueError):
        PostRequest(message="No URL here")

    with pytest.raises(ValueError):
        PostRequest(message="Two URLs https://a.com https://b.com")


def test_posting_service_initialization():
    service = PostingService()
    platforms = service.get_all_platforms()
    assert len(platforms) >= 5
    assert "Twitter/X" in platforms
    assert "LinkedIn" in platforms
    assert "Facebook" in platforms
    assert "Reddit" in platforms
    assert "Telegram" in platforms


def test_platform_result_schema():
    result = PlatformResult(
        platform="Test Platform",
        status="success",
        posted_url="https://example.com/post/123",
        public_access=True,
        date="2026-11-15",
        time="10:30:00",
        error=None
    )
    assert result.platform == "Test Platform"
    assert result.status == "success"
    assert str(result.posted_url) == "https://example.com/post/123"
    assert result.public_access is True


def test_mock_platform_success():
    import asyncio
    platform = MockPlatform("TestPlatform", should_succeed=True)
    result = asyncio.run(platform.post("Test message https://example.com"))
    assert result.status == "success"
    assert result.posted_url is not None
    assert result.public_access is True
    platform.close()


def test_mock_platform_failure():
    import asyncio
    platform = MockPlatform("TestPlatform", should_succeed=False)
    result = asyncio.run(platform.post("Test message https://example.com"))
    assert result.status == "failed"
    assert result.error == "Mock error"
    platform.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])