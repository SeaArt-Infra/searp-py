from __future__ import annotations

from urllib.parse import quote

from .request_options import RequestOption
from .service import request_json
from .transport import TransportClient


class VersionsService:
    def __init__(self, client: TransportClient) -> None:
        self._client = client

    def preview(self, version_id: str, body: dict, *options: RequestOption) -> dict:
        return request_json(self._client, "POST", f"/versions/{quote(str(version_id), safe='')}/preview", body, options)
