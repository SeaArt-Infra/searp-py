from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from urllib import error

from .errors import ERR_GENERAL, ERR_NETWORK, SeaRPError, new_http_error
from .request_options import RequestOption, build_request_options
from .transport import TransportClient


def request_json(client: TransportClient, method: str, path: str, body: object | None, options: tuple[RequestOption, ...]) -> object:
    request_options = build_request_options(options)
    status, payload = client.request(method, path, body, request_options.headers)
    if status >= 400:
        raise _http_error(status, payload)
    if not payload:
        return {}
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SeaRPError(kind=ERR_GENERAL, message=f"failed to decode response: {exc}") from exc


@dataclass(slots=True)
class StreamEvent:
    event: str
    data: str
    done: bool
    err: Exception | None = None


def stream_sse(client: TransportClient, method: str, path: str, body: object | None, options: tuple[RequestOption, ...]) -> Iterator[StreamEvent]:
    request_options = build_request_options(options)
    response = client.request_stream(method, path, body, request_options.headers)
    if isinstance(response, error.HTTPError):
        payload = response.read().decode("utf-8", "replace")
        raise _http_error(response.code, payload.encode("utf-8"))

    event_name = ""
    data_lines: list[str] = []

    def flush() -> StreamEvent | None:
        nonlocal event_name, data_lines
        if not data_lines and not event_name:
            return None
        event = StreamEvent(
            event=event_name,
            data="\n".join(data_lines),
            done=event_name == "done",
        )
        event_name = ""
        data_lines = []
        return event

    try:
        for raw_line in response:
            line = raw_line.decode("utf-8", "replace").rstrip("\r\n")
            if line == "":
                event = flush()
                if event is not None:
                    yield event
                continue
            if line.startswith(":"):
                continue
            if line.startswith("event:"):
                event_name = line[len("event:") :].strip()
            elif line.startswith("data:"):
                data_lines.append(line[len("data:") :].lstrip())
        event = flush()
        if event is not None:
            yield event
    except Exception as exc:
        raise SeaRPError(kind=ERR_NETWORK, message=f"stream read failed: {exc}") from exc


def _http_error(status: int, payload: bytes) -> SeaRPError:
    message = payload.decode("utf-8", "replace").strip()
    if not message:
        message = f"HTTP {status}"
    return new_http_error(status, message)
