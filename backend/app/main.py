from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.analysis import router as analysis_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.resume_sections import router as resume_sections_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(analysis_router, prefix="/api/v1", tags=["analysis"])
app.include_router(resumes_router, prefix="/api/v1", tags=["resumes"])
app.include_router(resume_sections_router, prefix="/api/v1", tags=["resumes"])


@app.get("/")
def home():
    return {"message": "FixMyResume Backend Running"}


@app.get("/test-db")
def test_db():
    return {"message": "Database connected successfully"}
