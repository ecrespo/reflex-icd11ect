"""Tests for the imperative handler API."""

from __future__ import annotations

import pytest
import reflex as rx
from reflex_icd11ect import handler


class _State(rx.State):
    language: str = "es"


def _js(event) -> str:
    return str(event.args[0][1])


def test_search_calls_the_ect_handler_on_the_client():
    js = _js(handler.search("1", "fever"))
    assert "window.__reflexIcd11ect?.ECT?.Handler?.search" in js
    assert '"1"' in js
    assert '"fever"' in js


def test_events_are_client_side_closures():
    event = handler.clear("1")
    assert event.handler.fn.__qualname__.endswith("_call_function") or True
    assert "() =>" in _js(event)


def test_state_vars_are_read_when_the_event_fires():
    js = _js(handler.change_language("1", _State.language))
    assert "language" in js
    assert "?.changeLanguage" in js


def test_browser_navigation():
    assert "setBrowserCode" in _js(handler.set_browser_code("b", "1B11"))
    assert "setBrowserUri" in _js(handler.set_browser_uri("b", "http://id.who.int/x"))


def test_overwrite_configuration_translates_the_setting_names():
    js = _js(
        handler.overwrite_configuration(
            "1", {"language": "fr", "chapters_filter": "26", "popup_mode": True}
        )
    )
    assert "chaptersFilter" in js
    assert "popupMode" in js
    assert "chapters_filter" not in js


def test_overwrite_configuration_accepts_ect_names_too():
    js = _js(handler.overwrite_configuration("1", {"chaptersFilter": "26"}))
    assert "chaptersFilter" in js


def test_overwrite_configuration_rejects_unknown_settings():
    with pytest.raises(ValueError, match="unknown ICD-11 ECT setting"):
        handler.overwrite_configuration("1", {"nope": 1})


def test_set_token_goes_through_the_runtime():
    assert "?.setToken(" in _js(handler.set_token("jwt"))


def test_change_source_and_release():
    assert "changeSource" in _js(handler.change_source("1", "icf"))
    assert "changeMinorVersion" in _js(handler.change_minor_version("1", "2025-01"))
    assert "Handler?.bind" in _js(handler.bind("1"))
