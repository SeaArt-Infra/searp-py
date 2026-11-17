# SeaRP API reference

Synced on 2026-11-17 against the SeaRP service at `8c14e1f`:
`docs/searp-api.md`, `docs/card-import-api.md` and the card creation migration
guide. Paths below are relative to engine `/v1` unless marked Control API.
Documentation/route differences are recorded below.

## Routes

| Method | Path | Client method |
| --- | --- | --- |
| GET | `/health` | `engine.health` |
| GET | `/live` | `engine.live` |
| GET | `/metrics` | `engine.metrics` |
| GET | `/capabilities` | `engine.capabilities` |
| GET | `/models` | `engine.models` |
| GET | `/llm` | `engine.llm_status` |
| POST | `/llm/check` | `engine.llm_check` |
| GET | `/generations/models` | `engine.generation_models` |
| POST | `/generations` | `engine.create_generation` |
| GET | `/generations/{id}` | `engine.get_generation` |
| POST | `/assemble` | `engine.assemble` |
| POST | `/debug/chat` | `engine.debug_chat / debug_chat_stream` |
| POST | `/sessions` | `sessions.create` |
| POST | `/experience/sessions` | `sessions.create_experience` |
| GET | `/sessions/{id}` | `sessions.get` |
| PATCH | `/sessions/{id}` | `sessions.patch` |
| GET | `/sessions/{id}/history/{index}` | `sessions.history_message` |
| POST | `/sessions/{id}/turns` | `sessions.turn / turn_stream` |
| POST | `/sessions/{id}/proactive` | `sessions.proactive / proactive_stream` |
| POST | `/sessions/{id}/rewind` | `sessions.rewind` |
| POST | `/sessions/{id}/fork` | `sessions.fork` |
| POST | `/sessions/{id}/edit` | `sessions.edit` |
| POST | `/sessions/{id}/operations` | `operations.run` |
| GET | `/operations` | `operations.list` |
| GET | `/operations/{id}` | `operations.get` |
| POST | `/operations/{id}/recover` | `operations.recover` |
| GET | `/traces` | `operations.traces` |
| POST | `/versions/{id}/preview` | `versions.preview` |
| GET | `/cards` | `cards.list` |
| POST (deprecated; sunset 2027-01-01) | `/cards` | `cards.create` |
| GET | `/cards/{id}` | `cards.get` |
| PATCH | `/cards/{id}` | `cards.update` |
| DELETE | `/cards/{id}` | `cards.delete` |
| POST | `/cards/import` | `cards.import_cards` |
| PATCH | `/cards/{id}/listing` | `cards.set_listing` |
| GET | `/users/{user_id}/cards` | `cards.list_by_user` |
| GET | `/cards/{id}/versions` | `cards.list_versions` |
| GET | `/cards/{id}/versions/{version}` | `cards.get_version` |
| DELETE | `/cards/{id}/versions/{version}` | `cards.delete_version` |
| POST | `/cards/{id}/versions/{version}/restore` | `cards.restore_version` |
| PATCH | `/cards/{id}/versions/{version}/translations/{lang}/{field}` | `cards.update_translation` |
| GET | `/cards/{id}/versions/{version}/translations` | `cards.list_translations` |
| POST | `/cards/{id}/versions/{version}/translations` | `cards.save_translations` |
| GET | `/sessions/{id}/cinema/rounds` | `cinema.list_rounds` |
| POST | `/sessions/{id}/cinema/rounds` | `cinema.create_round / create_round_stream` |
| GET | `/sessions/{id}/cinema/rounds/{round_id}` | `cinema.get_round` |
| GET | `/sessions/{id}/cinema/image-tasks/{task_id}` | `cinema.get_image_task` |
| POST | `/cinema/image-tasks/{task_id}/generate` | `cinema.generate_image_task` |
| POST | `/cinema/image-tasks/{task_id}/result` | `cinema.save_image_result` |
| POST | `/sessions/{id}/inspiration` | `sessions.inspiration` |
| POST | `/sessions/{id}/custom-task` | `sessions.custom_task` |
| GET | `/cards/untranslated` | `cards.untranslated` |
| POST | `/cards/{id}/translate` | `cards.translate` |
| POST | `/cards/translations/fork` | `cards.fork_translations` |
| POST | `/admin/v1/projects/{project_id}/cards/fork` | `cards.fork (Control API)` |
| GET | `/group-cards` | `group_cards.list` |
| POST | `/group-cards` | `group_cards.create` |
| GET | `/group-cards/{id}` | `group_cards.get` |
| PATCH | `/group-cards/{id}` | `group_cards.update` |
| DELETE | `/group-cards/{id}` | `group_cards.delete` |
| PATCH | `/group-cards/{id}/listing` | `group_cards.set_listing` |
| GET | `/group-cards/{id}/versions` | `group_cards.list_versions` |
| GET | `/group-cards/{id}/versions/{version}` | `group_cards.get_version` |
| GET | `/group-cards/{id}/members` | `group_cards.list_members` |
| POST | `/group-cards/{id}/members` | `group_cards.add_member` |
| PATCH | `/group-cards/{id}/members/{participant_id}` | `group_cards.update_member` |
| DELETE | `/group-cards/{id}/members/{participant_id}` | `group_cards.remove_member` |
| POST | `/group-cards/{id}/characters` | `group_cards.extract_characters` |
| POST | `/group-cards/{id}/preview` | `group_cards.preview` |
| POST | `/group-cards/import` | `group_cards.import_cards` |
| GET | `/group-cards/{id}/versions/{version}/translations` | `group_cards.list_translations` |
| POST | `/group-cards/{id}/versions/{version}/translations` | `group_cards.save_translations` |
| POST | `/group-sessions` | `group_sessions.create` |
| POST | `/sessions/{id}/group/turns` | `group_sessions.turn / turn_stream` |
| GET | `/sessions/{id}/group/turns/{turn_id}` | `group_sessions.get_turn` |
| GET | `/sessions/{id}/group/prompt` | `group_sessions.prompt` |
| GET/POST | `/world-books` | `world_books.list / create` |
| GET/DELETE | `/world-books/{id}` | `world_books.get / delete` |
| GET | `/catalog/world-books` | `world_books.catalog_list` |
| GET | `/catalog/world-books/{id}` | `world_books.catalog_get` |

