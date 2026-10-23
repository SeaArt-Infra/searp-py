from __future__ import annotations

from urllib.parse import quote, urlencode

from .request_options import RequestOption
from .service import request_json
from .transport import TransportClient


class GroupCardsService:
    def __init__(self, client: TransportClient) -> None:
        self._client = client

    def list(self, query: dict | None = None, *options: RequestOption) -> list:
        if callable(query):
            options = (query, *options)
            query = None
        return request_json(self._client, "GET", f"/group-cards{_query(query, ('q', 'listed', 'include_deleted', 'limit', 'offset'))}", None, options)

    def create(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/group-cards", body, options)

    def get(self, card_id: str, query: dict | None = None, *options: RequestOption) -> dict:
        if callable(query):
            options = (query, *options)
            query = None
        return request_json(self._client, "GET", f"{_path(card_id)}{_query(query, ('lang',))}", None, options)

    def update(self, card_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "PATCH", _path(card_id), body, options)

    def delete(self, card_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "DELETE", _path(card_id), None, options)

    def set_listing(self, card_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "PATCH", f"{_path(card_id)}/listing", body, options)

    def list_versions(self, card_id: str, *options: RequestOption) -> list:
        return request_json(self._client, "GET", f"{_path(card_id)}/versions", None, options)

    def get_version(self, card_id: str, version: int, query: dict | None = None, *options: RequestOption) -> dict:
        if callable(query):
            options = (query, *options)
            query = None
        return request_json(self._client, "GET", f"{_path(card_id)}/versions/{version}{_query(query, ('lang',))}", None, options)

    def list_members(self, card_id: str, *options: RequestOption) -> list:
        return request_json(self._client, "GET", f"{_path(card_id)}/members", None, options)

    def add_member(self, card_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"{_path(card_id)}/members", body, options)

    def update_member(self, card_id: str, participant_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "PATCH", f"{_path(card_id)}/members/{quote(str(participant_id), safe='')}", body, options)

    def remove_member(self, card_id: str, participant_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "DELETE", f"{_path(card_id)}/members/{quote(str(participant_id), safe='')}", body, options)

    def extract_characters(self, card_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"{_path(card_id)}/characters", body, options)

    def preview(self, card_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"{_path(card_id)}/preview", body, options)

    def import_cards(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/group-cards/import", body, options)

    def list_translations(self, card_id: str, version: int, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"{_path(card_id)}/versions/{version}/translations", None, options)

    def save_translations(self, card_id: str, version: int, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"{_path(card_id)}/versions/{version}/translations", body, options)


def _path(card_id: str) -> str:
    return f"/group-cards/{quote(str(card_id), safe='')}"


def _query(query: dict | None, keys: tuple) -> str:
    values = {}
    for key in keys:
        value = query.get(key) if query else None
        if value is not None:
            values[key] = str(value).lower() if isinstance(value, bool) else value
    return f"?{urlencode(values)}" if values else ""
