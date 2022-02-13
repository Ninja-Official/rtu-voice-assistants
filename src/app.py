from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import PROJECT_NAME, API_V1_PREFIX
from src.api.v1.routes import router as api_router

app = FastAPI(title=PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=API_V1_PREFIX)