## Requests and current contract

Request bodies use the server's snake_case JSON keys and are passed through
unchanged. Authentication and request-specific headers come from the client and
request options. Keep project credentials on the caller's server.

- Session creation requires `user_id` and `card_id`, inline `card_info`, or
  `version_id`. Inline cards require nonempty `name`, `introduction`,
  `greeting`, and `background`; `gender` accepts 0/1/2 or the documented
  male/female/other aliases. A nested `request` and sampling fields are rejected.
  Optional `card_version` pins a stored card version. Optional
  `system_template_id` selects a template ID; `user` is the player persona.
- Experience creation accepts `user_id`, optional `user` and
  `system_template_id`, and uses the currently published version.
- Debug chat takes inline `card_info` plus `text` or `message` on the first
  call. It defaults to `persist: true`; continue with the returned
  `session_id` and `expected_revision`. Use `persist: false` with
  `card_info` and `history` for a stateless call. Debug chat accepts sampling,
  memory and per-call prompt parameters; top-level `lang` overrides
  `card_info.lang` for that call; it does not accept a nested `request`.
- Turns take `action` (reply/additional/regenerate), `text` or `message`,
  optional `expected_revision`, sampling, memory, `user`, `lang`, and
  per-call `style_prompt_override`,
  `system_prompt_override`, `lastest_system_prompt` (keep this spelling),
  `favorability_score` (-1..100), and `metadata.history`.
