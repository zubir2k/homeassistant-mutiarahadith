"""Fixtures for MyHadith tests."""
from __future__ import annotations

import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        import pytest_socket

        def _win_disable_socket(allow_unix_socket=False):
            pass

        pytest_socket.disable_socket = _win_disable_socket
    except ImportError:
        pass

import pytest
import aiohttp
from unittest.mock import patch


@pytest.fixture(autouse=True)
def no_aiodns():
    """Mocked sessions still build a connector; keep aiodns from leaving a pycares thread."""
    with patch("aiohttp.connector.DefaultResolver", aiohttp.ThreadedResolver), \
         patch("homeassistant.helpers.aiohttp_client.AsyncResolver", aiohttp.ThreadedResolver):
        yield


@pytest.fixture(autouse=True)
def no_http_server():
    """The card needs the http and frontend components; don't open a real port."""
    with patch("homeassistant.components.http.HomeAssistantHTTP.start"):
        yield


FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Let Home Assistant load custom_components/mutiara_hadith."""
    if sys.platform == "win32":
        try:
            import pytest_socket

            pytest_socket.enable_socket()
        except ImportError:
            pass
    yield
    if sys.platform == "win32":
        try:
            import pytest_socket

            pytest_socket.enable_socket()
        except ImportError:
            pass


@pytest.fixture
def mock_site(aioclient_mock):
    """Serve the saved MyHadith pages."""
    aioclient_mock.get("https://myhadith.islam.gov.my/", text=load_fixture("home.html"))
    aioclient_mock.get(
        "https://myhadith.islam.gov.my/hadith/1061", text=load_fixture("hadith_1061.html")
    )
    return aioclient_mock
