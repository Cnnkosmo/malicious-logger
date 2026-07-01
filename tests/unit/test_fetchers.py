from unittest.mock import patch

import httpx
import pytest
import respx

from malicious_logger.exceptions import FetchError, RateLimitedError
from malicious_logger.fetchers import BaseFetcher, build_client
from malicious_logger.fetchers.urlhaus import URLHausFetcher
from malicious_logger.fetchers.alienvault import AlienVaultFetcher
from malicious_logger.fetchers.openphish import OpenPhishFetcher

FAKE_PAYLOAD = b"# comment\nhttp://evil.com/malware\n"


@pytest.fixture
def client():
    return build_client()


@pytest.fixture(autouse=True)
def no_retry_wait():
    # we have to patch tenacity's sleep so it won't actually sleep
    with patch("tenacity.nap.time.sleep"):
        yield



def test_all_sources_registered():
    assert set(BaseFetcher._registry.keys()) == {"urlhaus", "alienvault", "openphish"}


def test_registry_returns_correct_class():
    assert BaseFetcher._registry["urlhaus"] is URLHausFetcher
    assert BaseFetcher._registry["alienvault"] is AlienVaultFetcher
    assert BaseFetcher._registry["openphish"] is OpenPhishFetcher


@respx.mock
def test_urlhaus_fetch_returns_content(client):
    respx.get(URLHausFetcher.source_url).mock(
        return_value=httpx.Response(200, content=FAKE_PAYLOAD)
    )
    result = URLHausFetcher().fetch(client)
    assert result == FAKE_PAYLOAD


@respx.mock
def test_openphish_fetch_returns_content(client):
    respx.get(OpenPhishFetcher.source_url).mock(
        return_value=httpx.Response(200, content=FAKE_PAYLOAD)
    )
    result = OpenPhishFetcher().fetch(client)
    assert result == FAKE_PAYLOAD


@respx.mock
def test_alienvault_fetch_returns_content(client):
    respx.get(AlienVaultFetcher.source_url).mock(
        return_value=httpx.Response(200, content=FAKE_PAYLOAD)
    )
    result = AlienVaultFetcher().fetch(client)
    assert result == FAKE_PAYLOAD

#non retryiable errs
@respx.mock
def test_404_raises_fetch_error_immediately(client):
    respx.get(URLHausFetcher.source_url).mock(
        return_value=httpx.Response(404)
    )
    with pytest.raises(FetchError) as exc_info:
        URLHausFetcher().fetch(client)

    # should not retry called exactly once
    assert respx.calls.call_count == 1
    assert "404" in str(exc_info.value)


@respx.mock
def test_403_raises_fetch_error_immediately(client):
    respx.get(URLHausFetcher.source_url).mock(
        return_value=httpx.Response(403)
    )
    with pytest.raises(FetchError):
        URLHausFetcher().fetch(client)

    assert respx.calls.call_count == 1

@respx.mock
def test_503_retries_then_raises_fetch_error(client, monkeypatch):
    monkeypatch.setattr("malicious_logger.config.settings.max_retries", 2)
    respx.get(URLHausFetcher.source_url).mock(
        return_value=httpx.Response(503)
    )
    with pytest.raises(FetchError):
        URLHausFetcher().fetch(client)

    assert respx.calls.call_count == 2


@respx.mock
def test_500_retries_then_raises_fetch_error(client, monkeypatch):
    monkeypatch.setattr("malicious_logger.config.settings.max_retries", 2)
    respx.get(URLHausFetcher.source_url).mock(
        return_value=httpx.Response(500)
    )
    with pytest.raises(FetchError):
        URLHausFetcher().fetch(client)

    assert respx.calls.call_count == 2


@respx.mock
def test_503_succeeds_on_retry(client, monkeypatch):
    monkeypatch.setattr("malicious_logger.config.settings.max_retries", 3)
    respx.get(URLHausFetcher.source_url).mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, content=FAKE_PAYLOAD),
        ]
    )
    result = URLHausFetcher().fetch(client)
    assert result == FAKE_PAYLOAD
    assert respx.calls.call_count == 2

@respx.mock
def test_429_raises_rate_limited_error(client):
    respx.get(URLHausFetcher.source_url).mock(
        return_value=httpx.Response(429)
    )
    with pytest.raises(RateLimitedError) as exc_info:
        URLHausFetcher().fetch(client)

    assert exc_info.value.source_name == "urlhaus"
