from __future__ import annotations

from urllib.parse import quote, urlencode

from .request_options import RequestOption
from .service import request_json, stream_sse
from .transport import TransportClient


class SessionsService:
    def __init__(self, client: TransportClient) -> None:
        self._client = client

    def create(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/sessions", body, options)

    def create_experience(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/experience/sessions", body, options)

    def get(self, session_id: str, query: dict | None = None, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", _session_path(session_id) + _session_query(query), None, options)

    def history_message(self, session_id: str, index: int, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"{_session_path(session_id)}/history/{index}", None, options)

    def turn(self, session_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"{_session_path(session_id)}/turns", body, options)

    def turn_stream(self, session_id: str, body: dict, *options: RequestOption):
        return stream_sse(self._client, "POST", f"{_session_path(session_id)}/turns", body, options)

    def patch(self, session_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "PATCH", _session_path(session_id), body, options)

    def rewind(self, session_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"{_session_path(session_id)}/rewind", body, options)

    def fork(self, session_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"{_session_path(session_id)}/fork", body, options)

    def edit(self, session_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"{_session_path(session_id)}/edit", body, options)


def _session_path(session_id: str) -> str:
    return f"/sessions/{quote(str(session_id), safe='')}"


def _session_query(query: dict | None) -> str:
    if not query:
        return ""
    values = {}
    if "limit" in query:
        values["limit"] = query["limit"]
    if "offset" in query:
        values["offset"] = query["offset"]
    suffix = urlencode(values)
    return f"?{suffix}" if suffix else ""
