
# Import Pydantic's BaseSettings for environment-based config management
from pydantic_settings import BaseSettings



# Main settings class for application configuration
class Settings(BaseSettings):
    # MongoDB connection URL (default: local instance)
    MONGODB_URL: str = "mongodb://localhost:27017"
    # MongoDB database name
    MONGODB_DB: str = "netops_copilot"
    # Secret key for JWT signing (must be set in .env)
    JWT_SECRET_KEY: str
    # Algorithm used for JWT
    JWT_ALGORITHM: str = "HS256"
    # Access token expiration time in minutes
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configuration for loading environment variables from .env file
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"



# Instantiate the settings object (loads values from environment or .env)
settings = Settings()