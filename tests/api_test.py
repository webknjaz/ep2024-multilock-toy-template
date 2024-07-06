"""Tests for the Lokiverse API."""

from __future__ import annotations

import platform
import urllib
import uuid

import cheroot
import pytest
import requests
import requests_unixsocket

from lokiverse.api import serve_lokiverse_web_app


SYS_PLATFORM = platform.system()
IS_LINUX = SYS_PLATFORM == 'Linux'


@pytest.fixture
def abstract_socket_requests_connector():
    """Temporarily attach a ``unix+http://`` requests adapter."""
    with requests_unixsocket.monkeypatch():
        yield


@pytest.fixture
def abstract_sock_addr(request: pytest.FixtureRequest) -> str:
    """Return an abstract UNIX socket address."""
    if not IS_LINUX:
        pytest.skip(
            f'{SYS_PLATFORM} does not support an abstract socket namespace',
        )
    request.getfixturevalue('abstract_socket_requests_connector')
    return f'\x00lokiverse-test-socket-{uuid.uuid4() !s}'


@pytest.fixture
def network_sock_addr(request: pytest.FixtureRequest) -> tuple[str, int]:
    """Return an ephemeral network socket address."""
    return ('::', 0)


@pytest.fixture(params=('abstract', 'network'))
def web_server_listen_addr(
    request: pytest.FixtureRequest,
) -> str | tuple[str, int]:
    """Check that bound UNIX socket address is stored in server."""
    name = f'{request.param}_sock_addr'
    return request.getfixturevalue(name)


@pytest.fixture
def web_app(
    web_server_listen_addr: str | tuple[str, int],
) -> cheroot.wsgi.Server:
    with serve_lokiverse_web_app(web_server_listen_addr) as web_server:
        yield web_server


@pytest.fixture
def web_app_url(
    web_app: cheroot.wsgi.Server,
) -> str:
    if isinstance(web_app.bind_addr, tuple):
        return f'http://localhost:{web_app.bind_addr[1] !s}'

    urlencoded_sockname = urllib.parse.quote(web_app.bind_addr, safe='')
    return f'http+unix://{urlencoded_sockname !s}'


def test_hello_world_response(web_app_url: str) -> None:
    http_response = requests.get(web_app_url, timeout=1)
    http_response.raise_for_status()
    assert http_response.text == 'Hello world!'
