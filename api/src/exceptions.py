"""
Custom exceptions for the API, with rich structured data and helpers
to render consistent error responses (RFC-7807 compatible).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request
from starlette.responses import JSONResponse


# -------------------------------------------------
# Core: rich APIException (RFC-7807 compatible)
# -------------------------------------------------
class APIException(HTTPException):
    """
    Rich HTTP error with structured fields and helpers
    to render RFC-7807 problem+json consistently.
    """

    # pylint: disable=too-many-arguments

    def __init__(
        self,
        status_code: int,
        detail: str = "",
        *,
        code: Optional[
            str
        ] = None,  # machine-friendly error code (e.g. "auth/unauthorized")
        errors: Any = None,  # field-level errors, validation issues, etc.
        extra: Optional[
            Dict[str, Any]
        ] = None,  # any additional context (never secrets)
        headers: Optional[Dict[str, str]] = None,
        instance: Optional[str] = None,  # unique id for this occurrence
        retry_after: Optional[int] = None,  # seconds; sets Retry-After header if given
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers or {})
        self.code = code
        self.errors = errors
        self.extra = extra or {}
        self.instance = instance or f"urn:uuid:{uuid.uuid4()}"
        self.timestamp = datetime.now(timezone.utc).isoformat()

        if retry_after is not None:
            self.headers["Retry-After"] = str(retry_after)

    # Problem Details (RFC 7807):
    def to_problem(self, request: Optional[Request] = None) -> Dict[str, Any]:
        """
        Docstring for to_problem

        :param self: Description
        :param request: Description
        :type request: Optional[Request]
        :return: Description
        :rtype: Dict[str, Any]
        """

        body: Dict[str, Any] = {
            "type": self.extra.get("type", "about:blank"),
            "title": self.extra.get("title", self.__class__.__name__),
            "status": self.status_code,
            "detail": self.detail,
            "instance": self.instance,
            "timestamp": self.timestamp,
        }
        if self.code:
            body["code"] = self.code
        if self.errors is not None:
            body["errors"] = self.errors
        if request is not None:
            body["path"] = str(request.url.path)
        if self.extra:
            # keep extra last to avoid collisions with reserved keys
            body["extra"] = self.extra
        return body

    def to_response(self, request: Optional[Request] = None) -> JSONResponse:
        """
        Docstring for to_response

        :param self: Description
        :param request: Description
        :type request: Optional[Request]
        :return: Description
        :rtype: JSONResponse
        """

        return JSONResponse(
            self.to_problem(request),
            status_code=self.status_code,
            headers=self.headers,
            media_type="application/problem+json",
        )

    @property
    def retryable(self) -> bool:
        """
        Whether the client might retry (useful for clients/backoffs).

        :return: True if the error is likely transient and retrying might succeed, False otherwise
        :rtype: bool
        """

        return self.status_code in (429, 503, 504) or 500 <= self.status_code < 600

    @classmethod
    def from_unexpected(cls, exc: Exception) -> "APIException":
        """
        Factory to wrap unknown exceptions safely.
        Never leak internal messages by default.
        Attach the message to extra if needed.

        :param exc: Unexpected exception to wrap
        :type exc: Exception
        :return: Wrapped APIException with generic message and original exception info in extra
        :rtype: APIException
        """

        return InternalError(extra={"cause": exc.__class__.__name__})


# -------------------------------------------------
# Typed Exceptions (40x / 50x)
# -------------------------------------------------


class InvalidError(APIException):
    """
    Docstring for InvalidError
    """

    def __init__(self, detail: str = "Bad Request", **kw):
        super().__init__(400, detail, code="request/invalid", **kw)


class DataError(APIException):
    """
    Docstring for DataError
    """

    # 422 is the proper status for semantically invalid content
    def __init__(self, detail: str = "Unprocessable Entity", errors: Any = None, **kw):
        super().__init__(422, detail, code="request/unprocessable", errors=errors, **kw)


class AuthenticationError(APIException):
    """
    Docstring for AuthenticationError
    """

    def __init__(self, detail: str = "Unauthorized", **kw):
        super().__init__(401, detail, code="auth/unauthorized", **kw)


class AuthorizationError(APIException):
    """
    Docstring for AuthorizationError
    """

    def __init__(self, detail: str = "Forbidden", **kw):
        super().__init__(403, detail, code="auth/forbidden", **kw)


class NotFoundError(APIException):
    """
    Docstring for NotFoundError
    """

    def __init__(self, detail: str = "Not Found", **kw):
        super().__init__(404, detail, code="resource/not_found", **kw)


class NotAllowedError(APIException):
    """
    Docstring for NotAllowedError
    """

    def __init__(self, detail: str = "Method Not Allowed", **kw):
        super().__init__(405, detail, code="request/not_allowed", **kw)


class ConflictError(APIException):
    """
    Docstring for ConflictError
    """

    def __init__(self, detail: str = "Conflict", **kw):
        super().__init__(409, detail, code="resource/conflict", **kw)


class RateLimitError(APIException):
    """
    Docstring for RateLimitError
    """

    def __init__(
        self, detail: str = "Too Many Requests", retry_after: Optional[int] = None, **kw
    ):
        super().__init__(
            429, detail, code="quota/rate_limited", retry_after=retry_after, **kw
        )


class InternalError(APIException):
    """
    Docstring for InternalError
    """

    def __init__(self, detail: str = "Internal Server Error", **kw):
        super().__init__(500, detail, code="server/internal", **kw)


class BadGatewayError(APIException):
    """
    Docstring for BadGatewayError
    """

    def __init__(self, detail: str = "Bad Gateway", **kw):
        super().__init__(502, detail, code="upstream/bad_gateway", **kw)


class ServiceUnavailableError(APIException):
    """
    Docstring for ServiceUnavailableError
    """

    def __init__(
        self,
        detail: str = "Service Unavailable",
        retry_after: Optional[int] = None,
        **kw,
    ):
        super().__init__(
            503, detail, code="upstream/unavailable", retry_after=retry_after, **kw
        )


class GatewayTimeoutError(APIException):
    """
    Docstring for GatewayTimeoutError
    """

    def __init__(self, detail: str = "Gateway Timeout", **kw):
        super().__init__(504, detail, code="upstream/timeout", **kw)
