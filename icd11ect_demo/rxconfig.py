"""Configuration of the reflex-icd11ect demo app."""

import reflex as rx
from reflex.plugins import RadixThemesPlugin, SitemapPlugin

config = rx.Config(
    app_name="icd11ect_demo",
    show_built_with_reflex=False,
    plugins=[
        # Both are enabled by default; declaring them here is what Reflex
        # 0.9 asks for, and the theme belongs to the plugin since
        # `App(theme=...)` is deprecated.
        RadixThemesPlugin(
            theme=rx.theme(appearance="light", accent_color="teal", radius="medium"),
        ),
        SitemapPlugin(),
    ],
)
