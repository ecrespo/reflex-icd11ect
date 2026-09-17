"""Reflex custom component for the WHO ICD-11 Embedded Classification Tools.

Wraps `@whoicd/icd11ect <https://www.npmjs.com/package/@whoicd/icd11ect>`_,
the WHO's Embedded Coding Tool and Embedded Browser, powered by the ICD-API.

Quick start::

    import reflex as rx
    from reflex_icd11ect import icd11ect

    class State(rx.State):
        code: str = ""

        @rx.event
        def on_select(self, entity: dict[str, str]):
            self.code = entity["code"]

    def index():
        return rx.vstack(
            rx.text(State.code),
            icd11ect.coding_tool(
                api_server_url="https://id.who.int",
                api_secured=True,
                token=State.token,
                on_select=State.on_select,
            ),
        )
"""

from reflex_icd11ect import constants, handler, token
from reflex_icd11ect.constants import (
    ALL_SETTINGS,
    BROWSER_SETTINGS,
    CODING_TOOL_SETTINGS,
    COMMON_SETTINGS,
    ECT_PACKAGE,
    ECT_STYLESHEET,
    ECT_VERSION,
    ICD_TOKEN_ENDPOINT,
    ICD_TOKEN_SCOPE,
    LANGUAGES,
    MMS_CHAPTERS,
    OVERWRITABLE_SETTINGS,
    RTL_LANGUAGES,
    SELECT_BUTTON_MODES,
    SOURCES,
    WHO_CLOUD_API,
    WHO_DEVELOPER_TEST_API,
)
from reflex_icd11ect.icd11ect import (
    Icd11ectBrowser,
    Icd11ectCodingTool,
    Icd11ectController,
    browser_window,
    icd11ect_browser,
    icd11ect_coding_tool,
    icd11ect_controller,
    icd11ect_provider,
    result_window,
    search_input,
)
from reflex_icd11ect.namespace import icd11ect
from reflex_icd11ect.token import IcdTokenError, IcdTokenProvider
from reflex_icd11ect.types import BrowserContent, SelectedEntity

__version__ = "0.1.0"

__all__ = [
    "ALL_SETTINGS",
    "BROWSER_SETTINGS",
    "CODING_TOOL_SETTINGS",
    "COMMON_SETTINGS",
    "ECT_PACKAGE",
    "ECT_STYLESHEET",
    "ECT_VERSION",
    "ICD_TOKEN_ENDPOINT",
    "ICD_TOKEN_SCOPE",
    "LANGUAGES",
    "MMS_CHAPTERS",
    "OVERWRITABLE_SETTINGS",
    "RTL_LANGUAGES",
    "SELECT_BUTTON_MODES",
    "SOURCES",
    "WHO_CLOUD_API",
    "WHO_DEVELOPER_TEST_API",
    "BrowserContent",
    "Icd11ectBrowser",
    "Icd11ectCodingTool",
    "Icd11ectController",
    "IcdTokenError",
    "IcdTokenProvider",
    "SelectedEntity",
    "__version__",
    "browser_window",
    "constants",
    "handler",
    "icd11ect",
    "icd11ect_browser",
    "icd11ect_coding_tool",
    "icd11ect_controller",
    "icd11ect_provider",
    "result_window",
    "search_input",
    "token",
]
