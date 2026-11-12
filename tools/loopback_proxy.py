#!/usr/bin/env python3
"""Relay [::1]:PORT to 127.0.0.1:PORT, so a server bound to IPv4 loopback is also
reachable through tools that resolve "localhost" to ::1 (e.g. VS Code port forwarding)."""
import asyncio, sys

PORT = int(sys.argv[1])


async def pipe(reader, writer):
    try:
        while data := await reader.read(65536):
            writer.write(data)
            await writer.drain()
    except (ConnectionError, OSError):
        pass
    finally:
        writer.close()


async def handle(cr, cw):
    try:
        sr, sw = await asyncio.open_connection("127.0.0.1", PORT)
    except OSError:
        cw.close()
        return
    await asyncio.gather(pipe(cr, sw), pipe(sr, cw))


async def main():
    server = await asyncio.start_server(handle, "::1", PORT)
    async with server:
        await server.serve_forever()


asyncio.run(main())
