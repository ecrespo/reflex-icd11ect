"""Configuration of the reflex-icd11ect demo app."""

import reflex as rx
from reflex.plugins import RadixThemesPlugin, SitemapPlugin

config = rx.Config(
    app_name="icd11ect_demo",
    show_built_with_reflex=False,
    # Reads the ICD-API credentials from `.env`; see `.env.example`. A missing
    # file is a no-op, which is why the demo still starts with no credentials
    # at all against WHO's developer test server.
    env_file=".env",
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
