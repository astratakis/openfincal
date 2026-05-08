"""
Main entry point for the FreeVo API application.

This module initializes the FastAPI application, configures CORS middleware,
and starts the Uvicorn server.
"""

import logging
import socket
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from src.backend.postgres import POSTGRES_ASYNC_ENGINE, PostgresConnectionSingleton
from src.backend.redis import REDIS
from src.config import config

# Import routers
from src.routers import core

logger = logging.getLogger("uvicorn")

# pylint: disable=unused-argument


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Docstring for lifespan

    :param app: Description
    :type app: FastAPI
    """

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    logger.info("<<<<<<<<<<<<<<< WELCOME %s >>>>>>>>>>>>>>>", ip_address)

    logger.info("App startup: Initializing DB")
    eng = POSTGRES_ASYNC_ENGINE()
    async with eng.connect() as conn:
        await conn.execute(text("SELECT 1"))  # Test connection
    logger.info("DB connection OK")

    logger.info("App startup: Initializing Redis")

    REDIS.set(ip_address, "test")
    assert REDIS.get(ip_address) == "test", "Failed to set/get value from Redis"
    REDIS.delete(ip_address)
    logger.info("Redis connection OK")

    yield

    logger.info("App shutdown: Closing connections...")
    await PostgresConnectionSingleton.close()
    logger.info("DB connections closed")


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