- Operations take `idempotency_key`, `action`, `text` or `message`,
  `expected_revision` and `metadata` at the top level. Put model,
  temperature, max_tokens, user and request overrides under `live`; put
  max_context and pinned_memory under `memory`. Sampling options
  `top_p`, `thinking_mode`, `thinking_budget_tokens` and prompt parameters
  `lastest_system_prompt`, `favorability_score`, `lang` can also be top-level.
  `system_prompt_override` and `style_prompt_override` belong under `live`.
  Top-level non-null values
  override matching live values. Operations always return JSON.
- `metadata.history` only seeds an empty session. The response's
  `history_import` records seeded/skipped status; leading assistant messages
  are dropped. On operations this transcript participates in the input digest:
  keep it unchanged when retrying the same key.
- Sampling fields are `model`, `temperature` (0..2), `max_tokens`
  (1..1000000), `top_p` (0 < p <= 1), `thinking_mode` and
  `thinking_budget_tokens`. Thinking support depends on the selected model;
  Claude budgets require enabled thinking and 1024 <= budget < max_tokens.
  Gemini 3 accepts `thinking_mode=false` and folds it to the model's minimum
  thinking strength; SeaInfra uses `reasoning_effort=minimal` for that case,
  while OpenRouter keeps `reasoning.effort=low`.
- JSON generation retries transient 408/429/5xx failures once on the same
  model after 750ms; SSE never retries and the old cross-model fallback is
  removed. `failed_attempts` records the earlier attempt when present.
- `lang`, per-turn `user` and prompt instructions apply to that call only.
  Sampling and memory updates on non-version sessions are saved on success.
  Version sessions reject fixed configuration overrides; card sessions reject
  replacing their `request`. PATCH accepts `request` only for debug sessions.
- Assemble requires `request`; optional `history`, `user_message`,
  `max_context`, `pinned_memory`, `cinema` and prompt parameters are passed
  through. Version preview requires `text` and optional prompt parameters.
- Rewind/edit/fork accept `expected_revision`. Rewind and edit require
  an absolute history `index`; fork can omit it to copy all retained history.
  Edit takes text `content` and preserves attached images.
- Recover requires the **operation** `expected_revision` and `action`
  (commit/abandon); every abandonment requires
  `acknowledge_unknown: true`. Inspect operation status before recovery.

## Pagination and translations

| Resource | Query | Response / continuation |
| --- | --- | --- |
| Session history | limit, offset | Latest page by default, limit default/max 10; continue with history_offset + history.length, checking revision across pages |
| Project/user cards | lang, limit, offset; project list also ids/card_ids | Array; limit default 50, max 200; explicit offset=0 is preserved |
| Card versions | limit, before_version | {items, next_before_version}; limit default 20, max 100 |
| Card version detail | lang | Localized snapshot inside version metadata |
| Cinema rounds | limit, offset, order (asc/desc) | Array; limit default 10, max 100 |
| Operations | session_id, version_id, status, limit, offset | {items, next_offset}; continue even if filtering leaves an empty page, until next_offset is null |

Retained session history can start after index 0. A cold-history handoff can
return 409; retry the read rather than combining mismatched revisions.

Translation GET returns `{language_code: {field: text}}`. Translation POST
saves owner-provided fields with
`{user_id, expected_latest_version, lang, translations: {name: "...", ...}}`;
it does not run a translation model. The single-field PATCH requires
`{value, expected_latest_version}`. Supported fields are name, background,
dialog_style, reply_settings, introduction, greeting and scenario.

Restore requires `{expected_latest_version, change_note?}`. It copies the
selected snapshot into a new latest version; it does not reset the version
counter. Card updates/restores can use an `Idempotency-Key` request header.
Translation writes do not create content versions.

## Images, streaming and Cinema

For image chat, replace `text` with `message`:
`[{type: "text", text: "What is this?"}, {type: "image_url", image_url: {url: "https://cdn.example/a.png", detail: "auto"}}]`.
Do not send both nonempty text and message. Additional/regenerate omit both.
The server accepts up to 8 images, 1 MiB per inline image URL and 2 MiB inline
total. History `content` is a string or a content-part array, including in the
single-history-message response.

