from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.auth_routes import router as auth_router
from app.routes.device_routes import router as device_router
from app.routes.log_routes import router as log_router
from app.routes.incident_routes import router as incident_router

app = FastAPI(
    title="NetOps Copilot 2026: AI-Enhanced Log Intelligence Platform",
    version="1.0.0",
    description="Backend API for authentication, device management, log ingestion, incident handling, and AI-assisted analysis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"success": True, "message": "NetOps Copilot 2026 API is running"}

@app.get("/health")
def health():
    return {"success": True, "message": "Healthy"}

app.include_router(auth_router)
app.include_router(device_router)
app.include_router(log_router)
app.include_router(incident_router)