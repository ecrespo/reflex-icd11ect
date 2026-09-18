"""Reflex components for the WHO ICD-11 Embedded Classification Tools.

Three kinds of component live here:

``Icd11ectController``
    The lifecycle component. It renders no markup of its own: it configures
    ECT, registers the instance and binds it. Use it directly when you lay the
    search box and the result window out yourself, or as a page wide provider.

``Icd11ectCodingTool`` / ``Icd11ectBrowser``
    Controllers that also render the markup ECT looks for, so a single call is
    enough to get a working Coding Tool or Embedded Browser.

``search_input`` / ``result_window`` / ``browser_window``
    The bare DOM elements, for custom layouts. They only carry the classes and
    the ``data-ctw-ino`` attribute ECT binds to.

Every instance is identified by ``ino`` (ECT's ``data-ctw-ino``). It must be
unique on the page, and the elements of one instance must share it.
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal

import reflex as rx
from reflex.constants import Hooks
from reflex.event import EventChain, no_args_event_spec
from reflex.utils.format import format_prop, wrap
from reflex.utils.imports import ImportVar
from reflex.vars.base import Var, VarData

from reflex_icd11ect._runtime import ICD11ECT_RUNTIME_JS
from reflex_icd11ect.constants import (
    ALL_SETTINGS,
    ECT_PACKAGE,
    ECT_STYLESHEET,
    ECT_VERSION,
)
from reflex_icd11ect.types import browser_content_spec, selected_entity_spec

# Props that configure the bridge itself rather than ECT.
_OPTION_PROPS: tuple[str, ...] = (
    "token",
    "token_endpoint",
    "token_field",
    "token_timeout_ms",
)

_EVENT_PROPS: tuple[str, ...] = (
    "on_select",
    "on_search_start",
    "on_search_end",
    "on_browser_load",
    "on_browser_change",
    "on_token_request",
)

# Reflex event trigger -> key read by the JavaScript runtime.
_CALLBACK_NAMES: dict[str, str] = {
    "on_select": "onSelect",
    "on_search_start": "onSearchStart",
    "on_search_end": "onSearchEnd",
    "on_browser_load": "onBrowserLoad",
    "on_browser_change": "onBrowserChange",
    "on_token_request": "onTokenRequest",  # nosec B105 - a callback name.
}


def _merge_class_name(fixed: str, given: Any) -> Any:
    """Keep the class ECT binds to while honouring a user supplied one.

    Args:
        fixed: The class name ECT requires.
        given: The class name passed by the caller, if any.

    Returns:
        The class name to render.

    """
    if given is None:
        return fixed
    if isinstance(given, (list, tuple)):
        return [fixed, *given]
    if isinstance(given, str):
        return f"{fixed} {given}"
    return [fixed, given]


def search_input(ino: str | rx.Var[str] = "1", **props: Any) -> rx.Component:
    """Render the text input ECT attaches its search to.

    The input must stay uncontrolled: ECT writes into its value and toggles
    ``disabled`` while it loads, so do not bind ``value`` to your state.

    Args:
        ino: Identifier of the instance, ECT's ``data-ctw-ino``.
        **props: Extra props forwarded to the underlying ``input``.

    Returns:
        The search input element.

    """
    custom_attrs = {"data-ctw-ino": ino, **props.pop("custom_attrs", {})}
    props.setdefault("auto_complete", "off")
    props.setdefault("type", "text")
    return rx.el.input(
        class_name=_merge_class_name("ctw-input", props.pop("class_name", None)),
        custom_attrs=custom_attrs,
        **props,
    )


def result_window(ino: str | rx.Var[str] = "1", **props: Any) -> rx.Component:
    """Render the container the Coding Tool draws its results into.

    Args:
        ino: Identifier of the instance, ECT's ``data-ctw-ino``.
        **props: Extra props forwarded to the underlying ``div``.

    Returns:
        The result window element.

    """
    custom_attrs = {"data-ctw-ino": ino, **props.pop("custom_attrs", {})}
    return rx.el.div(
        class_name=_merge_class_name("ctw-window", props.pop("class_name", None)),
        custom_attrs=custom_attrs,
        **props,
    )


def browser_window(ino: str | rx.Var[str] = "1", **props: Any) -> rx.Component:
    """Render the container the Embedded Browser draws itself into.

    Args:
        ino: Identifier of the instance, ECT's ``data-ctw-ino``.
        **props: Extra props forwarded to the underlying ``div``.

    Returns:
        The embedded browser element.

    """
    custom_attrs = {"data-ctw-ino": ino, **props.pop("custom_attrs", {})}
    return rx.el.div(
        class_name=_merge_class_name("ctw-eb-window", props.pop("class_name", None)),
        custom_attrs=custom_attrs,
        **props,
    )


class Icd11ectController(rx.Fragment):
    """Configures ECT and binds one Coding Tool / Embedded Browser instance.

    It renders nothing by itself. Pair it with :func:`search_input` and
    :func:`result_window` (or :func:`browser_window`) that carry the same
    ``ino``, or use it with no elements at all as a page wide provider that
    holds the shared settings and the OAUTH 2.0 token.
    """

    # Settings this class contributes, python name -> ECT name.
    _ECT_SETTINGS = ALL_SETTINGS

    # --- identity ---------------------------------------------------------

    #: Instance identifier, rendered as ``data-ctw-ino``. Unique per page.
    ino: rx.Var[str] = Var.create("1")

    # --- required settings -------------------------------------------------

    #: URL of the ICD-API server, e.g. ``https://id.who.int`` for the WHO
    #: cloud or ``http://localhost`` for a local deployment. Required, unless
    #: another instance on the page already provides it.
    api_server_url: rx.Var[str]

    #: Whether the server requires an OAUTH 2.0 bearer token. ``True`` for
    #: the WHO cloud API, ``False`` for a local deployment.
    api_secured: rx.Var[bool]

    # --- classification ----------------------------------------------------

    #: Classification to use: ``"mms"`` (ICD-11 MMS), ``"icf"`` (ECT >= 1.7)
    #: or ``"foundation"`` (Embedded Browser only). Defaults to ``"mms"``.
    source: rx.Var[Literal["mms", "icf", "foundation"]]

    #: Release to use, e.g. ``"2025-01"``. Defaults to the latest release
    #: the server reports.
    minor_version: rx.Var[str]

    #: ISO 639-1 language code of the content and of the interface.
    language: rx.Var[str]

    #: Name of your application, reported to WHO's usage analytics.
    source_app: rx.Var[str]

    # --- shared appearance -------------------------------------------------

    #: Maximum height of the tool, in CSS ``px`` or ``vh`` units.
    height: rx.Var[str]

    #: Title shown above the hierarchy panel.
    hierarchy_title: rx.Var[str]

    #: Whether the hierarchy panel can be resized with the mouse (ECT >= 1.7).
    hierarchy_resizable: rx.Var[bool]

    #: Whether the extended postcoordination options are offered (ECT >= 1.7).
    other_postcoordination: rx.Var[bool]

    #: Whether keyboard navigation is enabled. Always off on mobile.
    enable_keyboard: rx.Var[bool]

    #: Whether diagnostic requirements are included in the content
    #: (ECT >= 1.7).
    include_diagnostic_criteria: rx.Var[bool]

    #: Whether ECT logs what it does to the browser console.
    verbose: rx.Var[bool]

    # --- Embedded Coding Tool ----------------------------------------------

    #: Whether the results are shown as a dropdown below the search box
    #: instead of a block in the page flow.
    popup_mode: rx.Var[bool]

    #: Whether to show a stripped down output with codes and titles only.
    #: Implies ``disable_hierarchy`` and turns the word list, the chapter
    #: filter and flexisearch off.
    simplified_mode: rx.Var[bool]

    #: Whether to hide the ICD-11 hierarchy browser.
    disable_hierarchy: rx.Var[bool]

    #: Whether the list of related words is shown.
    words_available: rx.Var[bool]

    #: Whether the chapter filter is offered to the user (MMS only).
    chapters_available: rx.Var[bool]

    #: Chapters the search is limited to, semicolon separated, e.g.
    #: ``"01;02;21"``. See :data:`~reflex_icd11ect.constants.MMS_CHAPTERS`.
    chapters_filter: rx.Var[str]

    #: Foundation URIs the search is limited to, comma separated.
    subtrees_filter: rx.Var[str]

    #: Whether the flexible search is used when the strict search finds
    #: nothing.
    flexisearch_available: rx.Var[bool]

    #: Whether typing a code or a URI searches for that entity.
    search_by_code_or_uri: rx.Var[bool]

    #: Medical coding mode. Undocumented ECT setting, use with care.
    medical_coding_mode: rx.Var[bool]

    #: Show the URI of the selection instead of its code. Undocumented ECT
    #: setting, use with care.
    view_selected_uri: rx.Var[bool]

    # --- Embedded Browser --------------------------------------------------

    #: Which entities get a select button: ``"none"`` (the ECT default),
    #: ``"categories"``, ``"all"`` or ``"allButRoot"``.
    enable_select_button: rx.Var[Literal["none", "categories", "all", "allButRoot"]]

    #: Whether the browser shows its own search box.
    browser_search_available: rx.Var[bool]

    #: Whether the advanced search is offered (ECT >= 1.7).
    browser_advanced_search_available: rx.Var[bool]

    #: Whether the hierarchy panel is shown (ECT >= 1.7).
    browser_hierarchy_available: rx.Var[bool]

    #: Foundation URIs the hierarchy is restricted to.
    browser_hierarchy_root_uris: rx.Var[list[str]]

    #: URI of the entity shown when the browser loads.
    browser_uri: rx.Var[str]

    #: Whether children that are not part of the linearization are listed.
    display_other_foundation_children: rx.Var[bool]

    # --- token handling ----------------------------------------------------

    #: A valid OAUTH 2.0 bearer token (a JWT). Required when
    #: ``api_secured=True`` unless ``token_endpoint`` is set. Keep it in your
    #: state and refresh it from ``on_token_request``.
    token: rx.Var[str]

    #: URL the browser fetches a token from, the pattern WHO documents. The
    #: response must be JSON; see ``token_field``.
    token_endpoint: rx.Var[str]

    #: Key of the JSON field holding the token in ``token_endpoint``'s
    #: response. Defaults to ``"token"``, falling back to ``"access_token"``.
    token_field: rx.Var[str]

    #: How long to wait, in milliseconds, for the backend to answer
    #: ``on_token_request`` before giving up. Defaults to 15000.
    token_timeout_ms: rx.Var[int]

    # --- events -----------------------------------------------------------

    #: Fired when the user picks an entity. The handler receives the selected
    #: entity as a mapping; see :class:`~reflex_icd11ect.types.SelectedEntity`.
    on_select: rx.EventHandler[selected_entity_spec]

    #: Fired when a search starts.
    on_search_start: rx.EventHandler[no_args_event_spec]

    #: Fired when a search ends, successfully or not.
    on_search_end: rx.EventHandler[no_args_event_spec]

    #: Fired once, when the Embedded Browser has finished loading.
    on_browser_load: rx.EventHandler[no_args_event_spec]

    #: Fired whenever the Embedded Browser displays another entity. The
    #: handler receives a mapping; see
    #: :class:`~reflex_icd11ect.types.BrowserContent`.
    on_browser_change: rx.EventHandler[browser_content_spec]

    #: Fired when ECT needs a fresh token, i.e. the previous one expired.
    #: Answer it by setting ``token`` to a new value.
    on_token_request: rx.EventHandler[no_args_event_spec]

    # --- wiring -----------------------------------------------------------

    #: Value of the ``kind`` field reported to the runtime, for debugging.
    _ect_kind: ClassVar[str] = "controller"

    @classmethod
    def _ect_settings(cls) -> dict[str, str]:
        """Collect the setting map of this class and of its bases.

        Returns:
            The python name -> ECT name mapping for this component.

        """
        settings: dict[str, str] = {}
        for klass in reversed(cls.__mro__):
            settings.update(getattr(klass, "_ECT_SETTINGS", None) or {})
        return settings

    def add_imports(self) -> dict[str, Any]:
        """Import ECT and its stylesheet.

        Returns:
            The imports needed by the runtime.

        """
        return {
            f"{ECT_PACKAGE}@{ECT_VERSION}": ImportVar(
                tag="*", alias="ECT", is_default=True
            ),
            "": ECT_STYLESHEET,
        }

    def add_custom_code(self) -> list[str]:
        """Emit the bridge runtime once per page.

        Returns:
            The JavaScript runtime.

        """
        return [ICD11ECT_RUNTIME_JS]

    def _exclude_props(self) -> list[str]:
        return [
            *super()._exclude_props(),
            "ino",
            *self._ect_settings(),
            *_OPTION_PROPS,
            *_EVENT_PROPS,
        ]

    def _ect_settings_js(self) -> str:
        """Build the ECT settings object for this instance.

        Only props the caller actually set are included, so ECT keeps its own
        defaults and a provider's settings are not overwritten with ``None``.

        Returns:
            A JavaScript object literal.

        """
        entries = []
        for python_name, ect_name in self._ect_settings().items():
            value = getattr(self, python_name, None)
            if value is None:
                continue
            entries.append(f"{ect_name}: {value!s}")
        return "{" + ", ".join(entries) + "}"

    def _ect_callbacks_js(self) -> str:
        """Build the callbacks object for this instance.

        Returns:
            A JavaScript object literal of arrow functions.

        """
        entries = []
        for trigger, js_name in _CALLBACK_NAMES.items():
            chain = self.event_triggers.get(trigger)
            if chain is None:
                continue
            if isinstance(chain, EventChain):
                chain = wrap(str(format_prop(chain)).strip("{}"), "(")
            entries.append(f"{js_name}: {chain!s}")
        return "{" + ", ".join(entries) + "}"

    def _ect_options_js(self) -> str:
        """Build the runtime options object for this instance.

        Returns:
            A JavaScript object literal.

        """
        entries = [f'kind: "{self._ect_kind}"']
        for python_name, js_name in (
            ("token", "token"),
            ("token_endpoint", "tokenEndpoint"),
            ("token_field", "tokenField"),
            ("token_timeout_ms", "tokenTimeoutMs"),
            ("verbose", "verbose"),
        ):
            value = getattr(self, python_name, None)
            if value is None:
                continue
            entries.append(f"{js_name}: {value!s}")
        return "{" + ", ".join(entries) + "}"

    def add_hooks(self) -> list[str | Var[str]]:
        """Register the instance with the runtime after the DOM is committed.

        Returns:
            The hooks to add to the component.

        """
        call = (
            f"useIcd11ect({self.ino!s}, {self._ect_settings_js()}, "
            f"{self._ect_callbacks_js()}, {self._ect_options_js()})"
        )
        return [
            Var(
                call,
                _var_type=str,
                _var_data=VarData(
                    imports={"react": ["useEffect", "useRef"]},
                    position=Hooks.HookPosition.POST_TRIGGER,
                ),
            ),
        ]


class Icd11ectCodingTool(Icd11ectController):
    """The ICD-11 Embedded Coding Tool: a search box plus a result window.

    ``on_select`` fires with the entity the user picks. The search box is
    uncontrolled by design, ECT owns its value.

    It accepts every ECT setting, including the Embedded Browser ones: ECT
    keeps a single configuration per page, so those still take effect there.
    """

    _ect_kind: ClassVar[str] = "codingTool"

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        """Create a Coding Tool.

        Args:
            *children: Extra children rendered after the result window.
            **props: The props of the component. ``placeholder`` and
                ``input_props`` configure the search box, ``window_props``
                the result window.

        Returns:
            The Coding Tool component.

        """
        ino = props.get("ino", "1")
        input_props: dict[str, Any] = dict(props.pop("input_props", {}) or {})
        window_props: dict[str, Any] = dict(props.pop("window_props", {}) or {})
        placeholder = props.pop("placeholder", None)
        if placeholder is not None:
            input_props.setdefault("placeholder", placeholder)
        return super().create(
            search_input(ino, **input_props),
            result_window(ino, **window_props),
            *children,
            **props,
        )


class Icd11ectBrowser(Icd11ectController):
    """The ICD-11 Embedded Browser.

    Set ``enable_select_button`` to let the user pick an entity; it is set to
    ``"all"`` for you when you pass ``on_select`` and leave it unset, because
    ECT ships no select button by default.

    It accepts every ECT setting, including the Coding Tool ones: ECT keeps a
    single configuration per page, so those still take effect there.
    """

    _ect_kind: ClassVar[str] = "browser"

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        """Create an Embedded Browser.

        Args:
            *children: Extra children rendered after the browser window.
            **props: The props of the component. ``window_props`` is
                forwarded to the browser container.

        Returns:
            The Embedded Browser component.

        """
        ino = props.get("ino", "1")
        window_props: dict[str, Any] = dict(props.pop("window_props", {}) or {})
        if "on_select" in props and "enable_select_button" not in props:
            props["enable_select_button"] = "all"
        return super().create(
            browser_window(ino, **window_props),
            *children,
            **props,
        )


# Ergonomic factories.
icd11ect_controller = Icd11ectController.create
icd11ect_provider = Icd11ectController.create
icd11ect_coding_tool = Icd11ectCodingTool.create
icd11ect_browser = Icd11ectBrowser.create

__all__ = [
    "ALL_SETTINGS",
    "Icd11ectBrowser",
    "Icd11ectCodingTool",
    "Icd11ectController",
    "browser_window",
    "icd11ect_browser",
    "icd11ect_coding_tool",
    "icd11ect_controller",
    "icd11ect_provider",
    "result_window",
    "search_input",
]
