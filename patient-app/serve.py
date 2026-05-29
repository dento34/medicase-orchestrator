"""Tiny static dev server for the patient app.

Usage:
    python patient-app/serve.py
    # then open http://localhost:5173/?case=demo-001&lang=pt

No dependencies — stdlib only. For production we deploy public/ to Vercel.
"""
from __future__ import annotations

import http.server
import socketserver
from pathlib import Path

PORT = 5173
ROOT = Path(__file__).parent / "public"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        # Allow mic/speech on localhost
        self.send_header("Permissions-Policy", "microphone=(self)")
        super().end_headers()


def main() -> None:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Patient app serving at http://localhost:{PORT}/")
        print(f"Try:  http://localhost:{PORT}/?case=demo-001&lang=pt")
        print("Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")


if __name__ == "__main__":
    main()
