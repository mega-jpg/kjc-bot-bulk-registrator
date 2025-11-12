# FastAPI Configuration
import os
from pathlib import Path

class Settings:
    # App info
    APP_NAME = "KJC Testing API"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "FastAPI + Static Frontend - Modern Full-Stack Application"
    
    # Server config
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True
    
    # Database
    MONGODB_URL = os.getenv("MONGODB_URL")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "kjc-group-staging")
    
    # Directories
    BASE_DIR = Path(__file__).parent
    STATIC_DIR = BASE_DIR / "static" 
    TEMPLATES_DIR = BASE_DIR / "templates"
    
    # CORS
    CORS_ORIGINS = ["*"]
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

settings = Settings()