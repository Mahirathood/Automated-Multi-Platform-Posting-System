from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.schemas import PostRequest, PostResponse, PlatformResult
from app.services.posting_service import PostingService
from app.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
posting_service = PostingService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Automated Multi-Platform Posting System")
    logger.info(f"Configured platforms: {posting_service.get_configured_platforms()}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="Automatically publishes messages across multiple third-party platforms via their APIs",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Automated Multi-Platform Posting System",
        "version": "1.0.0",
        "docs": "/docs",
        "configured_platforms": posting_service.get_configured_platforms(),
        "all_platforms": posting_service.get_all_platforms()
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}


@app.post("/posting", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def post_message(request: PostRequest):
    try:
        logger.info(f"Received posting request: {request.message[:50]}...")

        results = await posting_service.post_to_all_platforms(request.message)

        any_success = any(r.status == "success" for r in results)

        return PostResponse(
            success=any_success,
            results=results
        )

    except Exception as e:
        logger.error(f"Error processing posting request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )