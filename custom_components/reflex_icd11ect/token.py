"""OAUTH 2.0 token helper for the WHO cloud ICD-API.

The cloud API at ``https://id.who.int`` requires a bearer token obtained with
the client credentials grant. Register at https://icd.who.int/icdapi to get a
client id and secret, then keep the secret on the backend: never ship it to
the browser.

Use it from a Reflex state so the token travels over the websocket only::

    provider = IcdTokenProvider.from_env()

    class State(rx.State):
        icd_token: str = ""

        @rx.event(background=True)
        async def refresh_token(self):
            token = await provider.async_token()
            async with self:
                self.icd_token = token

and pass ``token=State.icd_token`` plus
``on_token_request=State.refresh_token`` to the component.

A local ICD-API deployment (Docker container, Windows service, systemd
service) needs none of this: set ``api_secured=False``.
"""

from __future__ import annotations

import base64
import binascii
import dataclasses
import json
import os
import threading
import time
from typing import Any, Final

import httpx

from reflex_icd11ect.constants import ICD_TOKEN_ENDPOINT, ICD_TOKEN_SCOPE

#: Seconds of margin kept before a token is considered expired. ECT uses the
#: same margin when it decides to ask for a new one.
EXPIRY_MARGIN_SECONDS: Final[int] = 300


class IcdTokenError(RuntimeError):
    """Raised when a token could not be obtained."""


def decode_jwt_expiry(token: str) -> float | None:
    """Read the ``exp`` claim of a JWT without verifying its signature.

    Args:
        token: The encoded JWT.

    Returns:
        The expiry as a POSIX timestamp, or None when it cannot be read.

    """
    try:
        payload = token.split(".")[1]
        padded = payload + "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(padded))
    except (IndexError, ValueError, binascii.Error, UnicodeDecodeError):
        return None
    expiry = claims.get("exp")
    return float(expiry) if isinstance(expiry, (int, float)) else None


@dataclasses.dataclass
class IcdTokenProvider:
    """Fetches and caches ICD-API access tokens.

    The cached token is reused until it is within
    :data:`EXPIRY_MARGIN_SECONDS` of expiring, so calling ``token()`` on every
    request is cheap.
    """

    #: The client id from the ICD-API portal.
    client_id: str
    #: The client secret from the ICD-API portal. Kept out of ``repr()`` so it
    #: cannot reach a log line or a traceback by accident.
    client_secret: str = dataclasses.field(repr=False)
    #: The OAUTH 2.0 token endpoint.
    token_endpoint: str = ICD_TOKEN_ENDPOINT
    #: The OAUTH 2.0 scope.
    scope: str = ICD_TOKEN_SCOPE
    #: Timeout of the token request, in seconds.
    timeout: float = 20.0

    _token: str = dataclasses.field(default="", init=False, repr=False)
    _expires_at: float = dataclasses.field(default=0.0, init=False, repr=False)
    _lock: threading.Lock = dataclasses.field(
        default_factory=threading.Lock, init=False, repr=False
    )

    @classmethod
    def from_env(cls, prefix: str = "ICD_", **kwargs: Any) -> IcdTokenProvider:
        """Build a provider from environment variables.

        Reads ``<prefix>CLIENT_ID`` and ``<prefix>CLIENT_SECRET``, and
        ``<prefix>TOKEN_ENDPOINT`` when you point at another authority.

        Args:
            prefix: Prefix of the variable names.
            **kwargs: Overrides passed to the constructor.

        Returns:
            The configured provider.

        Raises:
            IcdTokenError: If the credentials are missing.

        """
        client_id = os.environ.get(f"{prefix}CLIENT_ID", "")
        client_secret = os.environ.get(f"{prefix}CLIENT_SECRET", "")
        if not client_id or not client_secret:
            msg = (
                f"{prefix}CLIENT_ID and {prefix}CLIENT_SECRET must be set; "
                "get them from https://icd.who.int/icdapi"
            )
            raise IcdTokenError(msg)
        endpoint = os.environ.get(f"{prefix}TOKEN_ENDPOINT")
        if endpoint:
            kwargs.setdefault("token_endpoint", endpoint)
        return cls(client_id=client_id, client_secret=client_secret, **kwargs)

    @property
    def _request_data(self) -> dict[str, str]:
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
            "grant_type": "client_credentials",
        }

    def _is_fresh(self) -> bool:
        return bool(self._token) and time.time() < self._expires_at

    def _store(self, payload: dict[str, Any]) -> str:
        token = payload.get("access_token", "")
        if not token:
            msg = f"the token endpoint returned no access_token: {payload!r}"
            raise IcdTokenError(msg)
        expiry = decode_jwt_expiry(token)
        if expiry is None:
            expires_in = float(payload.get("expires_in", 3600))
            expiry = time.time() + expires_in
        self._token = token
        self._expires_at = expiry - EXPIRY_MARGIN_SECONDS
        return token

    def token(self, force: bool = False) -> str:
        """Return a valid token, fetching a new one when needed.

        Args:
            force: Whether to ignore the cached token.

        Returns:
            The bearer token.

        Raises:
            IcdTokenError: If the request failed.

        """
        with self._lock:
            if not force and self._is_fresh():
                return self._token
            try:
                response = httpx.post(
                    self.token_endpoint, data=self._request_data, timeout=self.timeout
                )
                response.raise_for_status()
            except httpx.HTTPError as error:
                msg = f"could not get an ICD-API token: {error}"
                raise IcdTokenError(msg) from error
            return self._store(response.json())

    async def async_token(self, force: bool = False) -> str:
        """Return a valid token, fetching a new one when needed.

        Args:
            force: Whether to ignore the cached token.

        Returns:
            The bearer token.

        Raises:
            IcdTokenError: If the request failed.

        """
        if not force and self._is_fresh():
            return self._token
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.token_endpoint, data=self._request_data
                )
                response.raise_for_status()
        except httpx.HTTPError as error:
            msg = f"could not get an ICD-API token: {error}"
            raise IcdTokenError(msg) from error
        with self._lock:
            return self._store(response.json())

    @property
    def expires_at(self) -> float:
        """When the cached token stops being used, as a POSIX timestamp.

        Returns:
            The effective expiry, 0.0 when no token is cached.

        """
        return self._expires_at


__all__ = [
    "EXPIRY_MARGIN_SECONDS",
    "IcdTokenError",
    "IcdTokenProvider",
    "decode_jwt_expiry",
]
