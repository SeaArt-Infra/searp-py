# SeaRP Python SDK

Python client for the SeaRP engine HTTP API. It is synchronous and uses only
the standard library.

## Install

```bash
pip install --upgrade git+https://github.com/SeaArt-Infra/searp-py.git
```

Requirements:

- Python 3.10+

## Quick Start

```python
import searp_sdk as rp

client = rp.Client(
    rp.ClientConfig(
        api_key="rp-your-project-token",
        base_url="https://rp.example.com",
    )
)

session = client.sessions.create(
    {
        "user_id": "visitor-1",
        "request": {
            "character": {"name": "Ada", "gender": 2},
            "style": 1,
            "lang": "en",
        },
    },
    rp.WithHeader("x-request-id", "request-1"),
)
print(session["id"])
```

`base_url` defaults to `http://127.0.0.1:8788`; the API base is derived as
`<base_url>/v1` unless it already ends in `/v1`.

`sessions.create` is the general session entry point. Use
`sessions.create_experience` only when the project has already published an
experience version.

## Services

| Service | Purpose |
| --- | --- |
| `client.sessions` | Sessions, history, turns, rewind/fork/edit |
| `client.operations` | Idempotent paid operations, recovery, traces |
| `client.engine` | Health, models, generations, assemble, debug chat |
| `client.cards` | Role-card CRUD, versions, translations |
| `client.versions` | Version preview |
| `client.cinema` | Cinema rounds and image tasks |

## Chat Turn

```python
turn = client.sessions.turn(
    session["id"],
    {
        "action": "reply",
        "text": "Hello.",
        "expected_revision": session["revision"],
    },
    rp.WithHeaders(
        {
            "x-infra-project-id": project_id,
            "x-infra-user-id": user_id,
            "x-request-id": request_id,
        }
    ),
)
```

For SSE streaming:

```python
for event in client.sessions.turn_stream(
    session["id"],
    {"action": "reply", "text": "Hello.", "stream": True},
):
    if event.done:
        break
    if event.event == "token":
        print(event.data, end="")
```

## Errors

The engine returns plain-text HTTP errors:

```python
try:
    client.sessions.get("missing")
except rp.SeaRPError as exc:
    print(exc.kind, exc.code, exc.status)
```

## Development

```bash
python3 -m unittest discover -s tests -v
```
