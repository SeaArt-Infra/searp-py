from __future__ import annotations

import unittest
from unittest.mock import patch

from searp_sdk import (
    Client,
    ClientConfig,
    ERR_CONFLICT,
    ERR_NOT_FOUND,
    SeaRPError,
    ERR_NETWORK,
    SessionsService,
    with_header,
)
from searp_sdk.cards import CardsService
from searp_sdk.cinema import CinemaService
from searp_sdk.engine import EngineService
from searp_sdk.operations import OperationsService
from searp_sdk.versions import VersionsService
from searp_sdk.admin import AdminService
from urllib.parse import parse_qs, urlsplit


class FakeTransport:
    def __init__(self, status: int = 200, payload: bytes = b"{}") -> None:
        self.status = status
        self.payload = payload
        self.calls: list[dict] = []

    def request(self, method: str, path: str, body, headers):
        self.calls.append({"method": method, "path": path, "body": body, "headers": headers})
        return self.status, self.payload

    def request_stream(self, method: str, path: str, body, headers):
        self.calls.append({"method": method, "path": path, "body": body, "headers": headers})
        return [b"event: token\n", b"data: Hel\n", b"\n", b"event: done\n", b"data: s1\n", b"\n"]


class ClientTests(unittest.TestCase):
    def test_default_api_base_url(self) -> None:
        client = Client(ClientConfig(api_key="key"))
        self.assertEqual(client.api_base_url, "http://127.0.0.1:8788/v1")

    def test_explicit_api_base_url(self) -> None:
        client = Client(ClientConfig(api_key="key", base_url="https://rp.example.com/v1"))
        self.assertEqual(client.api_base_url, "https://rp.example.com/v1")
        self.assertIsInstance(client.Sessions, SessionsService)
        self.assertIsInstance(client.Operations, OperationsService)
        self.assertIsInstance(client.Engine, EngineService)
        self.assertIsInstance(client.Cards, CardsService)
        self.assertIsInstance(client.Versions, VersionsService)
        self.assertIsInstance(client.Cinema, CinemaService)


class AdminTests(unittest.TestCase):
    def test_health_path(self) -> None:
        transport = FakeTransport(payload=b'{"ok":true}')
        service = AdminService(transport)
        result = service.health()
        self.assertEqual(result["ok"], True)
        call = transport.calls[0]
        self.assertEqual(call["method"], "GET")
        self.assertEqual(call["path"], "/health")

    def test_get_project_encodes_path(self) -> None:
        transport = FakeTransport(payload=b'{"id":"a/b"}')
        service = AdminService(transport)
        result = service.get_project("a/b")
        self.assertEqual(result["id"], "a/b")
        self.assertEqual(transport.calls[0]["path"], "/projects/a%2Fb")

    def test_error_envelope(self) -> None:
        service = AdminService(FakeTransport(status=404, payload=b'{"error":{"code":"not_found","message":"project not found"}}'))
        with self.assertRaises(SeaRPError) as caught:
            service.get_project("missing")
        self.assertEqual(caught.exception.kind, ERR_NOT_FOUND)
        self.assertEqual(caught.exception.code, "not_found")
        self.assertEqual(caught.exception.status, 404)

    def test_project_and_catalog_paths(self) -> None:
        transport = FakeTransport(payload=b'{"ok":true}')
        service = AdminService(transport)
        service.list_project_versions("p1", {"cursor": "2"})
        service.diff_project_version("p1", "v1", "v0")
        service.get_catalog_card_cover("card-1")
        self.assertEqual(transport.calls[0]["path"], "/projects/p1/versions?cursor=2")
        self.assertEqual(transport.calls[1]["path"], "/projects/p1/versions/v1/diff?against=v0")
        self.assertEqual(transport.calls[2]["path"], "/catalog/card-1/cover")


class ErrorTests(unittest.TestCase):
    def test_network_error_can_be_constructed_without_code(self) -> None:
        error = SeaRPError(kind=ERR_NETWORK, message="request failed: dns")
        self.assertEqual(error.code, None)
        self.assertEqual(error.message, "request failed: dns")


