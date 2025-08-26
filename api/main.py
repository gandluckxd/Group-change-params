"""
Group Change Params API
FastAPI service for group parameter changes in Altawin orders
"""

import sys
import os

# Fix for --noconsole PyInstaller builds
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

from modules.routes import router
from modules.config import API_HOST, API_PORT

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Group Change Params API",
    description="API for group parameter changes in Altawin orders",
    version="1.0.0"
)

# Setup CORS for client communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "Group Change Params API",
        "status": "running",
        "version": "1.0.0",
        "description": "API for group parameter changes in Altawin orders"
    }


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=API_HOST, 
        port=API_PORT,
        log_level="info"
    )