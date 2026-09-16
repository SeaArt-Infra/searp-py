from __future__ import annotations

from urllib.parse import quote, urlencode

from .request_options import RequestOption
from .service import request_json
from .transport import TransportClient


class CardsService:
    def __init__(self, client: TransportClient) -> None:
        self._client = client

    def list(self, query: dict | None = None, *options: RequestOption) -> list:
        return request_json(self._client, "GET", f"/cards{_card_query(query)}", None, options)

    def create(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/cards", body, options)

    def get(self, card_id: str, query: dict | None = None, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"/cards/{_id(card_id)}{_card_query(query)}", None, options)

    def update(self, card_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "PATCH", f"/cards/{_id(card_id)}", body, options)

    def delete(self, card_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "DELETE", f"/cards/{_id(card_id)}", None, options)

    def import_cards(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/cards/import", body, options)

    def set_listing(self, card_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "PATCH", f"/cards/{_id(card_id)}/listing", body, options)

    def list_versions(self, card_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"/cards/{_id(card_id)}/versions", None, options)

    def get_version(self, card_id: str, version: int, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"/cards/{_id(card_id)}/versions/{version}", None, options)

    def delete_version(self, card_id: str, version: int, *options: RequestOption) -> dict:
        return request_json(self._client, "DELETE", f"/cards/{_id(card_id)}/versions/{version}", None, options)

    def update_translation(self, card_id: str, version: int, lang: str, field: str, body: dict, *options: RequestOption) -> dict:
        path = f"/cards/{_id(card_id)}/versions/{version}/translations/{quote(lang, safe='')}/{quote(field, safe='')}"
        return request_json(self._client, "PATCH", path, body, options)

    def restore_version(self, card_id: str, version: int, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"/cards/{_id(card_id)}/versions/{version}/restore", None, options)

    def list_by_user(self, user_id: str, query: dict | None = None, *options: RequestOption) -> list:
        return request_json(self._client, "GET", f"/users/{_id(user_id)}/cards{_card_query(query)}", None, options)


def _id(value: str) -> str:
    return quote(str(value), safe="")


def _card_query(query: dict | None) -> str:
    if not query:
        return ""
    values = {}
    if query.get("lang"):
        values["lang"] = query["lang"]
    ids = query.get("ids") or query.get("card_ids")
    if isinstance(ids, (list, tuple)):
        values["ids" if query.get("ids") else "card_ids"] = ",".join(str(item) for item in ids)
    elif ids:
        values["ids" if query.get("ids") else "card_ids"] = ids
    suffix = urlencode(values)
    return f"?{suffix}" if suffix else ""
