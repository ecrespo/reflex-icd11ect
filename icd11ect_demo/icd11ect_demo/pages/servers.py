"""Server and authentication page."""

from __future__ import annotations

import reflex as rx
from reflex_icd11ect import WHO_CLOUD_API, WHO_DEVELOPER_TEST_API, icd11ect

from icd11ect_demo.state import SERVER_PRESETS, AuthState, CodingState, Settings
from icd11ect_demo.ui import card, ect_common_props, page, section, text_row

INO = "auth-check"


def presets() -> rx.Component:
    """Switch every instance to another server."""
    return section(
        "Where the ICD-API lives",
        "api_server_url and api_secured are the only required settings. "
        "Changing them here reconfigures ECT for the whole app.",
        rx.vstack(
            *[
                rx.hstack(
                    rx.button(
                        label,
                        on_click=Settings.set_api_server_url(url),
                        variant=rx.cond(
                            Settings.api_server_url == url, "solid", "surface"
                        ),
                        size="2",
                    ),
                    rx.code(url, size="1"),
                    align="center",
                    spacing="3",
                    wrap="wrap",
                )
                for label, url in SERVER_PRESETS.items()
            ],
            spacing="2",
            align="start",
            width="100%",
        ),
        rx.divider(),
        rx.grid(
            text_row(
                "api_server_url",
                Settings.api_server_url,
                Settings.set_api_server_url,
                WHO_DEVELOPER_TEST_API,
            ),
            rx.vstack(
                rx.text("api_secured", size="1", weight="medium", color_scheme="gray"),
                rx.hstack(
                    rx.switch(
                        checked=Settings.api_secured,
                        on_change=Settings.set_api_secured,
                    ),
                    rx.text("OAUTH 2.0 bearer token", size="2"),
                    align="center",
                    spacing="2",
                ),
                spacing="1",
                width="100%",
            ),
            columns="2",
            spacing="3",
            width="100%",
        ),
    )


def token_card() -> rx.Component:
    """Token status and the round trip that refreshes it."""
    return card(
        rx.hstack(
            rx.heading("OAUTH 2.0 token", size="4"),
            rx.spacer(),
            rx.cond(
                AuthState.token != "",
                rx.badge("token in state", color_scheme="green"),
                rx.badge("no token", color_scheme="red"),
            ),
            align="center",
            width="100%",
        ),
        rx.text(
            "reflex_icd11ect.IcdTokenProvider asks "
            "icdaccessmanagement.who.int for a token with the client "
            "credentials grant, caches it and refreshes it five minutes before "
            "it expires. It runs on the backend, so the client secret never "
            "reaches the browser; only the token does, over the websocket.",
            size="2",
            color_scheme="gray",
        ),
        rx.hstack(
            rx.button("Request a token", on_click=AuthState.refresh_token),
            rx.button("Forget it", variant="soft", on_click=AuthState.forget_token),
            rx.text(
                "ECT asked " + AuthState.requests.to_string() + " time(s)",
                size="1",
                color_scheme="gray",
            ),
            spacing="3",
            align="center",
            wrap="wrap",
        ),
        rx.callout(
            AuthState.status,
            icon=rx.cond(AuthState.failed, "triangle-alert", "info"),
            color_scheme=rx.cond(AuthState.failed, "red", "gray"),
            size="1",
            width="100%",
        ),
        rx.code_block(
            "export ICD_CLIENT_ID=...\n"
            "export ICD_CLIENT_SECRET=...\n"
            "# then restart the app",
            language="bash",
            width="100%",
        ),
    )


def flows() -> rx.Component:
    """The three ways of giving ECT a token."""
    return section(
        "Three ways to hand over a token",
        "Pick the one that matches your deployment.",
        rx.vstack(
            card(
                rx.heading("1. token prop, refreshed from the backend", size="3"),
                rx.text(
                    "The recommended flow. ECT fires on_token_request when its "
                    "token expires; answer it by setting the token prop.",
                    size="2",
                    color_scheme="gray",
                ),
                rx.code_block(
                    "icd11ect.coding_tool(\n"
                    '    api_server_url="https://id.who.int",\n'
                    "    api_secured=True,\n"
                    "    token=AuthState.token,\n"
                    "    on_token_request=AuthState.refresh_token,\n"
                    ")",
                    language="python",
                    width="100%",
                ),
                width="100%",
            ),
            card(
                rx.heading("2. token_endpoint", size="3"),
                rx.text(
                    "The pattern WHO documents: the browser fetches a token "
                    "from an endpoint of yours. Simple, but anyone who can "
                    "reach the endpoint gets tokens.",
                    size="2",
                    color_scheme="gray",
                ),
                rx.code_block(
                    "icd11ect.coding_tool(\n"
                    '    api_server_url="https://id.who.int",\n'
                    "    api_secured=True,\n"
                    '    token_endpoint="/api/icd/token",\n'
                    '    token_field="token",\n'
                    ")",
                    language="python",
                    width="100%",
                ),
                width="100%",
            ),
            card(
                rx.heading("3. no token at all", size="3"),
                rx.text(
                    "A local ICD-API deployment (Docker container, Windows "
                    "service, systemd service) needs no authentication, and "
                    "keeps every query inside your network.",
                    size="2",
                    color_scheme="gray",
                ),
                rx.code_block(
                    "docker run -p 80:80 -e "
                    "acceptLicense=true -e saveAnalytics=true whoicd/icd-api",
                    language="bash",
                    width="100%",
                ),
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
    )


def servers_page() -> rx.Component:
    """The servers and auth page.

    Returns:
        The page component.
    """
    return page(
        "Servers & auth",
        "ECT talks to an ICD-API server: WHO's cloud API with OAUTH 2.0, "
        "WHO's developer test server, or your own deployment.",
        presets(),
        rx.cond(
            Settings.api_server_url.contains(WHO_CLOUD_API),
            token_card(),
            rx.callout(
                "This server needs no token. Switch to the WHO cloud API to "
                "exercise the OAUTH 2.0 flow.",
                icon="info",
                size="1",
                width="100%",
            ),
        ),
        section(
            "Check it works",
            "A small Coding Tool bound to the settings above.",
            icd11ect.coding_tool(
                ino=INO,
                simplified_mode=True,
                placeholder="type to check the server answers...",
                input_props={
                    "width": "100%",
                    "padding": "0.6em 0.8em",
                    "border_radius": "0.4em",
                    "border": f"1px solid {rx.color('gray', 7)}",
                },
                window_props={"width": "100%", "margin_top": "0.4em"},
                on_select=CodingState.on_select,
                **ect_common_props(height="36vh"),
            ),
            rx.cond(
                CodingState.has_selection,
                rx.hstack(
                    rx.badge(CodingState.selected_code, variant="solid"),
                    rx.text(CodingState.selected_title, size="2"),
                    align="center",
                    spacing="2",
                ),
                rx.fragment(),
            ),
            width="100%",
        ),
        flows(),
    )
