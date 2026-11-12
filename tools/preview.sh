#!/usr/bin/env bash
# Serve the site with live reload on 127.0.0.1:PORT, plus a relay on [::1]:PORT
# (tools that resolve "localhost" to IPv6 then still connect). Loopback only.
# Forward from your machine with  ssh -L PORT:localhost:PORT <this login node>
# or VS Code's Ports panel, then open http://localhost:PORT
set -e
cd "$(dirname "$0")/.."
. tools/activate_quarto.sh
port=${1:-4747}
# Login nodes are shared: another user's server may already hold the port.
if ss -ltn 2>/dev/null | awk '{print $4}' | grep -qE ":${port}$"; then
    echo "port $port is already in use on $(hostname); pick another: tools/preview.sh <port>" >&2
    exit 1
fi
/usr/bin/python3 tools/loopback_proxy.py "$port" &
relay=$!
trap 'kill $relay 2>/dev/null' EXIT INT TERM
# Render everything once up front; otherwise preview renders each page on its
# first visit (seconds to tens of seconds per page here). Afterwards a page whose
# .qmd changed re-renders when next opened. Changes to included tables, results,
# chapters or _quarto.yml need tools/refresh.sh. Run only one preview per project.
quarto render --to html
echo "serving on $(hostname):$port (IPv4 and IPv6 loopback); forward with: ssh -L $port:localhost:$port $(hostname)"
quarto preview --port "$port" --no-browser --host 127.0.0.1
