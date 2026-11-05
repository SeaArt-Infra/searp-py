from __future__ import annotations

from urllib.parse import quote, urlencode

from .request_options import RequestOption
from .service import request_json
from .transport import TransportClient


class WorldBooksService:
    """Project and catalog world-book APIs."""

    def __init__(self, client: TransportClient) -> None:
        self._client = client

    def list(self, query: dict | None = None, *options: RequestOption) -> dict:
        return self._list("/world-books", query, options)

    def get(self, world_book_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"/world-books/{quote(str(world_book_id), safe='')}", None, options)

    def create(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/world-books", body, options)

    def delete(self, world_book_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "DELETE", f"/world-books/{quote(str(world_book_id), safe='')}", None, options)

    def catalog_list(self, query: dict | None = None, *options: RequestOption) -> dict:
        return self._list("/catalog/world-books", query, options)

    def catalog_get(self, world_book_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"/catalog/world-books/{quote(str(world_book_id), safe='')}", None, options)

    def _list(self, path: str, query: dict | None, options: tuple[RequestOption, ...]) -> dict:
        values = {}
        if query:
            for key in ("limit", "cursor"):
                if query.get(key) is not None:
                    values[key] = query[key]
        suffix = f"?{urlencode(values)}" if values else ""
        return request_json(self._client, "GET", path + suffix, None, options)


# Singular compatibility alias matching the Go service type.
WorldBookService = WorldBooksService
