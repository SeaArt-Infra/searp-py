from __future__ import annotations

from urllib.parse import quote, urlencode

from .request_options import RequestOption
from .service import request_json, stream_sse
from .transport import TransportClient


class GroupSessionsService:
    def __init__(self, client: TransportClient) -> None:
        self._client = client

    def create(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/group-sessions", body, options)

    def turn(self, session_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"{_path(session_id)}/turns", body, options)

    def turn_stream(self, session_id: str, body: dict, *options: RequestOption):
        return stream_sse(self._client, "POST", f"{_path(session_id)}/turns", body, options)

    def get_turn(self, session_id: str, turn_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"{_path(session_id)}/turns/{quote(str(turn_id), safe='')}", None, options)

    def prompt(self, session_id: str, query: dict | None = None, *options: RequestOption) -> dict:
        if callable(query):
            options = (query, *options)
            query = None
        values = {"turn_id": query["turn_id"]} if query and query.get("turn_id") is not None else {}
        suffix = f"?{urlencode(values)}" if values else ""
        return request_json(self._client, "GET", f"{_path(session_id)}/prompt{suffix}", None, options)


def _path(session_id: str) -> str:
    return f"/sessions/{quote(str(session_id), safe='')}/group"
