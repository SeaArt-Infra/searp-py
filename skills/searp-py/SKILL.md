---
name: searp-py
description: Build and troubleshoot SeaRP engine integrations with the searp-sdk Python client. Use when creating role-play sessions, running chat turns or streaming replies, using idempotent operations, importing cards, previewing versions, assembling prompts, generating images, or debugging chats from Python.
---

# SeaRP Python SDK

Use `searp-sdk` to call the SeaRP engine `/v1` API from Python 3.10+. Import it
as `searp_sdk as rp`. The SDK is synchronous and uses only the standard library.

## Install

```bash
pip install --upgrade git+https://github.com/SeaArt-Infra/searp-py.git
```

## Workflow

1. Initialize one `rp.Client` with the project bearer token.
2. Use `client.sessions` for sessions/turns, `client.operations` for idempotent
   paid generation, `client.engine` for models/generations/assemble/debug chat,
   and the remaining services for cards, versions, and cinema.
3. Prefer the operations API with a stable idempotency key for paid chat.
4. HTTP 200 does not guarantee a generated reply; inspect operation `status`.
5. Pass request-specific SeaInfra attribution headers with `rp.WithHeaders`.

## Initialize Client

```python
import searp_sdk as rp

client = rp.Client(
    rp.ClientConfig(
        api_key="rp-your-project-token",
        base_url="https://rp.example.com",
    )
)
```

## Create A Session

```python
session = client.sessions.create(
    {
        "user_id": "user-123",
        "request": {
            "character": {"name": "Ada", "gender": 2},
            "style": 1,
            "lang": "en",
        },
    }
)
```

Use `client.sessions.create_experience` only when the project has already
published an experience version.

## Run A Reply

```python
op = client.operations.run(
    session["id"],
    {
        "idempotency_key": "reply-001",
        "action": "reply",
        "text": "Hello.",
        "expected_revision": session["revision"],
    },
)
```

For streaming, use `client.sessions.turn_stream` and stop on `done`.

## Errors

Catch `rp.SeaRPError` and branch on `exc.kind`. `rp.ERR_CONFLICT` usually means
a stale `expected_revision` or an idempotency key reused with different input.

## Route Reference

- `sessions.create`, `create_experience`, `get`, `history_message`, `turn`,
  `turn_stream`, `patch`, `rewind`, `fork`, `edit`
- `operations.run`, `get`, `list`, `recover`, `traces`
- `engine.health`, `capabilities`, `models`, `llm_status`, `llm_check`,
  `generation_models`, `create_generation`, `get_generation`, `assemble`,
  `debug_chat`, `debug_chat_stream`
- `cards.list`, `create`, `get`, `update`, `delete`, `import_cards`,
  `set_listing`, `list_versions`, `get_version`, `delete_version`,
  `update_translation`, `restore_version`, `list_by_user`
- `versions.preview`
- `cinema.list_rounds`, `create_round`, `create_round_stream`, `get_round`,
  `get_image_task`, `generate_image_task`, `save_image_result`
