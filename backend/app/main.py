from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.device_routes import router as device_router
from app.routes.log_routes import router as log_router
from app.routes.incident_routes import router as incident_router

app = FastAPI(
    title="NetOps Copilot 2026",
    version="1.0.0",
    description="AI-Enhanced Log Intelligence Platform backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
