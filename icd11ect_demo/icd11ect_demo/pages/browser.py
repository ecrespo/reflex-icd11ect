"""The Embedded Browser page."""

from __future__ import annotations

import reflex as rx
from reflex_icd11ect import icd11ect

from icd11ect_demo.state import BrowserState
from icd11ect_demo.ui import (
    browser_props,
    card,
    ect_common_props,
    page,
    section,
    settings_panel,
)

INO = "browser"

EXAMPLE_CODES: tuple[tuple[str, str], ...] = (
    ("1B11", "Tuberculosis of lung"),
    ("5A11", "Type 2 diabetes mellitus"),
    ("6A60", "Bipolar type I disorder"),
    ("2C25.Z&XA2UD3", "postcoordinated expression"),
)


def controls() -> rx.Component:
    """Navigate the browser from the backend."""
    return section(
        "Navigate from the backend",
        "handler.set_browser_code and handler.set_browser_uri accept a single "
        "code or URI, or a postcoordinated expression joined with '&'.",
        rx.hstack(
            rx.input(
                value=BrowserState.goto_code,
                on_change=BrowserState.set_goto_code,
                placeholder="1B11",
                width="100%",
            ),
            rx.button("Go to code", on_click=BrowserState.go_to_code(INO)),
            width="100%",
            spacing="2",
        ),
        rx.hstack(
            rx.input(
                value=BrowserState.goto_uri,
                on_change=BrowserState.set_goto_uri,
                placeholder="http://id.who.int/icd/entity/1435254666",
                width="100%",
            ),
            rx.button("Go to URI", on_click=BrowserState.go_to_uri(INO)),
            width="100%",
            spacing="2",
        ),
        rx.flex(
            *[
                rx.tooltip(
                    rx.button(
                        code,
                        size="1",
                        variant="surface",
                        on_click=[
                            BrowserState.set_goto_code(code),
                            BrowserState.go_to_code(INO),
                        ],
                    ),
                    content=label,
                )
                for code, label in EXAMPLE_CODES
            ],
            wrap="wrap",
            spacing="2",
        ),
    )


def status_card() -> rx.Component:
    """What the browser reports back."""
    return card(
        rx.hstack(
            rx.heading("Browser events", size="4"),
            rx.spacer(),
            rx.cond(
                BrowserState.loaded,
                rx.badge("loaded", color_scheme="green"),
                rx.hstack(
                    rx.spinner(size="1"), rx.text("loading", size="1"), spacing="2"
                ),
            ),
            align="center",
            width="100%",
        ),
        rx.grid(
            rx.vstack(
                rx.text("on_browser_change", size="1", color_scheme="gray"),
                rx.hstack(
                    rx.cond(
                        BrowserState.code != "",
                        rx.badge(BrowserState.code, variant="solid"),
                        rx.text("-", size="2"),
                    ),
                    align="center",
                ),
                rx.code(BrowserState.uri, size="1", word_break="break-all"),
                spacing="1",
                align="start",
            ),
            rx.vstack(
                rx.text("on_select", size="1", color_scheme="gray"),
                rx.text(
                    rx.cond(BrowserState.picked != "", BrowserState.picked, "-"),
                    size="2",
                ),
                spacing="1",
                align="start",
            ),
            columns="2",
            spacing="4",
            width="100%",
        ),
        rx.cond(
            BrowserState.trail.length() > 0,
            rx.vstack(
                rx.text("trail", size="1", color_scheme="gray"),
                rx.flex(
                    rx.foreach(
                        BrowserState.trail,
                        lambda item: rx.badge(item, variant="soft", size="1"),
                    ),
                    wrap="wrap",
                    spacing="1",
                ),
                spacing="1",
                width="100%",
                align="start",
            ),
            rx.fragment(),
        ),
    )


def browser_page() -> rx.Component:
    """The Embedded Browser page.

    Returns:
        The page component.
    """
    return page(
        "Embedded Browser",
        "The full ICD-11 browser inside the page: hierarchy, search, "
        "postcoordination and, when enable_select_button is set, a way for the "
        "user to pick an entity.",
        section(
            "icd11ect.browser(...)",
            "Passing on_select sets enable_select_button to 'all' unless you "
            "choose another mode, because ECT ships no select button by default.",
            icd11ect.browser(
                ino=INO,
                window_props={"width": "100%"},
                on_select=BrowserState.on_select,
                on_browser_load=BrowserState.on_load,
                on_browser_change=BrowserState.on_change,
                **ect_common_props(),
                **browser_props(),
            ),
            width="100%",
        ),
        status_card(),
        controls(),
        settings_panel(coding=False, browser=True),
    )
