"""Tests for the OAUTH 2.0 token helper."""

from __future__ import annotations

import asyncio
import base64
import json
import time

import httpx
import pytest
from reflex_icd11ect.token import (
    EXPIRY_MARGIN_SECONDS,
    IcdTokenError,
    IcdTokenProvider,
    decode_jwt_expiry,
)


def _jwt(expires_in: int = 3600) -> str:
    payload = {"exp": int(time.time()) + expires_in, "scope": "icdapi_access"}
    encoded = (
        base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    )
    return f"header.{encoded}.signature"


def test_decode_jwt_expiry_reads_the_exp_claim():
    expiry = decode_jwt_expiry(_jwt(1800))
    assert expiry is not None
    assert 1700 < expiry - time.time() < 1900


def test_decode_jwt_expiry_is_forgiving():
    assert decode_jwt_expiry("not-a-jwt") is None
    assert decode_jwt_expiry("") is None
    assert decode_jwt_expiry("a.!!!.c") is None


def test_the_token_is_cached_until_shortly_before_it_expires():
    provider = IcdTokenProvider(client_id="id", client_secret="secret")
    token = _jwt(3600)
    provider._store({"access_token": token})
    assert provider.token() == token
    assert provider.expires_at == pytest.approx(
        decode_jwt_expiry(token) - EXPIRY_MARGIN_SECONDS
    )


def test_an_expired_token_is_not_reused():
    provider = IcdTokenProvider(client_id="id", client_secret="secret")
    provider._store({"access_token": _jwt(-10)})
    assert not provider._is_fresh()


def test_expires_in_is_used_when_the_token_is_not_a_jwt():
    provider = IcdTokenProvider(client_id="id", client_secret="secret")
    provider._store({"access_token": "opaque", "expires_in": 600})
    assert provider.expires_at == pytest.approx(
        time.time() + 600 - EXPIRY_MARGIN_SECONDS, abs=5
    )


def test_a_response_without_a_token_is_an_error():
    provider = IcdTokenProvider(client_id="id", client_secret="secret")
    with pytest.raises(IcdTokenError, match="no access_token"):
        provider._store({"error": "invalid_client"})


def test_from_env_requires_credentials(monkeypatch):
    monkeypatch.delenv("ICD_CLIENT_ID", raising=False)
    monkeypatch.delenv("ICD_CLIENT_SECRET", raising=False)
    with pytest.raises(IcdTokenError, match="ICD_CLIENT_ID"):
        IcdTokenProvider.from_env()


def test_from_env_reads_the_credentials_and_the_endpoint(monkeypatch):
    monkeypatch.setenv("ICD_CLIENT_ID", "id")
    monkeypatch.setenv("ICD_CLIENT_SECRET", "secret")
    monkeypatch.setenv("ICD_TOKEN_ENDPOINT", "https://example.test/token")
    provider = IcdTokenProvider.from_env()
    assert provider.client_id == "id"
    assert provider.token_endpoint == "https://example.test/token"


def test_the_request_uses_the_client_credentials_grant():
    provider = IcdTokenProvider(client_id="id", client_secret="secret")
    assert provider._request_data == {
        "client_id": "id",
        "client_secret": "secret",
        "scope": "icdapi_access",
        "grant_type": "client_credentials",
    }


def _mock_transport(handler):
    """Build a transport that answers with `handler(request)`."""
    return httpx.MockTransport(handler)


def _patch_httpx(monkeypatch, handler):
    """Route both the sync and the async token request through `handler`."""
    seen: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return handler(request)

    def fake_post(url, data=None, timeout=None):
        with httpx.Client(transport=_mock_transport(record)) as client:
            return client.post(url, data=data)

    class FakeAsyncClient(httpx.AsyncClient):
        def __init__(self, **kwargs):
            super().__init__(transport=_mock_transport(record), **kwargs)

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    return seen


def test_token_posts_the_client_credentials_grant(monkeypatch):
    issued = _jwt(3600)
    seen = _patch_httpx(
        monkeypatch,
        lambda request: httpx.Response(200, json={"access_token": issued}),
    )
    provider = IcdTokenProvider(client_id="id", client_secret="secret")

    assert provider.token() == issued
    assert str(seen[0].url) == provider.token_endpoint
    assert b"grant_type=client_credentials" in seen[0].content
    # The second call is served from the cache, the third one is forced.
    assert provider.token() == issued
    assert len(seen) == 1
    assert provider.token(force=True) == issued
    assert len(seen) == 2


def test_token_turns_a_failed_request_into_an_icd_token_error(monkeypatch):
    _patch_httpx(
        monkeypatch,
        lambda request: httpx.Response(401, json={"error": "invalid_client"}),
    )
    provider = IcdTokenProvider(client_id="id", client_secret="nope")
    with pytest.raises(IcdTokenError, match="could not get an ICD-API token"):
        provider.token()


async def _fetch(provider, **kwargs):
    return await provider.async_token(**kwargs)


def test_async_token_fetches_and_caches(monkeypatch):
    issued = _jwt(3600)
    seen = _patch_httpx(
        monkeypatch,
        lambda request: httpx.Response(200, json={"access_token": issued}),
    )
    provider = IcdTokenProvider(client_id="id", client_secret="secret")

    assert asyncio.run(_fetch(provider)) == issued
    assert asyncio.run(_fetch(provider)) == issued
    assert len(seen) == 1


def test_async_token_turns_a_failed_request_into_an_icd_token_error(monkeypatch):
    _patch_httpx(
        monkeypatch,
        lambda request: httpx.Response(500, text="boom"),
    )
    provider = IcdTokenProvider(client_id="id", client_secret="secret")
    with pytest.raises(IcdTokenError, match="could not get an ICD-API token"):
        asyncio.run(_fetch(provider))


def test_the_client_secret_stays_out_of_the_repr():
    provider = IcdTokenProvider(client_id="id", client_secret="s3cr3t")
    assert "s3cr3t" not in repr(provider)
    assert "id" in repr(provider)
