"""State shared by the demo pages."""

from __future__ import annotations

import reflex as rx
from reflex_icd11ect import (
    WHO_CLOUD_API,
    WHO_DEVELOPER_TEST_API,
    IcdTokenError,
    IcdTokenProvider,
    SelectedEntity,
    handler,
)

#: Presets offered on the "Servers & auth" page.
SERVER_PRESETS: dict[str, str] = {
    "WHO developer test server (no auth)": WHO_DEVELOPER_TEST_API,
    "WHO cloud API (OAUTH 2.0)": WHO_CLOUD_API,
    "Local deployment (http://localhost)": "http://localhost",
}

#: Searches offered as one click examples.
EXAMPLE_SEARCHES: tuple[str, ...] = (
    "fever",
    "diabetes mellitus",
    "bipolar",
    "fracture of femur",
    "malaria",
)


class Settings(rx.State):
    """The ECT settings the demo drives from the UI."""

    # --- server ---
    api_server_url: str = WHO_DEVELOPER_TEST_API
    api_secured: bool = False
    minor_version: str = ""

    # --- classification ---
    language: str = "en"
    source: str = "mms"

    # --- coding tool ---
    popup_mode: bool = False
    simplified_mode: bool = False
    disable_hierarchy: bool = False
    words_available: bool = True
    chapters_available: bool = True
    flexisearch_available: bool = True
    search_by_code_or_uri: bool = False
    chapters_filter: str = ""
    height: str = "60vh"

    # --- shared ---
    include_diagnostic_criteria: bool = False
    other_postcoordination: bool = True
    hierarchy_resizable: bool = True
    verbose: bool = False

    # --- browser ---
    enable_select_button: str = "all"
    browser_search_available: bool = True
    browser_advanced_search_available: bool = True
    browser_hierarchy_available: bool = True
    browser_uri: str = ""

    @rx.event
    def set_api_server_url(self, value: str):
        """Point every instance at another ICD-API server."""
        self.api_server_url = value
        self.api_secured = value.rstrip("/") == WHO_CLOUD_API

    @rx.event
    def set_api_secured(self, value: bool):
        """Turn OAUTH 2.0 on or off."""
        self.api_secured = value

    @rx.event
    def set_language(self, value: str):
        """Change the content and interface language."""
        self.language = value

    @rx.event
    def set_source(self, value: str):
        """Switch between MMS, ICF and the Foundation."""
        self.source = value

    @rx.event
    def set_minor_version(self, value: str):
        """Pin a release, e.g. 2025-01."""
        self.minor_version = value

    @rx.event
    def set_chapters_filter(self, value: str):
        """Limit the search to some MMS chapters."""
        self.chapters_filter = value

    @rx.event
    def toggle_chapter(self, chapter: str):
        """Add or remove one chapter from the filter."""
        chapters = [c for c in self.chapters_filter.split(";") if c]
        if chapter in chapters:
            chapters.remove(chapter)
        else:
            chapters.append(chapter)
        self.chapters_filter = ";".join(chapters)

    @rx.event
    def set_height(self, value: str):
        """Change the maximum height of the tools."""
        self.height = value

    @rx.event
    def set_browser_uri(self, value: str):
        """Change the entity the browser opens on."""
        self.browser_uri = value

    @rx.event
    def set_enable_select_button(self, value: str):
        """Choose which entities get a select button in the browser."""
        self.enable_select_button = value

    @rx.event
    def toggle(self, field: str):
        """Flip one of the boolean settings.

        Args:
            field: Name of the boolean setting.
        """
        current = getattr(self, field, None)
        if isinstance(current, bool):
            setattr(self, field, not current)


class CodingState(rx.State):
    """Selections and search activity of the Coding Tool pages."""

    #: The last entity the user picked, as the raw payload.
    selected: dict[str, str] = {}
    #: Every selection of the session, newest first.
    history: list[dict[str, str]] = []
    #: Whether a search is running.
    searching: bool = False
    #: Free text typed in the "search programmatically" box.
    query: str = ""
    #: Selections of the multi instance page, by instance.
    per_instance: dict[str, str] = {}

    @rx.event
    def on_select(self, entity: dict[str, str]):
        """Record the entity the user picked."""
        self.selected = entity
        self.history = [entity, *self.history][:25]

    @rx.event
    def on_select_instance(self, entity: dict[str, str]):
        """Record a selection on the multi instance page."""
        parsed = SelectedEntity.from_payload(entity)
        self.per_instance[parsed.i_no] = f"{parsed.code} - {parsed.title}"

    @rx.event
    def search_started(self):
        """Show the search indicator."""
        self.searching = True

    @rx.event
    def search_ended(self):
        """Hide the search indicator."""
        self.searching = False

    @rx.event
    def set_query(self, value: str):
        """Keep what was typed in the programmatic search box."""
        self.query = value

    @rx.event
    def run_query(self, ino: str = "1"):
        """Search for whatever is in the programmatic search box."""
        return handler.search(ino, self.query)

    @rx.event
    def search_example(self, query: str, ino: str = "1"):
        """Search for one of the example queries."""
        self.query = query
        return handler.search(ino, query)

    @rx.event
    def clear_all(self, ino: str = "1"):
        """Clear the tool and the recorded selection."""
        self.selected = {}
        return handler.clear(ino)

    @rx.event
    def clear_history(self):
        """Forget the recorded selections."""
        self.history = []

    @rx.var
    def has_selection(self) -> bool:
        """Whether something was selected."""
        return bool(self.selected)

    @rx.var
    def selected_code(self) -> str:
        """Code of the last selection."""
        return SelectedEntity.from_payload(self.selected).code

    @rx.var
    def selected_title(self) -> str:
        """Title of the last selection."""
        return SelectedEntity.from_payload(self.selected).title

    @rx.var
    def selected_text(self) -> str:
        """The exact text the user clicked on."""
        return SelectedEntity.from_payload(self.selected).selected_text

    @rx.var
    def selected_query(self) -> str:
        """The query that led to the last selection."""
        return SelectedEntity.from_payload(self.selected).search_query

    @rx.var
    def selected_linearization_uri(self) -> str:
        """Linearization URI of the last selection."""
        return SelectedEntity.from_payload(self.selected).linearization_uri

    @rx.var
    def selected_foundation_uri(self) -> str:
        """Foundation URI of the last selection."""
        return SelectedEntity.from_payload(self.selected).foundation_uri

    @rx.var
    def selected_is_postcoordinated(self) -> bool:
        """Whether the last selection is a postcoordinated expression."""
        return SelectedEntity.from_payload(self.selected).is_postcoordinated


class BrowserState(rx.State):
    """What the Embedded Browser is showing."""

    #: Set once the browser has loaded.
    loaded: bool = False
    #: Code of the entity currently displayed.
    code: str = ""
    #: URI of the entity currently displayed.
    uri: str = ""
    #: Entity picked with the select button.
    picked: str = ""
    #: What to type in the "go to" boxes.
    goto_code: str = "1B11"
    goto_uri: str = ""
    #: Every change of content, newest first.
    trail: list[str] = []

    @rx.event
    def on_load(self):
        """The browser finished loading."""
        self.loaded = True

    @rx.event
    def on_change(self, content: dict[str, str]):
        """The browser is showing something else."""
        self.code = content.get("code") or ""
        self.uri = content.get("uri") or ""
        label = self.code or self.uri
        if label:
            self.trail = [label, *self.trail][:15]

    @rx.event
    def on_select(self, entity: dict[str, str]):
        """The user pressed a select button."""
        parsed = SelectedEntity.from_payload(entity)
        self.picked = f"{parsed.code or parsed.foundation_uri} - {parsed.title}"

    @rx.event
    def set_goto_code(self, value: str):
        """Keep what was typed in the "go to code" box."""
        self.goto_code = value

    @rx.event
    def set_goto_uri(self, value: str):
        """Keep what was typed in the "go to URI" box."""
        self.goto_uri = value

    @rx.event
    def go_to_code(self, ino: str = "browser"):
        """Show the entity with that code."""
        return handler.set_browser_code(ino, self.goto_code)

    @rx.event
    def go_to_uri(self, ino: str = "browser"):
        """Show the entity with that URI."""
        return handler.set_browser_uri(ino, self.goto_uri)


class AuthState(rx.State):
    """OAUTH 2.0 token handling for the WHO cloud API."""

    #: The current bearer token, handed to the component.
    token: str = ""
    #: Human readable status of the last token request.
    status: str = "No token requested yet."
    #: Whether the last token request failed.
    failed: bool = False
    #: How many times ECT asked for a fresh token.
    requests: int = 0

    @rx.event(background=True)
    async def refresh_token(self):
        """Fetch a token with the client credentials grant.

        Wired to ``on_token_request``, so ECT gets a new token whenever the
        previous one expires. The client secret never leaves the backend.
        """
        async with self:
            self.requests += 1
            self.status = "Requesting a token..."
            self.failed = False
        try:
            provider = IcdTokenProvider.from_env()
            token = await provider.async_token()
        except IcdTokenError as error:
            async with self:
                self.failed = True
                self.status = str(error)
            return
        async with self:
            self.token = token
            self.failed = False
            self.status = f"Token obtained, {len(token)} characters."

    @rx.event
    def forget_token(self):
        """Drop the token that is held in the state."""
        self.token = ""
        self.status = "Token dropped."


class UiState(rx.State):
    """Small bits of UI state."""

    #: Whether the settings drawer is open.
    settings_open: bool = True

    @rx.event
    def toggle_settings(self):
        """Show or hide the settings panel."""
        self.settings_open = not self.settings_open
