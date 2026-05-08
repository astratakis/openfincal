"""
Docstring for app.src.auth
"""

import logging
from typing import Any, Callable, Dict

from fastapi import Request
from keycloak import KeycloakOpenID, KeycloakPostError
from src.backend.keycloak import KEYCLOAK_OPENID_CLIENT, KEYCLOAK_ADMIN_CLIENT
from src.backend.redis import REDIS
from src.config import config
from src.exceptions import AuthenticationError

logger = logging.getLogger("uvicorn")


def auth() -> Callable[..., Dict[str, Any]]:
    """
    Docstring for auth

    :return: Description
    :rtype: Callable[..., Dict[str, Any]]
    """

    async def dependency(request: Request) -> Dict[str, Any]:

        session_id = request.cookies.get("session_id")

        if session_id is None:
            raise AuthenticationError(detail="Session ID does not exist")

        access_token = REDIS.get(f"{session_id}-access")

        if access_token is None:
            raise AuthenticationError(
                detail="Access token with this session ID does not exist"
            )

        oid = KEYCLOAK_OPENID_CLIENT()
        status = oid.introspect(access_token)

        if status["active"]:
            logger.info("Session is active")
        else:
            logger.info("======= <UPDATING> =======")

            refresh_token = REDIS.get(f"{session_id}-refresh")

            test = KeycloakOpenID(
                server_url=config.KEYCLOAK_URL,
                realm_name=config.KEYCLOAK_REALM,
                client_id=config.KEYCLOAK_FRONTEND_CLIENT_ID,
                client_secret_key=None,  # Not needed for refresh
                verify=False,
            )

            try:
                data = test.refresh_token(refresh_token)
            except KeycloakPostError as e:
                logger.error("Failed to refresh token.")
                REDIS.delete(f"{session_id}-access")
                REDIS.delete(f"{session_id}-refresh")
                REDIS.delete(f"{session_id}-id")
                raise AuthenticationError(detail="Failed to refresh token") from e

            REDIS.set(f"{session_id}-access", data["access_token"])
            REDIS.set(f"{session_id}-refresh", data["refresh_token"])
            REDIS.set(f"{session_id}-id", data["id_token"])

            status = oid.introspect(data["access_token"])
            if status["active"]:
                logger.info("Session is active after refresh")
            else:
                logger.info("Session is not active after refresh")
                REDIS.delete(f"{session_id}-access")
                REDIS.delete(f"{session_id}-refresh")
                REDIS.delete(f"{session_id}-id")
                raise AuthenticationError(detail="Session is not active")

            access_token = data["access_token"]

        claims = oid.decode_token(access_token)
        sid = claims.get("sid")

        user_profile = oid.userinfo(access_token)
        user_id = user_profile.get("sub")

        return {
            "uid": user_id,
            "sid": sid,
            "cookie_session_id": session_id,
        }

    return dependency


def delete_session(auth_ctx: Dict[str, Any], ssid: str):
    """
    Deletes a session given its ID.
    """

    cookie_session_id = auth_ctx.get("cookie_session_id")

    KEYCLOAK_ADMIN_CLIENT().connection.raw_delete(
        f"/admin/realms/{config.KEYCLOAK_REALM}/sessions/{ssid}"
    )
    REDIS.delete(f"{cookie_session_id}-access")
    REDIS.delete(f"{cookie_session_id}-refresh")
    REDIS.delete(f"{cookie_session_id}-id")
