#!/usr/bin/env bash
# Serve the site with live reload. Forward from your machine with
#   ssh -L PORT:localhost:PORT <this login node>   and open http://localhost:PORT
set -e
cd "$(dirname "$0")/.."
. tools/activate_quarto.sh
port=${1:-4200}
echo "serving on $(hostname):$port; forward with: ssh -L $port:localhost:$port $(hostname)"
exec quarto preview --port "$port" --no-browser --host 127.0.0.1
