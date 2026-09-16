from __future__ import annotations

from dataclasses import dataclass

ERR_AUTH = "auth"
ERR_INVALID = "invalid"
ERR_NOT_FOUND = "not_found"
ERR_CONFLICT = "conflict"
ERR_QUOTA = "quota"
ERR_TIMEOUT = "timeout"
ERR_NETWORK = "network"
ERR_GENERAL = "general"


@dataclass(eq=False)
class SeaRPError(Exception):
    kind: str
    code: str | None
    message: str
    status: int | None = None

    def __str__(self) -> str:
        return self.message


def new_http_error(status: int, message: str, code: str | None = None) -> SeaRPError:
    kind = ERR_GENERAL
    if status == 400:
        kind = ERR_INVALID
    elif status in (401, 403):
        kind = ERR_AUTH
    elif status == 404:
        kind = ERR_NOT_FOUND
    elif status == 409:
        kind = ERR_CONFLICT
    elif status == 429:
        kind = ERR_QUOTA
    elif status in (408, 504):
        kind = ERR_TIMEOUT
    return SeaRPError(kind=kind, code=code, status=status, message=message)