class SessionsTests(unittest.TestCase):
    def test_create_path_body_and_headers(self) -> None:
        transport = FakeTransport(payload=b'{"id":"session-1","revision":1}')
        service = SessionsService(transport)
        result = service.create({"user_id": "u1"}, with_header("x-request-id", "req-1"))
        self.assertEqual(result["id"], "session-1")
        call = transport.calls[0]
        self.assertEqual(call["path"], "/sessions")
        self.assertEqual(call["body"], {"user_id": "u1"})
        self.assertEqual(call["headers"]["x-request-id"], ["req-1"])

    def test_not_found_error(self) -> None:
        service = SessionsService(FakeTransport(status=404, payload=b"session not found"))
        with self.assertRaises(SeaRPError) as caught:
            service.get("missing")
        self.assertEqual(caught.exception.kind, ERR_NOT_FOUND)
        self.assertEqual(caught.exception.status, 404)

    def test_turn_stream(self) -> None:
        service = SessionsService(FakeTransport())
        events = list(service.turn_stream("s1", {"action": "reply", "text": "hello"}))
        self.assertEqual([event.event for event in events], ["token", "done"])
        self.assertEqual(events[0].data, "Hel")
        self.assertTrue(events[1].done)

    def test_proactive_path_body_and_response(self) -> None:
        transport = FakeTransport(payload=b'{"id":"s1","revision":2,"text":"Hello again","operation":{"id":"p1"}}')
        service = SessionsService(transport)
        response = service.proactive("s1", {"idempotency_key": "p1"})
        self.assertEqual(response["text"], "Hello again")
        self.assertEqual(response["operation"]["id"], "p1")
        call = transport.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertEqual(call["path"], "/sessions/s1/proactive")
        self.assertEqual(call["body"], {"idempotency_key": "p1"})

    def test_proactive_stream(self) -> None:
        class ProactiveTransport(FakeTransport):
            def request_stream(self, method: str, path: str, body, headers):
                self.calls.append({"method": method, "path": path, "body": body, "headers": headers})
                return [b"event: operation\n", b"data: {\"id\":\"p1\"}\n", b"\n", b"event: token\n", b"data: Hi\n", b"\n", b"event: done\n", b"data: s1\n", b"\n"]

        service = SessionsService(ProactiveTransport())
        events = list(service.proactive_stream("s1", {"idempotency_key": "p1", "stream": True}))
        self.assertEqual([event.event for event in events], ["operation", "token", "done"])
        self.assertEqual(events[0].data, '{"id":"p1"}')


class OperationsTests(unittest.TestCase):
    def test_conflict_error(self) -> None:
        service = OperationsService(FakeTransport(status=409, payload=b"stale revision"))
        with self.assertRaises(SeaRPError) as caught:
            service.run("s1", {"idempotency_key": "k"})
        self.assertEqual(caught.exception.kind, ERR_CONFLICT)


class LatestContractTests(unittest.TestCase):
    def test_cinema_rounds_page_arrays_and_keep_legacy_options(self) -> None:
        transport = FakeTransport(payload=b'[{"round_id":"r1","cost":"0.01"}]')
        service = CinemaService(transport)
        caller = with_header("x-request-id", "req-1")
        rounds = service.list_rounds("s1", {"limit": 20, "offset": 0}, caller)
        service.list_rounds("s1", caller)
        self.assertEqual(rounds[0]["round_id"], "r1")
        self.assertEqual(parse_qs(urlsplit(transport.calls[0]["path"]).query), {"limit": ["20"], "offset": ["0"]})
        self.assertEqual(transport.calls[1]["headers"]["x-request-id"], ["req-1"])

    def test_batch_import_uses_explicit_control_api_and_project_token(self) -> None:
        client = Client(ClientConfig(api_key="project-key", base_url="https://engine.example", control_api_base_url="https://control.example/admin/v1/"))
        transport = client.cards._control_client
        body = {"cards": [{"name": "Ada", "introduction": "Pilot", "greeting": "Hi", "background": "Harbor"}]}

        def request(method, path, payload, headers):
            req = transport._build_request(method, path, payload, headers)
            self.assertEqual(req.full_url, "https://control.example/admin/v1/cards/import/batch")
            self.assertEqual(req.method, "POST")
            self.assertEqual(req.get_header("Authorization"), "Bearer project-key")
            self.assertEqual(req.get_header("X-request-id"), "req-1")
            self.assertEqual(payload, body)
            return 201, b'{"items":[{"id":"c1"}]}'

        with patch.object(type(transport), "request", side_effect=request):
            self.assertEqual(client.cards.import_batch(body, with_header("x-request-id", "req-1"))["items"][0]["id"], "c1")
        with self.assertRaisesRegex(SeaRPError, "control_api_base_url"):
            Client().cards.import_batch(body)

    def test_card_queries_translation_and_restore(self) -> None:
        transport = FakeTransport()
        service = CardsService(transport)
        caller = with_header("x-request-id", "req-1")
        service.list({"limit": 20, "offset": 0})
        service.list_by_user("u1", {"limit": 20, "offset": 0})
        service.list_versions("c1", {"limit": 20, "before_version": 7}, caller)
        service.get_version("c1", 3, {"lang": "zh"}, caller)
        service.list_versions("c1", caller)
        service.get_version("c1", 3, caller)
        service.list_translations("c1", 3)
        body = {"user_id": "u1", "expected_latest_version": 7, "lang": "zh", "translations": {"name": "艾达"}}
        service.save_translations("c1", 3, body, caller)
        service.restore_version("c1", 3, {"expected_latest_version": 7, "change_note": "restore"}, caller)
        calls = transport.calls
        self.assertEqual(parse_qs(urlsplit(calls[0]["path"]).query), {"limit": ["20"], "offset": ["0"]})
        self.assertEqual(parse_qs(urlsplit(calls[1]["path"]).query)["limit"], ["20"])
        self.assertEqual(parse_qs(urlsplit(calls[2]["path"]).query)["before_version"], ["7"])
        self.assertEqual(calls[3]["path"], "/cards/c1/versions/3?lang=zh")
        for index in (2, 3, 4, 5, 7, 8):
            self.assertEqual(calls[index]["headers"]["x-request-id"], ["req-1"])
        self.assertEqual(calls[6]["path"], "/cards/c1/versions/3/translations")
        self.assertEqual(calls[7]["method"], "POST")
        self.assertEqual(calls[7]["body"], body)
        self.assertEqual(calls[8]["body"], {"expected_latest_version": 7, "change_note": "restore"})
        with self.assertRaisesRegex(SeaRPError, "expected_latest_version"):
            service.restore_version("c1", 3)

    def test_liveness_metrics_and_json_error_evidence(self) -> None:
        transport = FakeTransport(payload=b'{"status":"live"}')
        service = EngineService(transport)
        self.assertEqual(service.live()["status"], "live")
        self.assertEqual(transport.calls[0]["path"], "/live")
        transport.payload = b"searp_requests_total 1\n"
        self.assertEqual(service.metrics(), "searp_requests_total 1\n")
        self.assertEqual(transport.calls[1]["path"], "/metrics")
        transport.status = 422
        transport.payload = b'{"error":{"code":"invalid","message":"unknown field"},"session_id":"s1"}'
        with self.assertRaises(SeaRPError) as caught:
            service.debug_chat({})
        self.assertEqual(caught.exception.kind, "invalid")
        self.assertEqual(caught.exception.code, "invalid")
        self.assertEqual(caught.exception.message, "unknown field")
        self.assertEqual(caught.exception.session_id, "s1")
        self.assertEqual(caught.exception.payload["session_id"], "s1")

    def test_cinema_sse_ids_whitespace_and_response_close(self) -> None:
        import io

        response = io.BytesIO(b"id: evt-2\nevent: cinema\ndata:  leading and trailing  \n\nevent: done\ndata: finished")
        transport = FakeTransport()

        def request_stream(method, path, body, headers):
            transport.calls.append({"method": method, "path": path, "body": body, "headers": headers})
            return response

        transport.request_stream = request_stream
        events = list(CinemaService(transport).create_round_stream("s1", {"content": "go"}, with_header("Last-Event-ID", "evt-1"), with_header("Idempotency-Key", "round-1")))
        headers = transport.calls[0]["headers"]
        self.assertEqual(headers["Accept"], ["text/event-stream"])
        self.assertEqual(headers["Last-Event-ID"], ["evt-1"])
        self.assertEqual(headers["Idempotency-Key"], ["round-1"])
        self.assertEqual(events[0].id, "evt-2")
        self.assertEqual(events[0].data, " leading and trailing  ")
        self.assertEqual(events[1].data, "finished")
        self.assertTrue(events[1].done)
        self.assertTrue(response.closed)

    def test_multimodal_chat_preserves_inputs_and_response_evidence(self) -> None:
        import json

        message = [{"type": "text", "text": "what?"}, {"type": "image_url", "image_url": {"url": "https://cdn.example/a.png", "detail": "auto"}}]
        body = {"action": "reply", "message": message, "lang": "zh", "lastest_system_prompt": "brief", "favorability_score": 45, "user": {"name": "Visitor"}, "metadata": {"history": [{"role": "user", "content": "hi"}]}, "top_p": 0.9, "thinking_mode": True}
        transport = FakeTransport(payload=json.dumps({"history": [{"role": "user", "content": message}], "history_import": {"seeded": {"messages": 1, "dropped": 0}}, "prompt_redacted": True}).encode())
        result = SessionsService(transport).turn("s1", body)
        self.assertEqual(transport.calls[0]["body"], body)
        self.assertEqual(result["history"][0]["content"], message)
        self.assertEqual(result["history_import"]["seeded"]["messages"], 1)
        self.assertTrue(result["prompt_redacted"])


if __name__ == "__main__":
    unittest.main()
