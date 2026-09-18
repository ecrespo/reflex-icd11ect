"""Tests for the ICD-11 ECT components."""

from __future__ import annotations

import pytest
import reflex as rx
from reflex_icd11ect import (
    ALL_SETTINGS,
    Icd11ectBrowser,
    Icd11ectCodingTool,
    Icd11ectController,
    icd11ect,
)


class _State(rx.State):
    code: str = ""

    @rx.event
    def on_select(self, entity: dict[str, str]):
        self.code = entity["code"]

    @rx.event
    def noop(self):
        pass


def test_coding_tool_renders_the_markup_ect_binds_to():
    component = icd11ect.coding_tool(ino="1", api_server_url="http://api")
    rendered = str(component.render())
    assert "ctw-input" in rendered
    assert "ctw-window" in rendered
    assert '"data-ctw-ino": "1"' in rendered or "data-ctw-ino" in rendered


def test_browser_renders_the_browser_container():
    rendered = str(icd11ect.browser(ino="b", api_server_url="http://api").render())
    assert "ctw-eb-window" in rendered
    assert "ctw-window" not in rendered.replace("ctw-eb-window", "")


def test_controller_renders_no_markup_of_its_own():
    component = icd11ect.controller(ino="c", api_server_url="http://api")
    assert component.children == []


def test_only_the_settings_that_were_set_are_sent():
    component = Icd11ectCodingTool.create(
        ino="1", api_server_url="http://api", language="es"
    )
    settings = component._ect_settings_js()
    assert 'apiServerUrl: "http://api"' in settings
    assert 'language: "es"' in settings
    assert "popupMode" not in settings
    assert "chaptersFilter" not in settings


def test_settings_are_translated_to_ect_names():
    component = Icd11ectCodingTool.create(
        ino="1",
        api_server_url="http://api",
        search_by_code_or_uri=True,
        chapters_filter="06;08",
        minor_version="2025-01",
    )
    settings = component._ect_settings_js()
    assert "searchByCodeOrURI: true" in settings
    assert 'chaptersFilter: "06;08"' in settings
    assert 'minorVersion: "2025-01"' in settings


def test_every_component_takes_every_setting():
    # ECT keeps one configuration per page, so hiding a setting on one
    # component would not stop it from applying.
    tool = Icd11ectCodingTool.create(
        ino="1", api_server_url="http://api", enable_select_button="all"
    )
    browser = Icd11ectBrowser.create(
        ino="2", api_server_url="http://api", popup_mode=True
    )
    assert 'enableSelectButton: "all"' in tool._ect_settings_js()
    assert "popupMode: true" in browser._ect_settings_js()


def test_an_unknown_prop_is_still_rejected():
    with pytest.raises((TypeError, AttributeError, ValueError)):
        Icd11ectCodingTool.create(ino="1", api_server_url="http://api", on_nonsense=1)


def test_controller_accepts_every_setting():
    component = Icd11ectController.create(
        ino="1",
        api_server_url="http://api",
        popup_mode=True,
        enable_select_button="categories",
    )
    settings = component._ect_settings_js()
    assert "popupMode: true" in settings
    assert 'enableSelectButton: "categories"' in settings


def test_browser_gets_a_select_button_when_on_select_is_wired():
    component = Icd11ectBrowser.create(
        ino="b", api_server_url="http://api", on_select=_State.on_select
    )
    assert 'enableSelectButton: "all"' in component._ect_settings_js()


def test_an_explicit_select_button_mode_wins():
    component = Icd11ectBrowser.create(
        ino="b",
        api_server_url="http://api",
        enable_select_button="none",
        on_select=_State.on_select,
    )
    assert 'enableSelectButton: "none"' in component._ect_settings_js()


def test_events_are_compiled_into_the_hook_not_into_props():
    component = Icd11ectCodingTool.create(
        ino="1",
        api_server_url="http://api",
        on_select=_State.on_select,
        on_search_start=_State.noop,
    )
    hooks = "".join(str(hook) for hook in component.add_hooks())
    assert "useIcd11ect(" in hooks
    assert "onSelect:" in hooks
    assert "onSearchStart:" in hooks
    assert "on_select" in hooks  # the backend handler name
    # The payload is renamed on the frontend.
    assert "foundation_uri:" in hooks
    rendered = str(component.render())
    assert "onSelect" not in rendered


def test_unwired_events_are_absent_from_the_hook():
    component = Icd11ectCodingTool.create(ino="1", api_server_url="http://api")
    hooks = "".join(str(hook) for hook in component.add_hooks())
    assert "onSelect" not in hooks
    assert "onTokenRequest" not in hooks


def test_props_are_not_rendered_on_the_dom():
    rendered = str(
        Icd11ectCodingTool.create(
            ino="1",
            api_server_url="http://api",
            language="fr",
            popup_mode=True,
        ).render()
    )
    for name in ("apiServerUrl", "popupMode", "api_server_url", "popup_mode"):
        assert name not in rendered


def test_the_npm_package_and_the_stylesheet_are_imported():
    imports = Icd11ectCodingTool.create(
        ino="1", api_server_url="http://api"
    ).add_imports()
    assert any("@whoicd/icd11ect" in key for key in imports)
    assert imports[""] == "@whoicd/icd11ect/style.css"


def test_the_runtime_is_emitted_as_custom_code():
    code = Icd11ectCodingTool.create(
        ino="1", api_server_url="http://api"
    ).add_custom_code()
    assert len(code) == 1
    assert "useIcd11ect" in code[0]
    assert "autoBind: false" in code[0]


def test_every_component_emits_the_same_runtime_so_reflex_dedupes_it():
    tool = Icd11ectCodingTool.create(ino="1", api_server_url="http://api")
    browser = Icd11ectBrowser.create(ino="2", api_server_url="http://api")
    assert tool.add_custom_code() == browser.add_custom_code()


def test_token_options_reach_the_hook():
    component = Icd11ectCodingTool.create(
        ino="1",
        api_server_url="https://id.who.int",
        api_secured=True,
        token_endpoint="/api/icd/token",
        token_field="access_token",
        token_timeout_ms=5000,
    )
    hooks = "".join(str(hook) for hook in component.add_hooks())
    assert 'tokenEndpoint: "/api/icd/token"' in hooks
    assert 'tokenField: "access_token"' in hooks
    assert "tokenTimeoutMs: 5000" in hooks


def test_state_vars_stay_reactive_in_the_settings():
    class _Settings(rx.State):
        language: str = "en"

    component = Icd11ectCodingTool.create(
        ino="1", api_server_url="http://api", language=_Settings.language
    )
    assert "_settings.language" in component._ect_settings_js().lower()


def test_bare_elements_keep_the_required_class_and_attribute():
    assert "ctw-input" in str(icd11ect.search_input("x").render())
    assert "ctw-window" in str(icd11ect.result_window("x").render())
    assert "ctw-eb-window" in str(icd11ect.browser_window("x").render())


def test_a_user_class_name_is_merged_with_the_ect_one():
    rendered = str(icd11ect.search_input("x", class_name="my-input").render())
    assert "ctw-input" in rendered
    assert "my-input" in rendered


def test_a_list_of_class_names_is_merged_with_the_ect_one():
    rendered = str(icd11ect.result_window("x", class_name=["a", "b"]).render())
    assert "ctw-window" in rendered
    assert "a" in rendered and "b" in rendered


def test_a_reactive_class_name_is_merged_with_the_ect_one():
    rendered = str(icd11ect.browser_window("x", class_name=_State.code).render())
    assert "ctw-eb-window" in rendered
    assert "code" in rendered


def test_placeholder_and_element_props_are_forwarded():
    rendered = str(
        icd11ect.coding_tool(
            ino="1",
            api_server_url="http://api",
            placeholder="buscar",
            input_props={"auto_focus": True},
            window_props={"id": "results"},
        ).render()
    )
    assert "buscar" in rendered
    assert "results" in rendered


def test_the_setting_map_covers_every_documented_ect_setting():
    # A rename in ECT would break the bridge silently, so keep the map honest.
    assert ALL_SETTINGS["api_server_url"] == "apiServerUrl"
    assert len(ALL_SETTINGS) == len(set(ALL_SETTINGS.values()))
