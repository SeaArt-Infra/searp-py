from __future__ import annotations

from urllib.parse import quote, urlencode

from .request_options import RequestOption
from .service import request_json
from .transport import TransportClient


class OperationsService:
    def __init__(self, client: TransportClient) -> None:
        self._client = client

    def run(self, session_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"/sessions/{quote(str(session_id), safe='')}/operations", body, options)

    def get(self, operation_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"/operations/{quote(str(operation_id), safe='')}", None, options)

    def list(self, query: dict | None = None, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"/operations{_operation_query(query)}", None, options)

    def recover(self, operation_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"/operations/{quote(str(operation_id), safe='')}/recover", body, options)

    def traces(self, query: dict | None = None, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"/traces{_operation_query(query)}", None, options)


def _operation_query(query: dict | None) -> str:
    if not query:
        return ""
    values = {}
    for key in ("session_id", "version_id", "status", "offset", "limit"):
        if query.get(key) is not None and query.get(key) != "":
            values[key] = query[key]
    suffix = urlencode(values)
    return f"?{suffix}" if suffix else ""
