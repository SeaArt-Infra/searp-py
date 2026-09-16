from __future__ import annotations

import unittest

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


class OperationsTests(unittest.TestCase):
    def test_conflict_error(self) -> None:
        service = OperationsService(FakeTransport(status=409, payload=b"stale revision"))
        with self.assertRaises(SeaRPError) as caught:
            service.run("s1", {"idempotency_key": "k"})
        self.assertEqual(caught.exception.kind, ERR_CONFLICT)


if __name__ == "__main__":
    unittest.main()
