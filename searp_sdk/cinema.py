from __future__ import annotations

from urllib.parse import quote

from .request_options import RequestOption
from .service import request_json, stream_sse
from .transport import TransportClient


class CinemaService:
    def __init__(self, client: TransportClient) -> None:
        self._client = client

    def list_rounds(self, session_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"{_path(session_id)}/rounds", None, options)

    def create_round(self, session_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"{_path(session_id)}/rounds", body, options)

    def create_round_stream(self, session_id: str, body: dict, *options: RequestOption):
        return stream_sse(self._client, "POST", f"{_path(session_id)}/rounds", body, options)

    def get_round(self, session_id: str, round_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"{_path(session_id)}/rounds/{_id(round_id)}", None, options)

    def get_image_task(self, session_id: str, task_id: str, *options: RequestOption) -> dict:
        return request_json(self._client, "GET", f"{_path(session_id)}/image-tasks/{_id(task_id)}", None, options)

    def generate_image_task(self, task_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"/cinema/image-tasks/{_id(task_id)}/generate", body, options)

    def save_image_result(self, task_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"/cinema/image-tasks/{_id(task_id)}/result", body, options)


def _path(session_id: str) -> str:
    return f"/sessions/{_id(session_id)}/cinema"


def _id(value: str) -> str:
    return quote(str(value), safe="")
