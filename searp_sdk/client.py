from __future__ import annotations

import posixpath
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from urllib.parse import urlparse

from .cards import CardsService
from .cinema import CinemaService
from .engine import EngineService
from .admin import AdminService
from .errors import ERR_GENERAL, SeaRPError
from .operations import OperationsService
from .sessions import SessionsService
from .transport import TransportClient
from .versions import VersionsService

DEFAULT_BASE_URL = "http://127.0.0.1:8788"
DEFAULT_ADMIN_BASE_URL = "http://127.0.0.1:8790/admin/v1"
DEFAULT_TIMEOUT = 300.0
SDK_VERSION = "0.1.0"


@dataclass(slots=True)
class ClientConfig:
    api_key: str = ""
    base_url: str = ""
    api_base_url: str = ""
    admin_base_url: str = ""
    headers: Mapping[str, str | Sequence[str]] = field(default_factory=dict)
    timeout: float = DEFAULT_TIMEOUT


class Client:
    def __init__(self, config: ClientConfig | None = None) -> None:
        config = config or ClientConfig()
        base_url = _resolve_root_url(config.base_url)
        api_base_url = _resolve_api_base_url(base_url, config.api_base_url)
        admin_base_url = _resolve_admin_base_url(base_url, config.admin_base_url, config.base_url)
        timeout = config.timeout if config.timeout > 0 else DEFAULT_TIMEOUT
        self.api_key = config.api_key
        self.base_url = base_url
        self.api_base_url = api_base_url
        self.admin_base_url = admin_base_url
        self.headers = _normalize_headers(config.headers)

        transport = TransportClient(
            api_key=self.api_key,
            base_url=self.api_base_url,
            default_headers=self.headers,
            user_agent=f"searp-py/{SDK_VERSION}",
            timeout=timeout,
        )
        self.sessions = SessionsService(transport)
        self.operations = OperationsService(transport)
        self.engine = EngineService(transport)
        self.cards = CardsService(transport)
        self.versions = VersionsService(transport)
        self.cinema = CinemaService(transport)
        admin_transport = TransportClient(
            api_key=self.api_key,
            base_url=self.admin_base_url,
            default_headers=self.headers,
            user_agent=f"searp-py/{SDK_VERSION}",
            timeout=timeout,
        )
        self.admin = AdminService(admin_transport)

        self.Sessions = self.sessions
        self.Operations = self.operations
        self.Engine = self.engine
        self.Cards = self.cards
        self.Versions = self.versions
        self.Cinema = self.cinema
        self.Admin = self.admin


def new(config: ClientConfig | None = None) -> Client:
    return Client(config)


def _normalize_headers(headers: Mapping[str, str | Sequence[str]]) -> dict[str, list[str]]:
    normalized: dict[str, list[str]] = {}
    for key, value in headers.items():
        normalized[key] = [value] if isinstance(value, str) else [str(item) for item in value]
    return normalized


def _resolve_root_url(raw: str) -> str:
    return _normalize_url(raw or DEFAULT_BASE_URL)


def _resolve_api_base_url(root: str, raw: str) -> str:
    if raw:
        return _normalize_url(raw)
    parsed = urlparse(root)
    if parsed.path.endswith("/v1"):
        return root
    return _join_url(root, "v1")


def _resolve_admin_base_url(root: str, raw: str, configured_base_url: str) -> str:
    if raw:
        return _normalize_url(raw)
    if not configured_base_url:
        return _normalize_url(DEFAULT_ADMIN_BASE_URL)
    return _join_url(root, "admin/v1")


def _normalize_url(raw: str) -> str:
    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        raise SeaRPError(kind=ERR_GENERAL, message="invalid URL: missing scheme or host")
    normalized_path = posixpath.normpath(parsed.path or "/")
    if normalized_path == "/":
        normalized_path = ""
    return parsed._replace(path=normalized_path).geturl()


def _join_url(base_url: str, suffix: str) -> str:
    parsed = urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        raise SeaRPError(kind=ERR_GENERAL, message="invalid URL: missing scheme or host")
    joined_path = posixpath.join(parsed.path or "/", suffix)
    return _normalize_url(parsed._replace(path=joined_path).geturl())
