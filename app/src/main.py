"""
Main entry point for the FreeVo API application.

This module initializes the FastAPI application, configures CORS middleware,
and starts the Uvicorn server.
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import config

# Import routers
from src.routers import core

logger = logging.getLogger("uvicorn")

# pylint: disable=unused-argument
# pylint: disable=missing-function-docstring

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting application")

    yield

    logger.info("Shutting down application")


# Create the FastAPI application and configure CORS middleware
api = FastAPI(
    title=config.TITLE,
    version=config.VERSION,
    root_path=config.CONTEXT_PATH,
    lifespan=lifespan,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        config.FRONTEND_EXT_URL,
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
        "PATCH",
    ],
    allow_headers=["*"],
    expose_headers=["Content-Length"],
)

# Attach routers to the main application
api.include_router(core.router)

if __name__ == "__main__":
    # Run Uvicorn programmatically using the configuration
    uvicorn.run(
        "main:api",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )
