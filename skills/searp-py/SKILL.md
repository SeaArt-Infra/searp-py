---
name: searp-py
description: Build and troubleshoot SeaRP engine and control-plane integrations with the searp-sdk Python client. Use when creating role-play sessions, running chat turns or streaming replies, using idempotent operations, importing cards, previewing versions, assembling prompts, generating images, debugging chats, or managing projects through the /admin/v1 gateway from Python.
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
   and the remaining services for cards, versions, and cinema. Use
   `client.admin` for the `/admin/v1` control plane.
3. Prefer the operations API with a stable idempotency key for paid chat.
4. HTTP 200 does not guarantee a generated reply; inspect operation `status`.
5. Pass request-specific SeaInfra attribution headers with `rp.WithHeaders`.

## Control Plane

```python
health = client.admin.health()
whoami = client.admin.whoami()
projects = client.admin.list_projects()
project = client.admin.create_project(
    {"id": "project-id", "token": "project-token-with-at-least-16-characters"}
)
```

For control-plane routes without a typed method, use
`client.admin.request(method, path, body, *options)`. Admin errors carry their
envelope `code` on `exc.code`.

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
session = client.sessions.create_experience({"user_id": "user-123"})
```

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
- `admin.request`, `health`, `whoami`, `agent_contract`, `list_projects`,
  `create_project`, `get_project`, `delete_project`, `rotate_project_token`,
  `get_project_live`, `update_project_live`
- `admin.raw`, `project_request`, `get_global_pack`, `update_global_pack`,
  `get_project_pack`, `patch_project_pack`, `delete_project_pack`,
  `fork_project_pack`
- `admin.list_catalog`, `import_catalog`, `get_catalog_card`,
  `update_catalog_card`, `delete_catalog_card`, `get_catalog_card_cover`
- `admin.list_project_cards`, `get_project_card`, `update_project_card`,
  `delete_project_card`, `set_project_card_listing`, `import_project_card`,
  `import_project_cards_batch`, `fork_project_card`,
  `list_project_card_versions`, `get_project_card_version`,
  `delete_project_card_version`, `restore_project_card_version`
- `admin.list_project_experiments`, `create_project_experiment`,
  `get_project_experiment`, `update_project_experiment`,
  `start_project_experiment`, `pause_project_experiment`,
  `stop_project_experiment`
- `admin.get_project_llm`, `update_project_llm`, `delete_project_llm`
- `admin.list_project_versions`, `create_project_version`,
  `get_project_version`, `diff_project_version`, `publish_project_version`,
  `get_project_release`, `list_project_releases`, `rollback_project_release`
- `admin.list_project_system_prompts`, `create_project_system_prompt`,
  `set_project_system_prompt_default`, `get_project_system_prompt`,
  `update_project_system_prompt`, `list_global_system_prompts`,
  `create_global_system_prompt`, `set_global_system_prompt_default`,
  `get_global_system_prompt`
- `admin.list_project_user_sessions`, `get_project_user_session`,
  `get_project_identity_migration`, `start_project_identity_migration`,
  `prepare_project_identity_migration`, `purge_project_identity_migration`,
  `adopt_project_identity_migration`, `revert_project_identity_migration`,
  `preview_project_identity_migration`
- `admin.list_project_rollouts`, `create_project_rollout`,
  `get_current_project_rollouts`, `get_project_rollout`,
  `update_project_rollout`, `delete_project_rollout`,
  `stop_project_rollout`, `list_project_rollout_audits`
- `admin.list_project_presets`, `create_project_preset`,
  `update_project_preset`, `publish_project_preset`,
  `list_project_sessions`, `update_project_session`
- `admin.list_project_suites`, `create_project_suite`, `get_project_suite`,
  `list_project_evaluations`, `get_project_evaluation`,
  `compare_project_evaluation`, `cancel_project_evaluation`,
  `resume_project_evaluation`, `list_project_feedback`,
  `create_project_feedback`
- `admin.project_engine`, `list_admin_cards`, `translations_queue`,
  `translations_callback`