Streaming methods set `Accept: text/event-stream` automatically. Preserve
token whitespace and handle SSE error events and disconnects; receiving HTTP
200 alone is not generation success. Sessions/turns done data is plain text
(session ID followed by reply); debug-chat done data is JSON.

Cinema requires a stable `Idempotency-Key` header. Round bodies take content,
option_index (0 is valid), custom_input and expected_revision, plus optional
model, temperature, max_tokens, top_p, max_context, pinned_memory,
conversation_style, `style_prompt_override`, user, lang and image_model. Those overrides apply to the
round. Cinema's outer SSE event name is `cinema`; parse data JSON and inspect
its inner `event` (including message_end and error), rather than waiting for a
chat-style done event. Event IDs are exposed by the SDK. Events are live
transport only; recover final state using operation, Round and image-task
queries after disconnect. A Last-Event-ID header must refer to an existing
operation for the same round; it does not guarantee historical event replay.

Image generate/result bodies require `session_id`. Generate accepts optional
model and only claims pending tasks. Result accepts status, image_url,
watermark_url, material_id and error; status defaults to ready, which requires
image_url. Costs are provider-reported strings or null. The SDK preserves
these values and does not invent cost estimates.

## Card creation, import and visibility

`POST /v1/cards` remains callable but is deprecated, with a documented sunset
of 2027-01-01. Existing create methods remain available for compatibility.
For cards already in the catalog, configure `control_api_base_url` to the full
`/admin/v1` base and use `cards.fork(project_id, {"catalog_ids": [...]})`.
The 1..100 catalog IDs are forked
independently: inspect both `items` and `errors` even on HTTP 200.

The legacy batch-import method still targets its explicitly configured Control
API base. Current release routes do not register either that legacy batch route
or the engine batch route shown in the main API document. It is retained for
older deployments; use catalog fork for current project onboarding.

Delegated engine imports/listing need short-lived project delegation. Main docs
show an import `{row}`, the migration guide shows `{source, content, publication}`,
and the release handler accepts `{card, overwrite?}`. Import bodies pass through
unchanged; use the payload supported by the target deployment. No automatic
payload conversion or fallback to a second write route is performed.

### Documentation and route differences

The main document lists `POST /v1/cards/{id}/versions`, but release registers
only GET there. Submit versioned edits through `PATCH /v1/cards/{id}` using
`base_version`, `expected_latest_version`, and optional `change_note`.
It also lists `GET /v1/sessions/{id}/history` for groups, but the registered
history list is `GET /v1/sessions/{id}?offset=&limit=`; use the existing session
get method for both single and group history. These unregistered routes are
not exposed as new SDK methods.

Plain-text and JSON HTTP errors are supported, with 400/422 mapped to invalid.
JSON error code/message and the complete response payload are retained; a
debug-chat error can include session_id to query before retrying.
Ordinary project responses may set `prompt_redacted: true`; do not interpret
empty prompt/messages as missing generation. Traces require prompt-inspection
delegation and return 404 for an ordinary project token.

## Python usage and migration

```python
client.cards.list({"lang": "zh", "limit": 20, "offset": 0})
client.cards.list_versions(card_id, {"limit": 20, "before_version": 7})
client.cards.get_version(card_id, 3, {"lang": "zh"})
client.cards.list_translations(card_id, 3)
client.cards.save_translations(card_id, 3, {
    "user_id": user_id, "expected_latest_version": 7, "lang": "zh",
    "translations": {"name": "艾达"},
})
client.cards.restore_version(card_id, 3, {"expected_latest_version": 7})
client.cinema.list_rounds(session_id, {"limit": 20, "offset": 0})
```

Version/round methods also keep the old option-only call form
(e.g. list_versions(id, with_header(...))). Restore now needs an explicit body.
Configure `ClientConfig(control_api_base_url="https://rp.example.com/admin/v1", ...)`,
then call `client.cards.fork(project_id, {"catalog_ids": [catalog_id]})`.
SSE events expose `id`; HTTP errors expose `payload` and `session_id`.

## Inspiration and translation reuse

