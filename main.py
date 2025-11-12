"""
FastAPI Server - Modern Full-Stack Application
Serves both API and Static Frontend
"""

import warnings
warnings.filterwarnings("ignore", message=".*Pydantic V1 functionality.*")
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import List, Dict
from pathlib import Path

# Load environment variables
load_dotenv()

# Load config
from config import settings

# MongoDB helpers
def get_db():
    client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    return client[settings.MONGODB_DATABASE]

# Create FastAPI app with proper config
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def frontend_home(request: Request):
    """Serve the main frontend application"""
    return templates.TemplateResponse("crud_interface.html", {"request": request})

@app.get("/health", response_class=JSONResponse)
async def health_check():
    """API Health check"""
    return {"status": "healthy", "server": "FastAPI + Static Frontend"}

# Additional API Routes
@app.get("/api/info")
async def api_info():
    """Get API information"""
    return {"message": "KJC Python Server API running!", "version": "2.0.0", "type": "FastAPI + Static"}

@app.get("/api/data")
async def get_data():
    """Sample data endpoint"""
    return {
        "data": ["item1", "item2", "item3"],
        "count": 3
    }

@app.get("/mongodb/test")
async def test_mongodb():
    try:
        # Kết nối MongoDB Atlas từ env
        mongodb_url = os.getenv("MONGODB_URL")
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        
        # Test database
        db_name = os.getenv("MONGODB_DATABASE", "kjc-group-staging")
        db = client[db_name]
        collection = db.api_test
        
        # Insert test data
        test_doc = {"message": "Hello MongoDB", "timestamp": datetime.now()}
        result = collection.insert_one(test_doc)
        
        # Read back
        found_doc = collection.find_one({"_id": result.inserted_id})
        found_doc["_id"] = str(found_doc["_id"])  # Convert ObjectId to string
        
        client.close()
        
        return {
            "status": "success",
            "mongodb_connected": True,
            "inserted_id": str(result.inserted_id),
            "document": found_doc
        }
    except Exception as e:
        return {
            "status": "error",
            "mongodb_connected": False,
            "error": str(e)
        }



# Import botnet routes
from botnet_routes import router as botnet_router
app.include_router(botnet_router, prefix="/api", tags=["API"])

# Development server
if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌐 Frontend: http://localhost:{settings.PORT}")  
    print(f"📖 API Docs: http://localhost:{settings.PORT}/docs")
    print(f"🔗 ReDoc: http://localhost:{settings.PORT}/redoc")
    
    uvicorn.run(
        "main:app", 
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )