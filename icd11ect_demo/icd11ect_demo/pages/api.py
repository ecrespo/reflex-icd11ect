"""A reference of everything the component exposes."""

from __future__ import annotations

import reflex as rx
from reflex_icd11ect import (
    BROWSER_SETTINGS,
    CODING_TOOL_SETTINGS,
    COMMON_SETTINGS,
    ECT_VERSION,
    OVERWRITABLE_SETTINGS,
)

from icd11ect_demo.ui import card, page, section

EVENTS: tuple[tuple[str, str, str], ...] = (
    (
        "on_select",
        "selectedEntityFunction",
        "The user picked an entity. Receives code, title, uri, "
        "linearization_uri, foundation_uri, selected_text, search_query.",
    ),
    ("on_search_start", "searchStartedFunction", "A search started. No arguments."),
    ("on_search_end", "searchEndedFunction", "A search ended. No arguments."),
    (
        "on_browser_load",
        "browserLoadedFunction",
        "The Embedded Browser finished its first load. No arguments.",
    ),
    (
        "on_browser_change",
        "browserChangedFunction",
        "The Embedded Browser shows another entity. Receives code and uri.",
    ),
    (
        "on_token_request",
        "getNewTokenFunction",
        "ECT needs a fresh OAUTH 2.0 token. Answer by setting the token prop.",
    ),
)

HANDLERS: tuple[tuple[str, str], ...] = (
    ("handler.search(ino, query)", "Search as if the user had typed the query."),
    ("handler.clear(ino)", "Empty the search box and the results."),
    ("handler.set_browser_code(ino, code)", "Show an entity in the browser, by code."),
    ("handler.set_browser_uri(ino, uri)", "Show an entity in the browser, by URI."),
    (
        "handler.change_language(ino, language)",
        "Switch one instance to another language.",
    ),
    ("handler.change_source(ino, source)", "Switch between mms, icf and foundation."),
    ("handler.change_minor_version(ino, release)", "Switch to another release."),
    (
        "handler.overwrite_configuration(ino, settings)",
        "Change the overridable settings of one instance at runtime.",
    ),
    ("handler.bind(ino)", "Bind an instance again after moving it in the DOM."),
    ("handler.set_token(token)", "Push a token without re-rendering."),
)

COMPONENTS: tuple[tuple[str, str], ...] = (
    ("icd11ect.coding_tool(...)", "Search box plus result window, bound and ready."),
    ("icd11ect.browser(...)", "The Embedded Browser."),
    ("icd11ect.controller(...)", "Lifecycle only, renders nothing."),
    ("icd11ect.provider(...)", "The controller used as page wide settings."),
    ("icd11ect.search_input(ino)", "The bare input element."),
    ("icd11ect.result_window(ino)", "The bare result container."),
    ("icd11ect.browser_window(ino)", "The bare browser container."),
)


def settings_table(
    title: str, description: str, settings: dict[str, str]
) -> rx.Component:
    """One table of props."""
    return section(
        title,
        description,
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Reflex prop"),
                    rx.table.column_header_cell("ECT setting"),
                    rx.table.column_header_cell("Per instance"),
                ),
            ),
            rx.table.body(
                *[
                    rx.table.row(
                        rx.table.cell(rx.code(python_name)),
                        rx.table.cell(rx.code(ect_name, variant="soft")),
                        rx.table.cell(
                            rx.cond(
                                ect_name in OVERWRITABLE_SETTINGS,
                                rx.badge("yes", color_scheme="green", size="1"),
                                rx.badge("page wide", color_scheme="gray", size="1"),
                            )
                        ),
                    )
                    for python_name, ect_name in settings.items()
                ],
            ),
            variant="surface",
            size="1",
            width="100%",
        ),
        width="100%",
    )


def two_column_table(
    title: str,
    description: str,
    rows: tuple[tuple[str, ...], ...],
    headers: tuple[str, ...],
) -> rx.Component:
    """A simple reference table."""
    return section(
        title,
        description,
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    *[rx.table.column_header_cell(header) for header in headers]
                ),
            ),
            rx.table.body(
                *[
                    rx.table.row(
                        *[
                            rx.table.cell(
                                rx.code(cell) if index == 0 else rx.text(cell, size="1")
                            )
                            for index, cell in enumerate(row)
                        ]
                    )
                    for row in rows
                ],
            ),
            variant="surface",
            size="1",
            width="100%",
        ),
        width="100%",
    )


def api_page() -> rx.Component:
    """The API reference page.

    Returns:
        The page component.
    """
    return page(
        "API reference",
        f"Generated from the component itself, against @whoicd/icd11ect {ECT_VERSION}.",
        two_column_table(
            "Components",
            "Every factory is also available as a class, e.g. Icd11ectCodingTool.",
            COMPONENTS,
            ("Factory", "What it renders"),
        ),
        two_column_table(
            "Events",
            "Reflex event triggers and the ECT callback behind each one.",
            tuple(
                (name, callback, description) for name, callback, description in EVENTS
            ),
            ("Prop", "ECT callback", "When it fires"),
        ),
        two_column_table(
            "Imperative API",
            "from reflex_icd11ect import handler. Each function returns an "
            "event you return from a state handler.",
            HANDLERS,
            ("Function", "What it does"),
        ),
        settings_table(
            "Shared settings",
            "Every component accepts every setting: ECT keeps one "
            "configuration per page, so hiding one would only mislead.",
            COMMON_SETTINGS,
        ),
        settings_table(
            "Coding Tool settings",
            "They shape the search box and its results.",
            CODING_TOOL_SETTINGS,
        ),
        settings_table(
            "Embedded Browser settings",
            "They shape the embedded browser.",
            BROWSER_SETTINGS,
        ),
        card(
            rx.heading("Page wide versus per instance", size="4"),
            rx.text(
                "ECT keeps one configuration for the whole page. The component "
                "merges the settings of every mounted instance into it, then "
                "applies what an instance sets differently through "
                "ECT.Handler.overwriteConfiguration. Only the settings marked "
                "'yes' above can differ per instance; the others take the value "
                "of the last instance that set them.",
                size="2",
                color_scheme="gray",
            ),
        ),
    )
