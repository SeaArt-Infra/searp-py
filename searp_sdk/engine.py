from __future__ import annotations

from urllib.parse import quote

from .request_options import RequestOption
from .service import request_json, stream_sse
from .transport import TransportClient


class EngineService:
    def __init__(self, client: TransportClient) -> None:
        self._client = client

    def health(self, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", "/health", None, options)

    def capabilities(self, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", "/capabilities", None, options)

    def models(self, *options: RequestOption) -> list:
        return request_json(self._client, "GET", "/models", None, options)

    def llm_status(self, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", "/llm", None, options)

    def llm_check(self, body: dict | None = None, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/llm/check", body or {}, options)

    def generation_models(self, *options: RequestOption) -> list:
        return request_json(self._client, "GET", "/generations/models", None, options)

    def create_generation(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/generations", body, options)

    def get_generation(self, generation_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"/generations/{quote(str(generation_id), safe='')}", None, options)

    def assemble(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/assemble", body, options)

    def debug_chat(self, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", "/debug/chat", body, options)

    def debug_chat_stream(self, body: dict, *options: RequestOption):
        return stream_sse(self._client, "POST", "/debug/chat", body, options)
