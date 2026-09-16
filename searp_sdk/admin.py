from __future__ import annotations

import json
from urllib.parse import quote

from .errors import ERR_GENERAL, SeaRPError, new_http_error
from .request_options import RequestOption, build_request_options
from .transport import TransportClient


class AdminService:
    def __init__(self, client: TransportClient) -> None:
        self._client = client

    def request(self, method: str, path: str, body: dict | None, *options: RequestOption) -> dict:
        return _request_json(self._client, method, path, body, options)

    def health(self, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", "/health", None, options)

    def whoami(self, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", "/whoami", None, options)

    def agent_contract(self, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", "/agent/contract", None, options)

    def list_projects(self, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", "/projects", None, options)

    def create_project(self, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", "/projects", body, options)

    def get_project(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", _project_path(project_id), None, options)

    def delete_project(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "DELETE", _project_path(project_id), None, options)

    def rotate_project_token(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", f"{_project_path(project_id)}/token", None, options)

    def get_project_live(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"{_project_path(project_id)}/live", None, options)

    def update_project_live(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PUT", f"{_project_path(project_id)}/live", body, options)


def _project_path(project_id: str) -> str:
    return f"/projects/{quote(str(project_id), safe='')}"


def _request_json(client: TransportClient, method: str, path: str, body: object | None, options: tuple[RequestOption, ...]) -> dict:
    request_options = build_request_options(options)
    status, payload = client.request(method, path, body, request_options.headers)
    if status >= 400:
        raise _http_error(status, payload)
    if not payload:
        return {}
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SeaRPError(kind=ERR_GENERAL, message=f"failed to decode response: {exc}") from exc
    if not isinstance(value, dict):
        raise SeaRPError(kind=ERR_GENERAL, message="admin response must be a JSON object")
    return value


def _http_error(status: int, payload: bytes) -> SeaRPError:
    try:
        envelope = json.loads(payload or b"{}")
    except json.JSONDecodeError:
        return new_http_error(status, payload.decode("utf-8", "replace").strip() or f"HTTP {status}")
    error = envelope.get("error") if isinstance(envelope, dict) else None
    if isinstance(error, dict) and (error.get("code") or error.get("message")):
        return new_http_error(
            status,
            str(error.get("message") or f"HTTP {status}"),
            str(error.get("code") or ""),
        )
    return new_http_error(status, payload.decode("utf-8", "replace").strip() or f"HTTP {status}")
