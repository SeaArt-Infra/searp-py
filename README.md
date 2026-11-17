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
        "card_info": {
            "name": "Ada", "gender": 2,
            "introduction": "Port pilot",
            "greeting": "Welcome to the fog harbor.",
            "background": "Knows the tides and shipping lanes.",
            "lang": "en",
        },
    },
    rp.WithHeader("x-request-id", "request-1"),
)
print(session["id"])
```

`base_url` defaults to `http://127.0.0.1:8788`; the API base is derived as
`<base_url>/v1` unless it already ends in `/v1`.

`sessions.create` accepts `card_id`, inline `card_info`, or `version_id`.
Use `engine.debug_chat` for temporary card/sampling configurations;
`request` and sampling fields are rejected by `sessions.create`.
`sessions.create_experience` opens the currently published experience version.

See [API reference](API_REFERENCE.md) for all routes, pagination, translations,
multimodal input, per-turn parameters, and migration notes.

## Release API update

Aligned with SeaRP release API docs `8c14e1f` on 2026-11-17. The SDK now
documents per-call style prompt overrides, group multimodal messages, debug
language overrides, and the current retry/thinking behavior.

```python
suggestions = client.sessions.inspiration(session["id"], {"lang": "zh"})
print(suggestions["replies"])

group = client.group_sessions.create({
    "group_id": group_id, "user_id": "visitor-1", "mode": "group_chat",
})
turn = client.group_sessions.turn(group["id"], {
    "content": "Hello everyone.", "expected_revision": group["revision"],
}, rp.with_header("Idempotency-Key", "group-turn-001"))
print(turn["revision"], turn["turn"]["segments"])
```

Use `client.group_sessions.turn_stream` for group SSE.
Handle segment events, errors and disconnects; only done confirms completion.
Inspiration changes no history and calls the model again on each retry.

`POST /v1/cards` is deprecated and scheduled to sunset on 2027-01-01.
The role-card creation example below remains for existing integrations.
For catalog cards, configure `control_api_base_url` and call
`client.cards.fork` with a project ID and `catalog_ids`; inspect
both `items` and `errors`. See [API reference](API_REFERENCE.md) for route
coverage, import-document differences, group request fields and recovery.

## Services

| Service | Purpose |
| --- | --- |
| `client.sessions` | Sessions, history, turns, rewind/fork/edit |
| `client.operations` | Idempotent paid operations, recovery, traces |
| `client.engine` | Health, models, generations, assemble, debug chat |
| `client.cards` | Role-card CRUD, versions, translations |
| `client.world_books` | Project and catalog world books |
| `client.versions` | Version preview |
| `client.cinema` | Cinema rounds and image tasks |

## Legacy Role Card Creation

Create a role card with `client.cards.create`, then open a session from that
card:

```python
card = client.cards.create(
    {
        "user_id": "visitor-1",
        "name": "Ada",
        "gender": 2,
        "introduction": "Port pilot",
        "greeting": "Welcome to the fog harbor.",
        "background": "Knows the tides and shipping lanes.",
        "lang": "en",
    }
)

session = client.sessions.create(
    {
        "user_id": "visitor-1",
        "card_id": card["id"],
    }
)
print(session["id"])
```

`card_version` is optional; omit it to pin the latest card version. Use
`client.cards.list`, `client.cards.get`, `client.cards.update`, and
`client.cards.delete` to maintain cards.

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

The engine returns plain-text or JSON HTTP errors:

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

<script
  type="text/plain"
  data-doc-skill
  data-doc-skill-id="searp-py"
  data-doc-skill-label="SeaRP Python SDK"
  data-doc-skill-filename="searp-py-SKILL.md"
  data-doc-skill-version="1"
