from __future__ import annotations

import json
import unittest
from io import BytesIO
from unittest.mock import Mock

import simple_rest_api
from simple_rest_api import SimpleRestHandler


class FakeSocket:
    def __init__(self, request_bytes: bytes):
        self._file = BytesIO(request_bytes)
        self.output = BytesIO()

    def makefile(self, mode: str, *args, **kwargs):
        if "r" in mode:
            return self._file
        return self.output

    def sendall(self, data: bytes) -> None:
        self.output.write(data)


class SimpleRestApiTests(unittest.TestCase):
    def setUp(self):
        simple_rest_api.ITEMS.clear()
        simple_rest_api.NEXT_ID = 1

    def request(self, raw: bytes):
        sock = FakeSocket(raw)
        SimpleRestHandler(sock, ("127.0.0.1", 12345), Mock())
        response = sock.output.getvalue()
        header_raw, body_raw = response.split(b"\r\n\r\n", 1)
        status_line = header_raw.splitlines()[0].decode("iso-8859-1")
        status = int(status_line.split()[1])
        headers = header_raw.decode("iso-8859-1")
        body = json.loads(body_raw.decode("utf-8"))
        return status, headers, body

    def test_health_success(self):
        status, headers, body = self.request(b"GET /health HTTP/1.1\r\nHost: test\r\n\r\n")
        self.assertEqual(status, 200)
        self.assertIn("Content-Type: application/json", headers)
        self.assertEqual(body, {"status": "ok"})

    def test_create_item_success(self):
        body = b'{"name": "demo"}'
        raw = (
            b"POST /items HTTP/1.1\r\n"
            b"Host: test\r\n"
            b"Content-Type: application/json\r\n"
            + f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
            + body
        )
        status, headers, payload = self.request(raw)
        self.assertEqual(status, 201)
        self.assertIn("Content-Type: application/json", headers)
        self.assertEqual(payload["item"], {"id": 1, "name": "demo"})

    def test_create_item_validation_error(self):
        body = b'{"name": ""}'
        raw = (
            b"POST /items HTTP/1.1\r\n"
            b"Host: test\r\n"
            b"Content-Type: application/json\r\n"
            + f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
            + body
        )
        status, headers, payload = self.request(raw)
        self.assertEqual(status, 400)
        self.assertIn("Content-Type: application/json", headers)
        self.assertEqual(payload, {"error": "name is required"})

    def test_not_found_error(self):
        status, headers, body = self.request(b"GET /missing HTTP/1.1\r\nHost: test\r\n\r\n")
        self.assertEqual(status, 404)
        self.assertIn("Content-Type: application/json", headers)
        self.assertEqual(body, {"error": "not found"})


if __name__ == "__main__":
    unittest.main()
