#!/usr/bin/env python3
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

ITEMS: dict[int, dict[str, Any]] = {}
NEXT_ID = 1


def make_response(status: int, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    return status, payload


class SimpleRestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict[str, Any] | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            data = json.loads(raw.decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            return None
        return data if isinstance(data, dict) else None

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if self.path == "/items":
            self._send_json(200, {"items": list(ITEMS.values())})
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        global NEXT_ID
        if self.path != "/items":
            self._send_json(404, {"error": "not found"})
            return
        data = self._read_json()
        if data is None or not isinstance(data.get("name"), str) or not data["name"].strip():
            self._send_json(400, {"error": "name is required"})
            return
        item = {"id": NEXT_ID, "name": data["name"].strip()}
        ITEMS[NEXT_ID] = item
        NEXT_ID += 1
        self._send_json(201, {"item": item})

    def log_message(self, format: str, *args: Any) -> None:
        return


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = HTTPServer((host, port), SimpleRestHandler)
    print(f"Serving on http://{host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    run()
