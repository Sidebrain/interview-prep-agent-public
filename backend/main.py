from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import logging
import os, sys

from app.api.v1.router import router as api_v1_router
from app.api.v2.router import router as api_v2_router


def verify_secrets():
    required_secrets = ["OPENAI_API_KEY", "STRIPE_API_KEY"]
    missing_secrets = [
        secret for secret in required_secrets if not os.environ.get(secret)
    ]

    if missing_secrets:
        print(f"Missing required secrets: {missing_secrets}")
        sys.exit(1)

    print("All required secrets present")


verify_secrets()

app = FastAPI()

# Set up basic logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_requests(request: Request, call_next):
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


@app.get("/")
async def index() -> dict:
    return {"Hello": "World"}
