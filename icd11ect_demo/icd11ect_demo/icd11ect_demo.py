"""The reflex-icd11ect demo app."""

from __future__ import annotations

import reflex as rx

from icd11ect_demo.pages import (
    api_page,
    browser_page,
    coding_tool_page,
    custom_page,
    multi_page,
    servers_page,
)

# The theme lives in `rxconfig.py`, on `RadixThemesPlugin`: `App(theme=...)`
# is deprecated since Reflex 0.9 and goes away in 1.0.
app = rx.App(
    style={"font_family": "Inter, ui-sans-serif, system-ui, sans-serif"},
)

app.add_page(coding_tool_page, route="/", title="ICD-11 Coding Tool | reflex-icd11ect")
app.add_page(browser_page, route="/browser", title="ICD-11 Browser | reflex-icd11ect")
app.add_page(multi_page, route="/multi", title="Many instances | reflex-icd11ect")
app.add_page(custom_page, route="/custom", title="Custom layout | reflex-icd11ect")
app.add_page(servers_page, route="/servers", title="Servers & auth | reflex-icd11ect")
app.add_page(api_page, route="/api", title="API reference | reflex-icd11ect")
