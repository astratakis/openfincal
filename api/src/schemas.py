"""
Pydantic schemas for API request/response validation (no forward refs)
- No `from __future__ import annotations`
- Define classes in dependency order (profile -> member -> household)
- No `.model_rebuild()` calls needed
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class AppInfo(BaseModel):
    """
    Pydantic model representing application information.
    """

    service: str
    version: str
    docs: str


class Error(BaseModel):
    """
    Docstring for Error
    """

    detail: str


class SessionDetails(BaseModel):
    """
    Sessions Schema for Ui
    """

    id: str
    ip_address: str = Field(validation_alias="ipAddress")
    start: int
    last_access: int = Field(validation_alias="lastAccess")
    remember_me: bool = Field(validation_alias="rememberMe")


class CurrentSessions(BaseModel):
    """
    Sessions Schema for Ui
    """

    sessions: List[SessionDetails]


class PasswordReset(BaseModel):
    """
    Password Reset Schema for UI
    """

    old_password: str
    new_password: str
    retype_new_password: str
