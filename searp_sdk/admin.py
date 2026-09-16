from __future__ import annotations

import json
from urllib.parse import quote, urlencode

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



    def raw(self, method: str, path: str, body: dict | None, *options: RequestOption) -> bytes:
        request_options = build_request_options(options)
        status, payload = self._client.request(method, path, body, request_options.headers)
        if status >= 400:
            raise _http_error(status, payload)
        return payload

    def project_request(self, project_id: str, method: str, subpath: str, body: dict | None, *options: RequestOption) -> dict:
        return _request_json(self._client, method, _project_subpath(project_id, subpath), body, options)

    def get_global_pack(self, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", "/pack", None, options)

    def update_global_pack(self, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PUT", "/pack", body, options)

    def get_project_pack(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", _project_subpath(project_id, "pack"), None, options)

    def patch_project_pack(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PATCH", _project_subpath(project_id, "pack"), body, options)

    def delete_project_pack(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "DELETE", _project_subpath(project_id, "pack"), None, options)

    def fork_project_pack(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, "pack/fork"), None, options)

    def list_catalog(self, query: dict | None = None, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"/catalog{_query_string(query)}", None, options)

    def import_catalog(self, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", "/catalog/import", body, options)

    def get_catalog_card(self, card_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"/catalog/{quote(str(card_id), safe='')}", None, options)

    def update_catalog_card(self, card_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PATCH", f"/catalog/{quote(str(card_id), safe='')}", body, options)

    def delete_catalog_card(self, card_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "DELETE", f"/catalog/{quote(str(card_id), safe='')}", None, options)

    def get_catalog_card_cover(self, card_id: str, *options: RequestOption) -> bytes:
        return self.raw("GET", f"/catalog/{quote(str(card_id), safe='')}/cover", None, *options)

    def list_project_cards(self, project_id: str, query: dict | None = None, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"{_project_subpath(project_id, 'cards')}{_query_string(query)}", None, options)

    def get_project_card(self, project_id: str, card_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", _project_card_path(project_id, card_id), None, options)

    def update_project_card(self, project_id: str, card_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PATCH", _project_card_path(project_id, card_id), body, options)

    def delete_project_card(self, project_id: str, card_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "DELETE", _project_card_path(project_id, card_id), None, options)

    def set_project_card_listing(self, project_id: str, card_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PATCH", f"{_project_card_path(project_id, card_id)}/listing", body, options)

    def import_project_card(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, "cards/import"), body, options)

    def import_project_cards_batch(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, "cards/import/batch"), body, options)

    def fork_project_card(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, "cards/fork"), body, options)

    def list_project_card_versions(self, project_id: str, card_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"{_project_card_path(project_id, card_id)}/versions", None, options)

    def get_project_card_version(self, project_id: str, card_id: str, version: int, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"{_project_card_path(project_id, card_id)}/versions/{version}", None, options)

    def delete_project_card_version(self, project_id: str, card_id: str, version: int, *options: RequestOption) -> dict:
        return _request_json(self._client, "DELETE", f"{_project_card_path(project_id, card_id)}/versions/{version}", None, options)

    def restore_project_card_version(self, project_id: str, card_id: str, version: int, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", f"{_project_card_path(project_id, card_id)}/versions/{version}/restore", None, options)

    def list_project_experiments(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", _project_subpath(project_id, "experiments"), None, options)

    def create_project_experiment(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, "experiments"), body, options)

    def get_project_experiment(self, project_id: str, experiment_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", _project_subpath(project_id, f"experiments/{quote(str(experiment_id), safe='')}"), None, options)

    def update_project_experiment(self, project_id: str, experiment_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PATCH", _project_subpath(project_id, f"experiments/{quote(str(experiment_id), safe='')}"), body, options)

    def start_project_experiment(self, project_id: str, experiment_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, f"experiments/{quote(str(experiment_id), safe='')}/start"), None, options)

    def pause_project_experiment(self, project_id: str, experiment_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, f"experiments/{quote(str(experiment_id), safe='')}/pause"), None, options)

    def stop_project_experiment(self, project_id: str, experiment_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, f"experiments/{quote(str(experiment_id), safe='')}/stop"), None, options)

    def get_project_llm(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", _project_subpath(project_id, "llm"), None, options)

    def update_project_llm(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PUT", _project_subpath(project_id, "llm"), body, options)

    def delete_project_llm(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "DELETE", _project_subpath(project_id, "llm"), body, options)

    def list_project_versions(self, project_id: str, query: dict | None = None, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"{_project_subpath(project_id, 'versions')}{_query_string(query)}", None, options)

    def create_project_version(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, "versions"), body, options)

    def get_project_version(self, project_id: str, version_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", _project_subpath(project_id, f"versions/{quote(str(version_id), safe='')}"), None, options)

    def diff_project_version(self, project_id: str, version_id: str, against: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"{_project_subpath(project_id, f'versions/{quote(str(version_id), safe='')}/diff')}?{urlencode({'against': against})}", None, options)

    def publish_project_version(self, project_id: str, version_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, f"versions/{quote(str(version_id), safe='')}/publish"), body, options)

    def get_project_release(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", _project_subpath(project_id, "release"), None, options)

    def list_project_releases(self, project_id: str, query: dict | None = None, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"{_project_subpath(project_id, 'releases')}{_query_string(query)}", None, options)

    def rollback_project_release(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, "release/rollback"), body, options)

    def list_project_system_prompts(self, project_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", _project_subpath(project_id, "system-prompts"), None, options)

    def create_project_system_prompt(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", _project_subpath(project_id, "system-prompts"), body, options)

    def set_project_system_prompt_default(self, project_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PUT", _project_subpath(project_id, "system-prompts"), body, options)

    def get_project_system_prompt(self, project_id: str, prompt_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", _project_subpath(project_id, f"system-prompts/{quote(str(prompt_id), safe='')}"), None, options)

    def update_project_system_prompt(self, project_id: str, prompt_id: str, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PUT", _project_subpath(project_id, f"system-prompts/{quote(str(prompt_id), safe='')}"), body, options)

    def list_global_system_prompts(self, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", "/global-system-prompts", None, options)

    def create_global_system_prompt(self, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", "/global-system-prompts", body, options)

    def set_global_system_prompt_default(self, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "PUT", "/global-system-prompts", body, options)

    def get_global_system_prompt(self, prompt_id: str, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"/global-system-prompts/{quote(str(prompt_id), safe='')}", None, options)

    def list_project_user_sessions(self, project_id: str, query: dict | None = None, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"{_project_subpath(project_id, 'user-sessions')}{_query_string(query)}", None, options)

    def get_project_user_session(self, project_id: str, session_id: str, query: dict | None = None, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", f"{_project_subpath(project_id, f'user-sessions/{quote(str(session_id), safe='')}')}{_query_string(query)}", None, options)

    def get_project_identity_migration(self, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", "/project-identity-migration", None, options)

    def start_project_identity_migration(self, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", "/project-identity-migration", body, options)

    def prepare_project_identity_migration(self, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", "/project-identity-migration/prepare", None, options)

    def purge_project_identity_migration(self, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", "/project-identity-migration/purge", body, options)

    def adopt_project_identity_migration(self, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", "/project-identity-migration/adopt", body, options)

    def revert_project_identity_migration(self, body: dict, *options: RequestOption) -> dict:
        return _request_json(self._client, "POST", "/project-identity-migration/revert", body, options)

    def preview_project_identity_migration(self, *options: RequestOption) -> dict:
        return _request_json(self._client, "GET", "/project-identity-migration/preview", None, options)

def _project_path(project_id: str) -> str:
    return f"/projects/{quote(str(project_id), safe='')}"



def _project_subpath(project_id: str, subpath: str = "") -> str:
    base = f"/projects/{quote(str(project_id), safe='')}"
    return f"{base}/{subpath}" if subpath else base


def _project_card_path(project_id: str, card_id: str) -> str:
    return _project_subpath(project_id, f"cards/{quote(str(card_id), safe='')}")


def _query_string(query: dict | None) -> str:
    if not query:
        return ""
    values = {key: value for key, value in query.items() if value is not None and value != ""}
    suffix = urlencode(values)
    return f"?{suffix}" if suffix else ""

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
