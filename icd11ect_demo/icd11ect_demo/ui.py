"""Shared layout and small building blocks for the demo."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import reflex as rx
from reflex_icd11ect import LANGUAGES, MMS_CHAPTERS, SOURCES

from icd11ect_demo.state import AuthState, Settings

NAV: tuple[tuple[str, str, str], ...] = (
    ("/", "Coding Tool", "search"),
    ("/browser", "Embedded Browser", "book-open"),
    ("/multi", "Many instances", "columns-3"),
    ("/custom", "Custom layout", "layout-dashboard"),
    ("/servers", "Servers & auth", "server"),
    ("/api", "API reference", "code"),
)

LINKS: tuple[tuple[str, str], ...] = (
    ("ECT documentation", "https://icd.who.int/docs/icd-api/icd11ect/"),
    ("@whoicd/icd11ect", "https://www.npmjs.com/package/@whoicd/icd11ect"),
    ("ICD-11 browser", "https://icd.who.int/browse11"),
    ("reflex-icd11ect", "https://github.com/ecrespo/reflex-icd11ect"),
)


def ect_common_props(**overrides: Any) -> dict[str, Any]:
    """Settings every instance of the demo shares.

    Args:
        **overrides: Props replacing the shared ones for this instance. A
            value of None drops the prop, which lets ECT keep its default.

    Returns:
        The props to spread onto a component.
    """
    props: dict[str, Any] = {
        "api_server_url": Settings.api_server_url,
        "api_secured": Settings.api_secured,
        "minor_version": Settings.minor_version,
        "language": Settings.language,
        "source": Settings.source,
        "source_app": "reflex-icd11ect-demo",
        "height": Settings.height,
        "hierarchy_resizable": Settings.hierarchy_resizable,
        "other_postcoordination": Settings.other_postcoordination,
        "include_diagnostic_criteria": Settings.include_diagnostic_criteria,
        "verbose": Settings.verbose,
        "token": AuthState.token,
        "on_token_request": AuthState.refresh_token,
    }
    props.update(overrides)
    return props


def coding_tool_props() -> dict[str, Any]:
    """Coding Tool settings driven by the settings panel.

    Returns:
        The props to spread onto a Coding Tool.
    """
    return {
        "popup_mode": Settings.popup_mode,
        "simplified_mode": Settings.simplified_mode,
        "disable_hierarchy": Settings.disable_hierarchy,
        "words_available": Settings.words_available,
        "chapters_available": Settings.chapters_available,
        "flexisearch_available": Settings.flexisearch_available,
        "search_by_code_or_uri": Settings.search_by_code_or_uri,
        "chapters_filter": Settings.chapters_filter,
    }


def browser_props() -> dict[str, Any]:
    """Embedded Browser settings driven by the settings panel.

    Returns:
        The props to spread onto an Embedded Browser.
    """
    return {
        "enable_select_button": Settings.enable_select_button,
        "browser_search_available": Settings.browser_search_available,
        "browser_advanced_search_available": Settings.browser_advanced_search_available,
        "browser_hierarchy_available": Settings.browser_hierarchy_available,
        "browser_uri": Settings.browser_uri,
    }


def card(*children, **props) -> rx.Component:
    """A titled panel.

    Args:
        *children: The content.
        **props: Extra props for the card.

    Returns:
        The card component.
    """
    return rx.card(rx.vstack(*children, spacing="3", width="100%"), size="2", **props)


def section(title: str, description: str, *children, **props) -> rx.Component:
    """A card with a heading and a lead paragraph.

    Args:
        title: The heading.
        description: The lead paragraph.
        *children: The content.
        **props: Extra props for the card.

    Returns:
        The section component.
    """
    return card(
        rx.heading(title, size="4"),
        rx.text(description, size="2", color_scheme="gray"),
        *children,
        **props,
    )


def switch_row(label: str, value: rx.Var[bool], field: str) -> rx.Component:
    """A labelled switch bound to one boolean setting.

    Args:
        label: The label.
        value: The current value.
        field: Name of the field on the Settings state.

    Returns:
        The switch row.
    """
    return rx.hstack(
        rx.switch(checked=value, on_change=Settings.toggle(field)),
        rx.text(label, size="2"),
        spacing="2",
        align="center",
    )


def select_row(
    label: str,
    items: list[str],
    value: rx.Var[str],
    on_change: Callable[..., Any],
    **props,
) -> rx.Component:
    """A labelled select.

    Args:
        label: The label.
        items: The options.
        value: The current value.
        on_change: Handler called with the new value.
        **props: Extra props for the select.

    Returns:
        The select row.
    """
    return rx.vstack(
        rx.text(label, size="1", weight="medium", color_scheme="gray"),
        rx.select(items, value=value, on_change=on_change, width="100%", **props),
        spacing="1",
        width="100%",
    )


def text_row(
    label: str,
    value: rx.Var[str],
    on_change: Callable[..., Any],
    placeholder: str = "",
) -> rx.Component:
    """A labelled text input.

    Args:
        label: The label.
        value: The current value.
        on_change: Handler called with the new value.
        placeholder: The placeholder.

    Returns:
        The input row.
    """
    return rx.vstack(
        rx.text(label, size="1", weight="medium", color_scheme="gray"),
        rx.input(
            value=value,
            on_change=on_change,
            placeholder=placeholder,
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def chapter_filter() -> rx.Component:
    """Checkboxes that build the ``chapters_filter`` string.

    Returns:
        The chapter filter component.
    """
    return rx.vstack(
        rx.hstack(
            rx.text("chapters_filter", size="1", weight="medium", color_scheme="gray"),
            rx.code(rx.cond(Settings.chapters_filter, Settings.chapters_filter, "all")),
            rx.spacer(),
            rx.button(
                "reset",
                size="1",
                variant="ghost",
                on_click=Settings.set_chapters_filter(""),
            ),
            width="100%",
            align="center",
        ),
        rx.flex(
            *[
                rx.tooltip(
                    rx.checkbox(
                        code,
                        checked=Settings.chapters_filter.contains(code),
                        on_change=Settings.toggle_chapter(code),
                        size="1",
                    ),
                    content=title,
                )
                for code, title in MMS_CHAPTERS.items()
            ],
            wrap="wrap",
            spacing="3",
            width="100%",
        ),
        spacing="2",
        width="100%",
    )


def settings_panel(coding: bool = True, browser: bool = False) -> rx.Component:
    """The live settings panel.

    Args:
        coding: Whether to show the Coding Tool settings.
        browser: Whether to show the Embedded Browser settings.

    Returns:
        The settings panel.
    """
    shared = [
        select_row(
            "language",
            list(LANGUAGES),
            Settings.language,
            Settings.set_language,
        ),
        select_row("source", list(SOURCES), Settings.source, Settings.set_source),
        text_row("height", Settings.height, Settings.set_height, "60vh"),
        text_row(
            "minor_version",
            Settings.minor_version,
            Settings.set_minor_version,
            "latest release",
        ),
    ]
    toggles = [
        switch_row(
            "include_diagnostic_criteria",
            Settings.include_diagnostic_criteria,
            "include_diagnostic_criteria",
        ),
        switch_row(
            "other_postcoordination",
            Settings.other_postcoordination,
            "other_postcoordination",
        ),
        switch_row(
            "hierarchy_resizable", Settings.hierarchy_resizable, "hierarchy_resizable"
        ),
        switch_row("verbose (console)", Settings.verbose, "verbose"),
    ]
    if coding:
        toggles = [
            switch_row("popup_mode", Settings.popup_mode, "popup_mode"),
            switch_row("simplified_mode", Settings.simplified_mode, "simplified_mode"),
            switch_row(
                "disable_hierarchy", Settings.disable_hierarchy, "disable_hierarchy"
            ),
            switch_row("words_available", Settings.words_available, "words_available"),
            switch_row(
                "chapters_available", Settings.chapters_available, "chapters_available"
            ),
            switch_row(
                "flexisearch_available",
                Settings.flexisearch_available,
                "flexisearch_available",
            ),
            switch_row(
                "search_by_code_or_uri",
                Settings.search_by_code_or_uri,
                "search_by_code_or_uri",
            ),
            *toggles,
        ]
    if browser:
        toggles = [
            switch_row(
                "browser_search_available",
                Settings.browser_search_available,
                "browser_search_available",
            ),
            switch_row(
                "browser_advanced_search_available",
                Settings.browser_advanced_search_available,
                "browser_advanced_search_available",
            ),
            switch_row(
                "browser_hierarchy_available",
                Settings.browser_hierarchy_available,
                "browser_hierarchy_available",
            ),
            *toggles,
        ]
    extra: list[rx.Component] = []
    if browser:
        extra.append(
            select_row(
                "enable_select_button",
                ["none", "categories", "all", "allButRoot"],
                Settings.enable_select_button,
                Settings.set_enable_select_button,
            )
        )
        extra.append(
            text_row(
                "browser_uri",
                Settings.browser_uri,
                Settings.set_browser_uri,
                "http://id.who.int/icd/entity/1435254666",
            )
        )
    return section(
        "Settings",
        "Every control writes a component prop. Changing one reconfigures ECT "
        "and rebinds the instances on the page.",
        rx.grid(*shared, *extra, columns="2", spacing="3", width="100%"),
        rx.divider(),
        rx.flex(*toggles, wrap="wrap", spacing="4", width="100%"),
        *([rx.divider(), chapter_filter()] if coding else []),
        width="100%",
    )


def sidebar() -> rx.Component:
    """The navigation sidebar.

    Returns:
        The sidebar component.
    """
    return rx.vstack(
        rx.hstack(
            rx.icon("stethoscope", size=22),
            rx.heading("reflex-icd11ect", size="4"),
            align="center",
            spacing="2",
        ),
        rx.text(
            "WHO ICD-11 Embedded Classification Tools, as a Reflex component.",
            size="1",
            color_scheme="gray",
        ),
        rx.divider(),
        rx.vstack(
            *[
                rx.link(
                    rx.hstack(
                        rx.icon(icon, size=16),
                        rx.text(label, size="2"),
                        align="center",
                        spacing="2",
                    ),
                    href=href,
                    underline="none",
                    color_scheme="gray",
                    width="100%",
                    padding="0.35em 0.5em",
                    border_radius="0.4em",
                    _hover={"background": rx.color("accent", 3)},
                )
                for href, label, icon in NAV
            ],
            spacing="1",
            width="100%",
        ),
        rx.spacer(),
        rx.divider(),
        rx.vstack(
            *[
                rx.link(label, href=url, is_external=True, size="1")
                for label, url in LINKS
            ],
            spacing="1",
            align="start",
        ),
        rx.hstack(rx.color_mode.button(), justify="start", width="100%"),
        spacing="3",
        padding="1.25em",
        width="16em",
        min_width="16em",
        height="100vh",
        position="sticky",
        top="0",
        border_right=f"1px solid {rx.color('gray', 5)}",
    )


def server_banner() -> rx.Component:
    """A reminder of which server the page talks to.

    Returns:
        The banner component.
    """
    return rx.callout(
        rx.hstack(
            rx.text("Server:", size="1", weight="bold"),
            rx.code(Settings.api_server_url, size="1"),
            rx.text("|", size="1", color_scheme="gray"),
            rx.text("api_secured:", size="1", weight="bold"),
            rx.code(Settings.api_secured.to_string(), size="1"),
            rx.cond(
                Settings.api_secured,
                rx.cond(
                    AuthState.token != "",
                    rx.badge("token loaded", color_scheme="green", size="1"),
                    rx.badge("no token", color_scheme="red", size="1"),
                ),
                rx.fragment(),
            ),
            spacing="2",
            align="center",
            wrap="wrap",
        ),
        icon="server",
        size="1",
        color_scheme="gray",
        width="100%",
    )


def page(title: str, subtitle: str, *children) -> rx.Component:
    """The page shell.

    Args:
        title: The page heading.
        subtitle: The lead paragraph.
        *children: The page content.

    Returns:
        The page component.
    """
    return rx.hstack(
        sidebar(),
        rx.vstack(
            rx.heading(title, size="7"),
            rx.text(subtitle, color_scheme="gray"),
            server_banner(),
            *children,
            spacing="4",
            padding="2em",
            width="100%",
            max_width="78em",
        ),
        align="start",
        spacing="0",
        width="100%",
    )
