#!/usr/bin/env python3
"""Serve a directory on 127.0.0.1:PORT and [::1]:PORT with caching disabled, so a
browser reload always shows the latest render. Usage: static_server.py PORT DIR"""
import functools, http.server, socket, sys, threading

PORT, ROOT = int(sys.argv[1]), sys.argv[2]


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


class V6Server(http.server.ThreadingHTTPServer):
    address_family = socket.AF_INET6


handler = functools.partial(Handler, directory=ROOT)
servers = [http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)]
try:
    servers.append(V6Server(("::1", PORT), handler))
except OSError as e:
    print(f"IPv6 loopback not served: {e}", file=sys.stderr)
for s in servers[1:]:
    threading.Thread(target=s.serve_forever, daemon=True).start()
servers[0].serve_forever()
