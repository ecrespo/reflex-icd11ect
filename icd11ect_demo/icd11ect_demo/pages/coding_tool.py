"""The Embedded Coding Tool page."""

from __future__ import annotations

import reflex as rx
from reflex_icd11ect import icd11ect

from icd11ect_demo.state import EXAMPLE_SEARCHES, CodingState
from icd11ect_demo.ui import (
    card,
    coding_tool_props,
    ect_common_props,
    page,
    section,
    settings_panel,
)

INO = "coding"


def field(label: str, value: rx.Var[str], mono: bool = False) -> rx.Component:
    """One line of the selection card."""
    return rx.cond(
        value != "",
        rx.hstack(
            rx.text(
                label, size="1", color_scheme="gray", width="10em", flex_shrink="0"
            ),
            rx.cond(
                mono,
                rx.code(value, size="1", variant="soft", word_break="break-all"),
                rx.text(value, size="2", word_break="break-word"),
            ),
            align="start",
            spacing="2",
            width="100%",
        ),
        rx.fragment(),
    )


def selection_card() -> rx.Component:
    """What the user picked last."""
    return card(
        rx.hstack(
            rx.heading("Selection", size="4"),
            rx.cond(
                CodingState.selected_is_postcoordinated,
                rx.badge("postcoordinated", color_scheme="purple"),
                rx.fragment(),
            ),
            rx.spacer(),
            rx.cond(
                CodingState.searching,
                rx.hstack(
                    rx.spinner(size="1"), rx.text("searching", size="1"), spacing="2"
                ),
                rx.fragment(),
            ),
            align="center",
            width="100%",
        ),
        rx.cond(
            CodingState.has_selection,
            rx.vstack(
                rx.hstack(
                    rx.badge(CodingState.selected_code, size="2", variant="solid"),
                    rx.text(CodingState.selected_title, weight="medium"),
                    align="center",
                    spacing="3",
                    wrap="wrap",
                ),
                field("selected_text", CodingState.selected_text),
                field("search_query", CodingState.selected_query),
                field(
                    "linearization_uri",
                    CodingState.selected_linearization_uri,
                    mono=True,
                ),
                field("foundation_uri", CodingState.selected_foundation_uri, mono=True),
                spacing="2",
                width="100%",
            ),
            rx.text(
                "Type at least three characters in the box above, then click a result.",
                size="2",
                color_scheme="gray",
            ),
        ),
        rx.hstack(
            rx.button(
                "Clear tool",
                on_click=CodingState.clear_all(INO),
                variant="soft",
                size="2",
            ),
            spacing="2",
        ),
    )


def programmatic_search() -> rx.Component:
    """Drive the tool from the backend."""
    return section(
        "Search from the backend",
        "reflex_icd11ect.handler mirrors ECT.Handler, so a state event handler "
        "can search, clear or navigate the tool.",
        rx.hstack(
            rx.input(
                value=CodingState.query,
                on_change=CodingState.set_query,
                placeholder="handler.search(...)",
                width="100%",
            ),
            rx.button("Search", on_click=CodingState.run_query(INO)),
            width="100%",
            spacing="2",
        ),
        rx.flex(
            *[
                rx.button(
                    query,
                    size="1",
                    variant="surface",
                    on_click=CodingState.search_example(query, INO),
                )
                for query in EXAMPLE_SEARCHES
            ],
            wrap="wrap",
            spacing="2",
        ),
    )


def history_table() -> rx.Component:
    """Everything picked in this session."""
    return card(
        rx.hstack(
            rx.heading("History", size="4"),
            rx.spacer(),
            rx.button(
                "Clear",
                size="1",
                variant="ghost",
                on_click=CodingState.clear_history,
            ),
            align="center",
            width="100%",
        ),
        rx.cond(
            CodingState.history.length() > 0,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Code"),
                        rx.table.column_header_cell("Title"),
                        rx.table.column_header_cell("Selected text"),
                        rx.table.column_header_cell("Query"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        CodingState.history,
                        lambda entry: rx.table.row(
                            rx.table.cell(rx.code(entry["code"])),
                            rx.table.cell(entry["title"]),
                            rx.table.cell(entry["selected_text"]),
                            rx.table.cell(
                                rx.text(
                                    entry["search_query"], size="1", color_scheme="gray"
                                )
                            ),
                        ),
                    ),
                ),
                variant="surface",
                size="1",
                width="100%",
            ),
            rx.text("Nothing selected yet.", size="2", color_scheme="gray"),
        ),
    )


def coding_tool_page() -> rx.Component:
    """The Coding Tool page.

    Returns:
        The page component.
    """
    return page(
        "Embedded Coding Tool",
        "One search box, one result window, bound to ECT and wired to Reflex "
        "events. The search box stays uncontrolled: ECT owns its value.",
        section(
            "icd11ect.coding_tool(...)",
            "on_select fires with the entity the user clicks; on_search_start "
            "and on_search_end drive the spinner in the card below.",
            icd11ect.coding_tool(
                ino=INO,
                placeholder="Search the ICD-11, e.g. 'fever' or 'diabetes'...",
                input_props={
                    "width": "100%",
                    "padding": "0.6em 0.8em",
                    "border_radius": "0.4em",
                    "border": f"1px solid {rx.color('gray', 7)}",
                },
                window_props={"width": "100%", "margin_top": "0.5em"},
                on_select=CodingState.on_select,
                on_search_start=CodingState.search_started,
                on_search_end=CodingState.search_ended,
                **ect_common_props(),
                **coding_tool_props(),
            ),
            width="100%",
        ),
        selection_card(),
        programmatic_search(),
        settings_panel(coding=True),
        history_table(),
    )
