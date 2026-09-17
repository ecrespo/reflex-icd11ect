"""Configuration of the reflex-icd11ect demo app."""

import reflex as rx
from reflex.plugins import SitemapPlugin

config = rx.Config(
    app_name="icd11ect_demo",
    show_built_with_reflex=False,
    plugins=[SitemapPlugin()],
)
