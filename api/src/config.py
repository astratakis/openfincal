"""
Configuration module for the FastAPI application.
This module defines the Configuration dataclass that loads settings from environment variables.
"""

import logging
import os
import sys
from dataclasses import dataclass

logger = logging.getLogger("uvicorn")


@dataclass
class Configuration:
    """
    Configuration class that loads settings from environment variables.
    """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=invalid-name

    # Environment
    ENV: str = os.getenv("ENV", None)
    VERSION: str = os.getenv("VERSION", "1.0.0")
    TITLE: str = os.getenv("TITLE", "API")

    FRONTEND_COOKIE_SECURE: bool = os.getenv("FRONTEND_COOKIE_SECURE") == "true"
    FRONTEND_COOKIE_SAMESITE: str = os.getenv("FRONTEND_COOKIE_SAMESITE", None)
    FRONTEND_EXT_URL: str = os.getenv("FRONTEND_EXT_URL", None)

    # Database Configuration
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", None)
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", None)
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", None)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", None)
    POSTGRES_POOL_SIZE: int = int(os.getenv("POSTGRES_POOL_SIZE", "10"))
    POSTGRES_MAX_OVERFLOW: int = int(os.getenv("POSTGRES_MAX_OVERFLOW", "20"))

    # Keycloak Configuration
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", None)
    KEYCLOAK_EXT_URL: str = os.getenv("KEYCLOAK_EXT_URL", None)
    KEYCLOAK_ISSUER_URL: str = os.getenv("KEYCLOAK_ISSUER_URL", None)
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", None)
    POST_LOGOUT_REDIRECT_URI: str = os.getenv("POST_LOGOUT_REDIRECT_URI", None)

    KEYCLOAK_FRONTEND_CLIENT_ID: str = os.getenv("KEYCLOAK_FRONTEND_CLIENT_ID", None)
    KEYCLOAK_BACKEND_CLIENT_ID: str = os.getenv("KEYCLOAK_BACKEND_CLIENT_ID", None)
    KEYCLOAK_REDIRECT_URI: str = os.getenv("KEYCLOAK_REDIRECT_URI", None)

    KEYCLOAK_CLIENT_ID: str = None
    KEYCLOAK_CLIENT_SECRET: str = None

    KEYCLOAK_POOL_SIZE: int = 5

    REDIS_HOST: str = os.getenv("REDIS_HOST", None)
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", "8000"))
    CONTEXT_PATH = os.getenv("CONTEXT_PATH", "")

    def __post_init__(self):
        """
        Post-initialization method to set up the configuration.
        """

        if self.ENV not in {"prod", "dev"}:
            logger.error("Environment can only be 'dev' or 'prod'")
            sys.exit(1)

        self.KEYCLOAK_CLIENT_ID = self.KEYCLOAK_BACKEND_CLIENT_ID

        try:
            with open("/usr/shared/client-secret.txt", "r", encoding="utf-8") as file:
                self.KEYCLOAK_CLIENT_SECRET = file.read().strip()
                file.close()
        except FileNotFoundError:
            logger.error(
                "Client secret file not found at /usr/shared/client-secret.txt"
            )
            sys.exit(1)

        if self.ENV == "dev":
            logger.info("Loading FastAPI in development mode...")

            # Fix for E1101: Convert dataclass to dict
            current_settings = self.__dict__

            # Calculate width for pretty printing
            width = max(len(k) for k in current_settings)

            for key, value in current_settings.items():
                # Hide sensitive data
                if "PASSWORD" in key or "SECRET" in key:
                    value = "***"

                logger.info("%-*s -> %s", width, key, value)
        elif self.ENV == "prod":
            logger.info("Loading FastAPI in production mode...")
        else:
            sys.exit(1)


# Global configuration instance
config = Configuration()
