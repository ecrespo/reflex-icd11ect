"""Imperative ECT API, callable from Reflex event handlers.

``ECT.Handler`` is imperative: it searches, clears and navigates by side
effect. Each function here returns an event you can return (or yield) from a
state handler::

    class State(rx.State):
        @rx.event
        def code_fever(self):
            return handler.search("1", "fever")

They are no-ops when no ICD-11 ECT component is mounted on the page.
"""

from __future__ import annotations

from typing import Any

import reflex as rx

from reflex_icd11ect.constants import ALL_SETTINGS

#: JavaScript expression for the page's runtime singleton.
RUNTIME = "window.__reflexIcd11ect"


def _js(value: Any) -> str:
    """Render a Python value or a Var as a JavaScript expression.

    Args:
        value: The value to render.

    Returns:
        The JavaScript source for that value.

    """
    return str(rx.Var.create(value))


def _handler_call(method: str, *args: Any) -> rx.event.EventSpec:
    """Call a method of ``ECT.Handler`` on the client.

    Args:
        method: Name of the ECT handler method.
        *args: Arguments passed to it.

    Returns:
        The event that performs the call.

    """
    rendered = ", ".join(_js(arg) for arg in args)
    # run_script compiles to a closure that the client evaluates when the event
    # fires, so the Vars interpolated above are read at that moment instead of
    # while the page renders.
    return rx.run_script(rx.Var(f"{RUNTIME}?.ECT?.Handler?.{method}({rendered})"))


def search(ino: str | rx.Var[str], query: str | rx.Var[str]) -> rx.event.EventSpec:
    """Run a search in a Coding Tool as if the user had typed it.

    Args:
        ino: Identifier of the Coding Tool instance.
        query: The text to search for.

    Returns:
        The event that runs the search.

    """
    return _handler_call("search", ino, query)


def clear(ino: str | rx.Var[str]) -> rx.event.EventSpec:
    """Clear the search box and the results of a Coding Tool.

    Args:
        ino: Identifier of the Coding Tool instance.

    Returns:
        The event that clears the tool.

    """
    return _handler_call("clear", ino)


def set_browser_uri(
    ino: str | rx.Var[str], uri: str | rx.Var[str]
) -> rx.event.EventSpec:
    """Show an entity in the Embedded Browser, by URI.

    Args:
        ino: Identifier of the Embedded Browser instance.
        uri: A single URI, or a postcoordinated expression such as
            ``"<uri1> & <uri2>"``.

    Returns:
        The event that navigates the browser.

    """
    return _handler_call("setBrowserUri", ino, uri)


def set_browser_code(
    ino: str | rx.Var[str], code: str | rx.Var[str]
) -> rx.event.EventSpec:
    """Show an entity in the Embedded Browser, by code.

    Args:
        ino: Identifier of the Embedded Browser instance.
        code: A code such as ``"1B11"``, or a postcoordinated expression such
            as ``"2C25.Z&XA2UD3"``.

    Returns:
        The event that navigates the browser.

    """
    return _handler_call("setBrowserCode", ino, code)


def change_source(
    ino: str | rx.Var[str], source: str | rx.Var[str]
) -> rx.event.EventSpec:
    """Switch an instance to another classification.

    Args:
        ino: Identifier of the instance.
        source: ``"mms"``, ``"icf"`` or ``"foundation"``.

    Returns:
        The event that switches the classification.

    """
    return _handler_call("changeSource", ino, source)


def change_minor_version(
    ino: str | rx.Var[str], minor_version: str | rx.Var[str]
) -> rx.event.EventSpec:
    """Switch an instance to another release.

    Args:
        ino: Identifier of the instance.
        minor_version: The release, e.g. ``"2025-01"``.

    Returns:
        The event that switches the release.

    """
    return _handler_call("changeMinorVersion", ino, minor_version)


def change_language(
    ino: str | rx.Var[str], language: str | rx.Var[str]
) -> rx.event.EventSpec:
    """Switch an instance to another language.

    Args:
        ino: Identifier of the instance.
        language: An ISO 639-1 code, e.g. ``"es"``.

    Returns:
        The event that switches the language.

    """
    return _handler_call("changeLanguage", ino, language)


def bind(ino: str | rx.Var[str]) -> rx.event.EventSpec:
    """Bind an instance again, e.g. after moving its elements in the DOM.

    Args:
        ino: Identifier of the instance.

    Returns:
        The event that binds the instance.

    """
    return _handler_call("bind", ino)


def overwrite_configuration(
    ino: str | rx.Var[str],
    settings: dict[str, Any],
    force: bool = True,
) -> rx.event.EventSpec:
    """Change the settings of one instance at runtime.

    Only part of ECT's settings can be overridden per instance; see
    :data:`~reflex_icd11ect.constants.OVERWRITABLE_SETTINGS`. Anything else has
    to be changed on the component's props, which reconfigures ECT.

    Args:
        ino: Identifier of the instance.
        settings: Settings by python name, e.g. ``{"language": "es"}``.
        force: Whether to refresh an already rendered instance.

    Returns:
        The event that applies the settings.

    Raises:
        ValueError: If a setting name is unknown.

    """
    translated: dict[str, Any] = {}
    for name, value in settings.items():
        ect_name = ALL_SETTINGS.get(
            name, name if name in ALL_SETTINGS.values() else None
        )
        if ect_name is None:
            msg = f"unknown ICD-11 ECT setting: {name!r}"
            raise ValueError(msg)
        translated[ect_name] = value
    return _handler_call("overwriteConfiguration", ino, translated, force)


def set_token(token: str | rx.Var[str]) -> rx.event.EventSpec:
    """Hand a fresh OAUTH 2.0 token to the runtime.

    Setting the ``token`` prop does this for you; use this when you want to
    push a token without re-rendering, e.g. from a background task.

    Args:
        token: The bearer token (a JWT).

    Returns:
        The event that stores the token.

    """
    return rx.run_script(rx.Var(f"{RUNTIME}?.setToken({_js(token)})"))


__all__ = [
    "bind",
    "change_language",
    "change_minor_version",
    "change_source",
    "clear",
    "overwrite_configuration",
    "search",
    "set_browser_code",
    "set_browser_uri",
    "set_token",
]
