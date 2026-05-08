"""
Core system operations for the FreeVO API.
"""

import logging
import time
from typing import Any, Dict
import uuid
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from keycloak import (
    KeycloakAuthenticationError,
    KeycloakGetError,
    KeycloakOpenID,
    KeycloakPostError,
)
from src.auth import auth, delete_session
from src.backend.redis import REDIS
from src.config import config
from src.exceptions import BadGatewayError, DataError, NotFoundError, AuthorizationError
from src.backend.keycloak import KEYCLOAK_ADMIN_CLIENT, KEYCLOAK_OPENID_CLIENT

from src.schemas import CurrentSessions, Error, PasswordReset, AppInfo

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
    responses={
        200: {"model": AppInfo},
    },
)
def info():
    return {
        "service": config.TITLE,
        "version": config.VERSION,
        "docs": "/docs",
    }


@router.get("/endpoints")
def endpoints(request: Request):
    return {
        route.name: {
            "path": route.path,
            "method": (
                list(route.methods)[0]
                if hasattr(route, "methods") and route.methods
                else None
            ),
        }
        for route in request.app.routes
        if hasattr(route, "name") and hasattr(route, "path")
    }


@router.get(
    "/login",
    status_code=307,
    summary="Login Operation",
    description="Performs login operation by redirecting to keycloak url",
)
def login():
    """
    Redirect user to Keycloak login page.
    This is the entry point for authentication.
    """

    params = {
        "client_id": config.KEYCLOAK_FRONTEND_CLIENT_ID,
        "redirect_uri": config.KEYCLOAK_REDIRECT_URI,
        "response_type": "code",  # We want an authorization code
        "scope": "openid profile email",  # Request these scopes
    }

    url = (
        f"{config.KEYCLOAK_EXT_URL}/realms/{config.KEYCLOAK_REALM}"
        f"/protocol/openid-connect/auth?{urlencode(params)}"
    )

    logging.info("Redirecting to Keycloak login page: %s", url)

    return RedirectResponse(url=url)


@router.post(
    "/logout",
    status_code=204,
    summary="Logs out current user",
    description="Deletes the current session of the user",
    responses={
        401: {"model": Error},
    },
)
def logout(auth_ctx: Dict[str, Any] = Depends(auth())):

    user_id = auth_ctx.get("uid")
    cookie_session_id = auth_ctx.get("cookie_session_id")

    KEYCLOAK_ADMIN_CLIENT().user_logout(user_id)

    REDIS.delete(f"{cookie_session_id}-access")
    REDIS.delete(f"{cookie_session_id}-refresh")
    REDIS.delete(f"{cookie_session_id}-id")


@router.get(
    "/callback",
    status_code=307,
    summary="Validate KC Code",
    description="Validates a keycloak code and redirects to the home page",
    responses={
        502: {"model": Error},
    },
)
def callback(code: str = Query()):

    logger.info("Received callback with code: %s", code)

    oidc_client = KeycloakOpenID(
        server_url=config.KEYCLOAK_URL,
        realm_name=config.KEYCLOAK_REALM,
        client_id=config.KEYCLOAK_FRONTEND_CLIENT_ID,
        client_secret_key=None,  # Not needed for code exchange
        verify=False,
    )

    try:
        token_response = oidc_client.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=config.KEYCLOAK_REDIRECT_URI,
        )

        logger.info("Token exchange successful")

        # 3. Use the tokens
        access_token = token_response["access_token"]
        refresh_token = token_response.get("refresh_token")
        id_token = token_response.get("id_token")

    except KeycloakGetError as e:
        # Handle connection errors or invalid requests
        logger.error("Failed to connect to Keycloak")
        raise BadGatewayError(detail="Failed to connect to Keycloak") from e
    except KeycloakPostError as e:
        # Handle 400/401 errors from Keycloak (e.g., invalid code)
        logger.error("Keycloak returned an error: %s", e)
        raise BadGatewayError(detail="Keycloak returned an error") from e

    session_id = str(uuid.uuid4())

    REDIS.set(f"{session_id}-access", access_token)
    REDIS.set(f"{session_id}-refresh", refresh_token)
    REDIS.set(f"{session_id}-id", id_token)
    redirect = RedirectResponse(url=config.FRONTEND_EXT_URL)

    logger.info("Session Created with ID: %s", session_id)

    redirect.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=config.FRONTEND_COOKIE_SECURE,
        samesite=config.FRONTEND_COOKIE_SAMESITE,
        path="/",
        # domain="freevo.es"
    )

    logger.info("HTTP only cookie was set.")

    return redirect


