"""
Configuration management for DevMind Backend
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application Settings
    app_name: str = "DevMind API"
    debug: bool = False
    version: str = "1.0.0"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Settings
    database_url: str = "postgresql+asyncpg://devmind:devmind@localhost/devmind"
    
    # Vector Database Settings
    vector_dimension: int = 384  # sentence-transformers dimension
    
    # AI Services
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Integration APIs
    github_token: Optional[str] = None
    slack_token: Optional[str] = None
    jira_url: Optional[str] = None
    jira_username: Optional[str] = None
    jira_token: Optional[str] = None
    
    # Redis for caching and real-time features
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS Settings
    allowed_origins: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # MCP Settings
    mcp_server_name: str = "devmind-context-server"
    mcp_server_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Environment-specific configurations
def get_database_url() -> str:
    """Get the appropriate database URL based on environment"""
    if settings.debug:
        return "postgresql+asyncpg://devmind:devmind@localhost/devmind_dev"
    return settings.database_url

def get_cors_origins() -> list:
    """Get CORS origins based on environment"""
    if settings.debug:
        return ["*"]  # Allow all origins in development
    return settings.allowed_origins