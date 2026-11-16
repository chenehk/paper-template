#!/usr/bin/env bash
# Serve the rendered site (_site/) on 127.0.0.1:PORT and [::1]:PORT, loopback only.
# Forward from your machine with  ssh -L PORT:localhost:PORT <this login node>
# or VS Code's Ports panel, then open http://localhost:PORT
# Nothing renders on request, so pages load instantly. Edits are rendered by
# tools/render.sh: the hook in .claude/settings.json runs it after Claude edits a file;
# after editing by hand, run  tools/render.sh <page.qmd>  (or with no argument for
# everything). Reload the browser once the render finishes (see .render.log).
set -e
cd "$(dirname "$0")/.."
port=${1:-4747}
# Login nodes are shared: another user's server may already hold the port.
if ss -ltn 2>/dev/null | awk '{print $4}' | grep -qE ":${port}$"; then
    echo "port $port is already in use on $(hostname); pick another: tools/preview.sh <port>" >&2
    exit 1
fi
[ -f _site/index.html ] || tools/refresh.sh
echo "serving _site on $(hostname):$port (IPv4 and IPv6 loopback); forward with: ssh -L $port:localhost:$port $(hostname)"
exec /usr/bin/python3 tools/static_server.py "$port" _site