`sessions.inspiration` posts `{}` or per-call `lang`, `model`,
`temperature`, `max_tokens`, `top_p`. It returns two suggestions with
`style=positive/neutral`, `text`, model and provider evidence. It does not modify
history/revision or create an operation. It calls the model on every request;
there is no idempotency or SSE variant. Thinking parameters, persona/card
fields and a body `session_id` are rejected by the server. Missing usage stays
null. Group sessions are unsupported.

`sessions.custom_task` posts `{pe, model}` plus optional `lang`, `temperature`,
and `max_tokens`; it reads session history without changing the session.
`cards.translate` invokes the server translation model and preserves existing
translations. `cards.untranslated` also accepts `card_ids`, `locales`,
`languages`, `fields`, `missing_only`, `q`, and `include_total`.

World books are available through `client.world_books`; list/create/delete are
project-scoped, while `catalog_list` and `catalog_get` provide read-only access
to the global catalog. Catalog writes are outside the public SDK.

`cards.untranslated` takes `locale`, optional `limit` (default 50, max 200),
`offset`, and `include_partial`; batch/inventory mode additionally accepts
card IDs, locales, languages, fields, `missing_only`, `q`, and `include_total`.
Its `summary` covers only the returned page. Explicit false and offset=0 are preserved.
`cards.fork_translations` takes
`{items: [{card_id, card_version, locales: [...]}]}`; inspect per-item `errors`
and `action=created/skipped`. Existing edited translations are preserved.

## Group cards and sessions

Use `group_cards` for story CRUD, immutable versions, members, imports,
preview, character inference, and owner translations. Lists, versions and
members return arrays; the version list currently returns at most 50 versions.
Group list filters are `q`, `listed`, `include_deleted`, `limit`, `offset`.
Get and version detail accept `lang`. Member removal is a DELETE with a JSON
body containing `user_id` and `expected_latest_version`; it soft-deletes the
member and preserves historic speaker attribution. Other roster changes pass
the documented body unchanged. Preview does not call a model; character
inference requires prompt-inspection permission.

Use `group_sessions` to create a session with `group_id`, optional `group_version`,
`user_id`, `user`, `mode`, `output_format`, `active_participant_ids`,
`max_context`, `pinned_memory`. Sessions pin both story and member versions.
Group turns take optional plain-text `content` or OpenAI `message` content parts
(mutually exclusive), optional `action`, `expected_revision`,
`addressed_participant_ids`, `style_prompt_override` and per-call sampling/prompt overrides. Supply a
stable `Idempotency-Key` request header for safe retries; without it, resending
can generate another paid turn. JSON responses flatten the session snapshot
and add `execution`, nullable `usage`, `operation` and `turn` (segments,
parser warnings, speaker validation and cost).

Group streaming uses the existing SSE parser: `operation`, `token`, `usage`,
`done`, `error`, plus `segment_start`, `segment_delta`, `segment_end` and
`parser_warning`. Data remains raw text; parse segment data as JSON.
Event IDs and `Last-Event-ID` pass through. A done frame contains the session
ID and canonical text on separate lines. Query the group turn after a disconnect;
handle errors and incomplete streams before treating text as committed.
Prompt lookup accepts `turn_id` and requires prompt-inspection permission.
Read group history and use edit/rewind/fork via the common session service.

## Cinema order and recovery updates

`cinema.list_rounds` accepts `order=asc/desc`; order determines where offset counts
from, while each returned array remains in ascending sequence order.
Use desc with offset=0 and limit=1 to fetch the latest round.
A completed Cinema round ends with inner `message_end`, not a chat done event.
Failed rounds are not committed; inspect the operation and session before a
new attempt with a new key.

Every explicit recover `abandon` requires `acknowledge_unknown: true`.
Terminal operations are retained for a documented default of 7 hours; unresolved
operations use the session TTL (default 1 day). Idempotency ends when evidence
expires, so persist business results and complete retries within that window.
Use the actual operation `deadline_ms`, not the historical capabilities
`operation_deadline_seconds`, for lease decisions.
