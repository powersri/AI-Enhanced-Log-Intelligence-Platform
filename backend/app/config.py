
# Import Pydantic's BaseSettings for environment-based config management
from pydantic_settings import BaseSettings

# Main settings class for application configuration
class Settings(BaseSettings):
    # ============= Database Configuration =============
    # MongoDB connection URL (default: local instance)
    MONGODB_URL: str = "mongodb://localhost:27017"
    # MongoDB database name
    MONGODB_DB: str = "netops_copilot"

    # ============= JWT Configuration =============
    # Secret key for JWT signing (must be set in .env)
    JWT_SECRET_KEY: str
    # Algorithm used for JWT
    JWT_ALGORITHM: str = "HS256"
    # Access token expiration time in minutes
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ============= Frontend Configuration =============
    # Allowed origins for CORS (comma-separated in .env)
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ============= AI / RAG Service Configuration =============
    # API key for Gemini (used for embeddings / AI analysis)
    GEMINI_API_KEY: str | None = None
    RAG_KNOWLEDGE_DIR: str = "app/rag/knowledge_base"

    # ============= App Behavior Configuration =============
    # Enable debug mode (can be set to False in production)
    DEBUG: bool = True
    # Log level for the application
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    # Configuration for loading environment variables from .env file
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instantiate the settings object (loads values from environment or .env)
settings = Settings()