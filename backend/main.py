from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
from app.api.v1.router import router as api_v1_router
from app.api.v2.router import router as api_v2_router
import logging

app = FastAPI()

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    # allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_v1_router, prefix="/api/v1", tags=["v1"])
app.include_router(api_v2_router, prefix="/api/v2", tags=["v2"])


@app.get("/")
async def index() -> dict:
    return {"Hello": "World"}
