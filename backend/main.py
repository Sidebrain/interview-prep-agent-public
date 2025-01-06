import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator, Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.api.v2.router import router as api_v2_router
from app.api.v3.router import router as api_v3_router
from app.services import setup_logging


def verify_secrets() -> None:
    required_secrets = ["OPENAI_API_KEY", "STRIPE_API_KEY"]
    missing_secrets = [
        secret
        for secret in required_secrets
        if not os.environ.get(secret)
    ]

    if missing_secrets:
        print(f"Missing required secrets: {missing_secrets}")
        sys.exit(1)

    print("All required secrets present")


verify_secrets()


# Set up logging
setup_logging(debug=True)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # will use this to setup beanie
    yield

    # cleanup beanie


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


CLIENT_URL = os.getenv("CLIENT_URL", "http://localhost:3000")
allowed_origins = [CLIENT_URL, "http://localhost:3000"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_v1_router, prefix="/api/v1", tags=["v1"])
app.include_router(api_v2_router, prefix="/api/v2", tags=["v2"])
app.include_router(api_v3_router, prefix="/api/v3", tags=["v3"])


@app.get("/")
async def index() -> dict[str, str]:
    return {"Hello": "World"}
