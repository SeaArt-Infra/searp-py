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
Use `client.sessions.custom_task` for read-only caller-supplied PE work,
`client.cards.translate` for model-backed card translation, and
`client.world_books` for project/catalog world books.
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
  `update_translation`, `restore_version`, `list_translations`, `save_translations`, `import_batch`, `list_by_user`
- `versions.preview`
- `cinema.list_rounds`, `create_round`, `create_round_stream`, `get_round`,
  `get_image_task`, `generate_image_task`, `save_image_result`

- `cards.untranslated`, `fork_translations`, `fork`
- `group_cards`: CRUD, listing, versions, roster, characters, preview, import, translations
- `group_sessions`: create, turn, turn stream, get turn, prompt
