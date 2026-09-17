"""Several instances on one page, each with its own settings."""

from __future__ import annotations

import reflex as rx
from reflex_icd11ect import icd11ect

from icd11ect_demo.state import CodingState, Settings
from icd11ect_demo.ui import card, ect_common_props, page, section

#: (ino, language, chapters filter, heading)
INSTANCES: tuple[tuple[str, str, str, str], ...] = (
    ("m-en", "en", "", "English, every chapter"),
    ("m-es", "es", "06", "Espanol, chapter 06 (mental health)"),
    ("m-fr", "fr", "11;12", "Francais, chapters 11 and 12"),
)


def instance(ino: str, language: str, chapters: str, heading: str) -> rx.Component:
    """One Coding Tool with its own language and chapter filter."""
    # Each instance overrides the shared language and height with its own.
    common = ect_common_props(language=language, height="34vh")
    return card(
        rx.vstack(
            rx.hstack(
                rx.badge(language.upper(), variant="solid"),
                rx.text(heading, size="2", weight="medium"),
                align="center",
                spacing="2",
            ),
            rx.text(f'ino="{ino}"', size="1", color_scheme="gray"),
            icd11ect.coding_tool(
                ino=ino,
                chapters_filter=chapters,
                simplified_mode=True,
                placeholder="search...",
                input_props={
                    "width": "100%",
                    "padding": "0.5em 0.7em",
                    "border_radius": "0.4em",
                    "border": f"1px solid {rx.color('gray', 7)}",
                },
                window_props={"width": "100%", "margin_top": "0.4em"},
                on_select=CodingState.on_select_instance,
                **common,
            ),
            rx.divider(),
            rx.text(
                rx.cond(
                    CodingState.per_instance[ino],
                    CodingState.per_instance[ino],
                    "nothing selected",
                ),
                size="1",
                weight="medium",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def multi_page() -> rx.Component:
    """The many instances page.

    Returns:
        The page component.
    """
    return page(
        "Many instances",
        "ECT keeps one configuration per page, so the component configures it "
        "once and applies what differs per instance through "
        "ECT.Handler.overwriteConfiguration. Every instance needs its own ino.",
        section(
            "Three Coding Tools, three languages",
            "They share the server and release from the settings panel but "
            "each one overrides language and chapters_filter. All three run in "
            "simplified_mode to keep the page readable.",
            rx.grid(
                *[instance(*args) for args in INSTANCES],
                columns=rx.breakpoints(initial="1", md="3"),
                spacing="3",
                width="100%",
            ),
            width="100%",
        ),
        card(
            rx.heading("Why one ino per instance", size="4"),
            rx.text(
                "ino becomes the data-ctw-ino attribute ECT binds to. The "
                "search box and the result window of an instance share it, and "
                "ECT reports it back on every callback, which is how the "
                "component routes events to the right Reflex handler.",
                size="2",
                color_scheme="gray",
            ),
            rx.code_block(
                'icd11ect.coding_tool(ino="m-es", language="es")',
                language="python",
                width="100%",
            ),
        ),
        card(
            rx.heading("Shared server", size="4"),
            rx.hstack(
                rx.text("api_server_url", size="1", color_scheme="gray"),
                rx.code(Settings.api_server_url, size="1"),
                align="center",
                spacing="2",
            ),
        ),
    )
