"""Custom layouts: the controller and the bare elements, placed by hand."""

from __future__ import annotations

import reflex as rx
from reflex_icd11ect import icd11ect

from icd11ect_demo.state import CodingState
from icd11ect_demo.ui import card, ect_common_props, page, section

SPLIT_INO = "split"
POPUP_INO = "popup"


def split_demo() -> rx.Component:
    """The controller, the input and the window in three different places."""
    return section(
        "controller + search_input + result_window",
        "icd11ect.controller does the binding and renders nothing, so the "
        "search box can live in a form header while the results render "
        "somewhere else entirely.",
        icd11ect.controller(
            ino=SPLIT_INO,
            simplified_mode=True,
            on_select=CodingState.on_select,
            **ect_common_props(height="40vh"),
        ),
        rx.grid(
            card(
                rx.heading("Patient encounter", size="3"),
                rx.text("Diagnosis", size="1", color_scheme="gray"),
                icd11ect.search_input(
                    SPLIT_INO,
                    placeholder="start typing a diagnosis...",
                    width="100%",
                    padding="0.6em 0.8em",
                    border_radius="0.4em",
                    border=f"1px solid {rx.color('gray', 7)}",
                ),
                rx.text(
                    rx.cond(
                        CodingState.has_selection,
                        "Coded as " + CodingState.selected_code,
                        "not coded yet",
                    ),
                    size="1",
                    color_scheme="gray",
                ),
                rx.text("Notes", size="1", color_scheme="gray"),
                rx.text_area(placeholder="free text...", width="100%", rows="4"),
                width="100%",
            ),
            card(
                rx.heading("Results", size="3"),
                rx.text(
                    "This is the same instance: the window only needs the same ino.",
                    size="1",
                    color_scheme="gray",
                ),
                icd11ect.result_window(SPLIT_INO, width="100%"),
                width="100%",
            ),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="3",
            width="100%",
        ),
        rx.code_block(
            'icd11ect.controller(ino="split", on_select=State.on_select, ...)\n'
            'icd11ect.search_input("split", placeholder="...")\n'
            'icd11ect.result_window("split")',
            language="python",
            width="100%",
        ),
        width="100%",
    )


def popup_demo() -> rx.Component:
    """popup_mode, which turns the window into a dropdown."""
    return section(
        "popup_mode",
        "With popup_mode the results float over the page instead of taking "
        "room in the flow, which is what you want inside a form.",
        icd11ect.coding_tool(
            ino=POPUP_INO,
            popup_mode=True,
            simplified_mode=True,
            placeholder="popup search...",
            input_props={
                "width": "100%",
                "padding": "0.6em 0.8em",
                "border_radius": "0.4em",
                "border": f"1px solid {rx.color('gray', 7)}",
            },
            window_props={"width": "100%"},
            on_select=CodingState.on_select,
            **ect_common_props(height="50vh"),
        ),
        rx.text(
            "The two instances on this page share the server settings; only "
            "the layout differs.",
            size="1",
            color_scheme="gray",
        ),
        width="100%",
    )


def custom_page() -> rx.Component:
    """The custom layout page.

    Returns:
        The page component.
    """
    return page(
        "Custom layout",
        "Three components for one tool: a controller that owns the lifecycle, "
        "and the two bare elements ECT binds to.",
        split_demo(),
        popup_demo(),
        card(
            rx.heading("icd11ect.provider", size="4"),
            rx.text(
                "The controller with no elements is a page wide provider: put "
                "it once in your layout with the server, the language and the "
                "token handling, and the tools on the page inherit them. Any "
                "prop you set on a tool still wins over the provider.",
                size="2",
                color_scheme="gray",
            ),
            rx.code_block(
                "def layout(content):\n"
                "    return rx.fragment(\n"
                "        icd11ect.provider(\n"
                '            api_server_url="https://id.who.int",\n'
                "            api_secured=True,\n"
                "            token=AuthState.token,\n"
                "            on_token_request=AuthState.refresh_token,\n"
                "        ),\n"
                "        content,\n"
                "    )",
                language="python",
                width="100%",
            ),
        ),
    )
