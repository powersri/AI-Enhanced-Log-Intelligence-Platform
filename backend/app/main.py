
# Import FastAPI and CORS middleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routers for different resource domains
from app.routes.auth_routes import router as auth_router
from app.routes.device_routes import router as device_router
from app.routes.log_routes import router as log_router
from app.routes.incident_routes import router as incident_router

# Create the FastAPI application instance with metadata
app = FastAPI(
    title="NetOps Copilot 2026",
    version="1.0.0",
    description="AI-Enhanced Log Intelligence Platform backend",
)

# Add CORS middleware to allow frontend (e.g., Vite/React) to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for API welcome message
@app.get("/")
def root():
    return {"success": True, "message": "NetOps Copilot 2026 API is running"}

# Health check endpoint for monitoring
@app.get("/health")
def health():
    return {"success": True, "message": "Healthy"}

# Register routers for authentication, devices, logs, and incidents
app.include_router(auth_router)
app.include_router(device_router)
app.include_router(log_router)
app.include_router(incident_router)