@router.get(
    "/verify",
    status_code=204,
    summary="Verifies the current session",
    description="Given the session ID refresh the access and refresh tokens.",
    dependencies=[Depends(auth())],
    responses={
        401: {"model": Error},
    },
)
async def verify():
    return None


@router.get(
    "/sessions",
    summary="Get the sessions of a User",
    description="Returns a list of sessions of the current user",
    responses={
        200: {"model": CurrentSessions},
        401: {"model": Error},
    },
)
def get_sessions(auth_ctx: Dict[str, Any] = Depends(auth())):
    user_id = auth_ctx.get("uid")
    sessions = KEYCLOAK_ADMIN_CLIENT().get_sessions(user_id)
    return CurrentSessions(sessions=sessions)


@router.delete(
    "/sessions",
    status_code=204,
    summary="Delete all sessions of the user",
    description="Deletes all sessions of the currently logged user",
    responses={
        401: {"model": Error},
    },
)
def delete_sessions(auth_ctx: Dict[str, Any] = Depends(auth())):
    user_id = auth_ctx.get("uid")
    KEYCLOAK_ADMIN_CLIENT().user_logout(user_id)
    return None


@router.delete(
    "/sessions/{ssid}",
    status_code=204,
    summary="Delete a session of the user",
    description="Deletes a session of the user given the session id",
    responses={
        401: {"model": Error},
        403: {"model": Error},
        404: {"model": Error},
    },
)
def delete_session(ssid: str, auth_ctx: Dict[str, Any] = Depends(auth())):
    user_id = auth_ctx.get("uid")
    sessions = KEYCLOAK_ADMIN_CLIENT().get_sessions(user_id)

    session = next((s for s in sessions if s.get("id") == ssid), None)

    if session is None:
        raise NotFoundError(detail="Session not found")

    current_session = auth_ctx.get("sid")

    if current_session == ssid:
        delete_session(auth_ctx, ssid)
        return None

    delta_time = int(time.time()) * 1000 - session.get("start")

    logger.info(
        "Deleting session with ID: %s, which started %d ms ago", ssid, delta_time
    )

    if delta_time < 2 * 24 * 60 * 60 * 1000:
        raise AuthorizationError(
            detail="Cannot delete sessions younger than 2 days for security reasons"
        )

    delete_session(auth_ctx, ssid)


@router.post(
    "/reset",
    status_code=204,
    summary="Resets password",
    description="Resets the password of the currently authenticated user",
    responses={
        401: {"model": Error},
        422: {"model": Error},
    },
)
async def reset(payload: PasswordReset, auth_ctx: Dict[str, Any] = Depends(auth())):

    if payload.new_password != payload.retype_new_password:
        raise DataError(detail="Passwords do not match")

    user_id = auth_ctx.get("uid")
    username = KEYCLOAK_ADMIN_CLIENT().get_user(user_id).get("username", None)

    try:
        token = KEYCLOAK_OPENID_CLIENT().token(
            username=username, password=payload.old_password
        )
    except KeycloakAuthenticationError:
        token = None

    if token is None or token == "":
        raise DataError(detail="Old password is incorrect")

    KEYCLOAK_ADMIN_CLIENT().set_user_password(
        user_id=user_id, password=payload.new_password, temporary=False
    )