>
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
        "card_info": {
            "name": "Ada", "gender": 2,
            "introduction": "Port pilot",
            "greeting": "Welcome to the fog harbor.",
            "background": "Knows the tides and shipping lanes.",
            "lang": "en",
        },
    }
)
```

Use `card_id`, `card_info`, or `version_id` with `sessions.create`;
use `engine.debug_chat` with `card_info` for temporary sampling/configuration.
`sessions.create` rejects a nested `request`.
Use `client.sessions.create_experience` for the currently published version.

## Legacy Role Card Creation

```python
card = client.cards.create(
    {
        "user_id": "user-123",
        "name": "Ada",
        "gender": 2,
        "introduction": "Port pilot",
        "greeting": "Welcome to the fog harbor.",
        "background": "Knows the tides and shipping lanes.",
        "lang": "en",
    }
)

session = client.sessions.create(
    {
        "user_id": "user-123",
        "card_id": card["id"],
    }
)
```

Omit `card_version` to pin the latest card version. Use `client.cards.list`,
`client.cards.get`, `client.cards.update`, and `client.cards.delete` to
maintain cards.

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

## Release API additions (2026-11-17)

Use `client.group_cards` for story cards, immutable versions, members,
imports, preview and translations. Use `client.group_sessions` for creating group
sessions, generating JSON/SSE turns, querying turn records and prompts.
Member removals require a JSON body with `user_id` and
`expected_latest_version`. Group generation accepts either plain-text
`content` or OpenAI `message` content parts, plus per-call
`style_prompt_override`, and supports a
stable `Idempotency-Key` header; preserve the key and original input on retry.
JSON responses include the flattened session revision and group `turn.segments`.
The shared SSE parser also exposes `segment_*` and `parser_warning` events.
Read history through the ordinary session get method.

Turns and Cinema rounds also accept `style_prompt_override` for a one-call
style replacement. Debug chat accepts top-level `lang` to override the card
language for that call. JSON generation retries transient 408/429/5xx failures
once on the same model; SSE does not retry, and cross-model fallback is removed.

`client.sessions.inspiration` returns positive/neutral player reply
suggestions. It accepts an empty body or per-call language and sampling,
changes no history/revision, and has no SSE or idempotency. Every retry calls
the model again. `client.cards.untranslated` queries missing
translations; `fork_translations` copies existing catalog translations.
Check per-item errors even when HTTP is 200.

Card creation is deprecated with sunset 2027-01-01; existing create examples
are for compatibility. Use catalog fork with `catalog_ids` and an explicit
Control API base for onboarding published cards. Legacy batch-import is kept
for older deployments. Consult API_REFERENCE.md for import payload differences
between the release documents and registered handlers.
Cinema lists support descending offset order; returned arrays remain sorted
by ascending sequence. Recover abandon always needs
`acknowledge_unknown: true`; use operation revision for recovery and session
revision for generation. Terminal operation evidence defaults to 7 hours.

## Route Reference

- `sessions.create`, `create_experience`, `get`, `history_message`, `turn`,
  `turn_stream`, `proactive`, `proactive_stream`, `inspiration`, `patch`, `rewind`, `fork`, `edit`
- `operations.run`, `get`, `list`, `recover`, `traces`
- `engine.health`, `live`, `metrics`, `capabilities`, `models`, `llm_status`, `llm_check`,
  `generation_models`, `create_generation`, `get_generation`, `assemble`,
  `debug_chat`, `debug_chat_stream`
- `cards.list`, `create`, `get`, `update`, `delete`, `import_cards`,
  `set_listing`, `list_versions`, `get_version`, `delete_version`,
  `update_translation`, `restore_version`, `list_translations`, `save_translations`, `translate`, `untranslated`, `import_batch`, `list_by_user`
- `sessions.custom_task`
- `world_books`: list, create, get, delete, catalog list/get
- `versions.preview`
- `cinema.list_rounds`, `create_round`, `create_round_stream`, `get_round`,
  `get_image_task`, `generate_image_task`, `save_image_result`

- `cards.untranslated`, `fork_translations`, `fork`
- `group_cards`: CRUD, listing, versions, roster, characters, preview, import, translations
- `group_sessions`: create, turn, turn stream, get turn, prompt
</script>
