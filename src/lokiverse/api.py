"""Lokiverse API."""

from __future__ import annotations

from contextlib import contextmanager
from logging import getLogger
from threading import Thread
from time import sleep
from typing import Any, Callable, Iterator

from cheroot.wsgi import Server as WSGIServer


def _produce_hello_world_http_response(
    _environ: dict[str, Any],
    start_response: Callable[
        [str, list[tuple[str, str]]],
        Callable[[bytes], None],
    ],
):
    """Respond with 200 OK over HTTP."""
    http_response_status = '200 OK'
    http_response_headers = [('Content-type', 'text/plain')]

    start_response(http_response_status, http_response_headers)

    return [b'Hello world!']


@contextmanager
def serve_lokiverse_web_app(
    bind_addr: str | tuple[str, int],
) -> Iterator[WSGIServer]:
    """Spawn a web server listening to the port given.

    This context manager cleans up its resources on exit.
    """
    http_server = WSGIServer(
        bind_addr=bind_addr,
        wsgi_app=_produce_hello_world_http_response,
    )
    server_thread = Thread(target=http_server.safe_start)

    server_thread.start()
    while not http_server.ready:
        sleep(0.1)

    loggable_bound_socket_addr = (
        ':'.join(map(str, http_server.bind_addr))
        if isinstance(http_server.bind_addr, tuple)
        else '@' + http_server.bind_addr[1:]
    )
    getLogger().info(f'Listening on {loggable_bound_socket_addr}...')

    try:
        yield http_server
    finally:
        http_server.stop()
        server_thread.join()
