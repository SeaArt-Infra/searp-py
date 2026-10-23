from __future__ import annotations

from urllib.parse import quote, urlencode

from .request_options import RequestOption
from .errors import ERR_INVALID, SeaRPError
from .service import request_json
from .transport import TransportClient


class CardsService:
    def __init__(self, client: TransportClient, control_client: TransportClient | None = None) -> None:
        self._client = client
        self._control_client = control_client

    def import_batch(self, body: dict, *options: RequestOption) -> dict:
        """Legacy deployment route; current release onboarding uses fork."""
        if self._control_client is None:
            raise SeaRPError(kind=ERR_INVALID, message="cards.import_batch requires control_api_base_url (full /admin/v1 base)")
        return request_json(self._control_client, "POST", "/cards/import/batch", body, options)

    def list(self, query: dict | None = None, *options: RequestOption) -> list:
        return request_json(self._client, "GET", f"/cards{_card_query(query)}", None, options)

    def fork(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        if self._control_client is None:
            raise SeaRPError(kind=ERR_INVALID, message="cards.fork requires control_api_base_url (full /admin/v1 base)")
        return request_json(self._control_client, "POST", f"/projects/{_id(project_id)}/cards/fork", body, options)

    def untranslated(self, query: dict, *options: RequestOption) -> dict:
        values = {}
        for key in ("locale", "limit", "offset", "include_partial"):
            value = query.get(key)
            if value is not None:
                values[key] = str(value).lower() if isinstance(value, bool) else value
        return request_json(self._client, "GET", f"/cards/untranslated?{urlencode(values)}", None, options)

    def fork_translations(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/cards/translations/fork", body, options)

    def create(self, body: dict, *options: RequestOption) -> dict:
        """Deprecated endpoint, scheduled to sunset on 2027-01-01."""
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

    def list_versions(self, card_id: str, query: dict | None = None, *options: RequestOption) -> dict:
        if callable(query):
            options = (query, *options)
            query = None
        values = {key: query[key] for key in ("limit", "before_version") if query and query.get(key) is not None}
        suffix = f"?{urlencode(values)}" if values else ""
        return request_json(self._client, "GET", f"/cards/{_id(card_id)}/versions{suffix}", None, options)

    def get_version(self, card_id: str, version: int, query: dict | None = None, *options: RequestOption) -> dict:
        if callable(query):
            options = (query, *options)
            query = None
        return request_json(self._client, "GET", f"/cards/{_id(card_id)}/versions/{version}{_card_query(query)}", None, options)

    def delete_version(self, card_id: str, version: int, *options: RequestOption) -> dict:
        return request_json(self._client, "DELETE", f"/cards/{_id(card_id)}/versions/{version}", None, options)

    def update_translation(self, card_id: str, version: int, lang: str, field: str, body: dict, *options: RequestOption) -> dict:
        path = f"/cards/{_id(card_id)}/versions/{version}/translations/{quote(lang, safe='')}/{quote(field, safe='')}"
        return request_json(self._client, "PATCH", path, body, options)

    def restore_version(self, card_id: str, version: int, body: dict | None = None, *options: RequestOption) -> dict:
        if not isinstance(body, dict) or "expected_latest_version" not in body:
            raise SeaRPError(kind=ERR_INVALID, message="restore requires a body with expected_latest_version")
        return request_json(self._client, "POST", f"/cards/{_id(card_id)}/versions/{version}/restore", body, options)

    def list_translations(self, card_id: str, version: int, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"/cards/{_id(card_id)}/versions/{version}/translations", None, options)

    def save_translations(self, card_id: str, version: int, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"/cards/{_id(card_id)}/versions/{version}/translations", body, options)

    def list_by_user(self, user_id: str, query: dict | None = None, *options: RequestOption) -> list:
        return request_json(self._client, "GET", f"/users/{_id(user_id)}/cards{_card_query(query)}", None, options)


def _id(value: str) -> str:
    return quote(str(value), safe="")


def _card_query(query: dict | None) -> str:
    if not query:
        return ""
    values = {}
    for key in ("limit", "offset"):
        if query.get(key) is not None:
            values[key] = query[key]
    if query.get("lang"):
        values["lang"] = query["lang"]
    ids = query.get("ids") or query.get("card_ids")
    if isinstance(ids, (list, tuple)):
        values["ids" if query.get("ids") else "card_ids"] = ",".join(str(item) for item in ids)
    elif ids:
        values["ids" if query.get("ids") else "card_ids"] = ids
    suffix = urlencode(values)
    return f"?{suffix}" if suffix else ""
