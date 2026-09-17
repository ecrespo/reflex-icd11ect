"""The ``icd11ect`` namespace, mirroring how Reflex groups related components."""

from __future__ import annotations

import reflex as rx

from reflex_icd11ect import handler as _handler
from reflex_icd11ect.icd11ect import (
    Icd11ectBrowser,
    Icd11ectCodingTool,
    Icd11ectController,
    browser_window,
    result_window,
    search_input,
)


class Icd11ectNamespace(rx.ComponentNamespace):
    """The ICD-11 Embedded Classification Tools.

    Calling the namespace creates a Coding Tool::

        icd11ect(api_server_url=..., on_select=State.on_select)
        icd11ect.browser(api_server_url=..., ino="2")
    """

    #: The lifecycle component, for custom layouts and page wide settings.
    controller = staticmethod(Icd11ectController.create)
    #: Alias of :attr:`controller`, for use as a page wide provider.
    provider = staticmethod(Icd11ectController.create)
    #: The Embedded Coding Tool: search box plus results.
    coding_tool = staticmethod(Icd11ectCodingTool.create)
    #: The Embedded Browser.
    browser = staticmethod(Icd11ectBrowser.create)
    #: The bare search box element.
    search_input = staticmethod(search_input)
    #: The bare Coding Tool result container.
    result_window = staticmethod(result_window)
    #: The bare Embedded Browser container.
    browser_window = staticmethod(browser_window)
    #: The imperative ``ECT.Handler`` API.
    handler = _handler

    __call__ = staticmethod(Icd11ectCodingTool.create)


icd11ect = Icd11ectNamespace()

__all__ = ["Icd11ectNamespace", "icd11ect"]
