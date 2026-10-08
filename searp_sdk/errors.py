from __future__ import annotations

from dataclasses import dataclass
import json

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
    message: str
    code: str | None = None
    status: int | None = None
    payload: dict | None = None
    session_id: str = ""

    def __str__(self) -> str:
        return self.message


def new_http_error(status: int, message: str, code: str | None = None) -> SeaRPError:
    payload = None
    try:
        decoded = json.loads(message)
        if isinstance(decoded, dict):
            payload = decoded
            envelope = decoded.get("error")
            if isinstance(envelope, dict):
                code = envelope.get("code") or code
                message = envelope.get("message") or message
    except (ValueError, TypeError):
        pass
    kind = ERR_GENERAL
    if status in (400, 422):
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
    return SeaRPError(kind=kind, code=code, status=status, message=message, payload=payload, session_id=(payload or {}).get("session_id", ""))
