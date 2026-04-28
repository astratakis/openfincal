"""
Core system operations for the FreeVO API.
"""

import logging
from fastapi import APIRouter
from src.config import config


router = APIRouter(prefix="/api/v1/system", tags=["System Operations"])

# pylint: disable=missing-function-docstring
# pylint: disable=duplicate-code

logger = logging.getLogger("uvicorn")


@router.get("/ping")
def ping():
    return "pong"


@router.get(
    "/info",
    summary="API Information",
    description="Basic information of the API, like version and docs location",
)
def info():
    return {
        "service": config.TITLE,
        "version": config.VERSION,
        "docs": "/docs",
    }
