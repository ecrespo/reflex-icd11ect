"""Event payloads and event specs for the ICD-11 ECT components.

ECT hands its callbacks JavaScript objects with camelCase keys. The event
specs below rewrite them into snake_case objects on the frontend, so the
Reflex event handler receives an idiomatic Python mapping.

Annotate the handler argument as ``dict[str, str]`` and, if you want
attribute access, wrap it::

    @rx.event
    def on_select(self, entity: dict[str, str]):
        selected = SelectedEntity.from_payload(entity)
        self.code = selected.code
"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import Any, Final

import reflex as rx

# python name -> ECT (JavaScript) name for the ``selectedEntity`` object.
SELECTED_ENTITY_FIELDS: Final[tuple[tuple[str, str], ...]] = (
    ("i_no", "iNo"),
    ("code", "code"),
    ("title", "title"),
    ("uri", "uri"),
    ("linearization_uri", "linearizationUri"),
    ("foundation_uri", "foundationUri"),
    ("selected_text", "selectedText"),
    ("best_match_text", "bestMatchText"),
    ("search_query", "searchQuery"),
)

# python name -> ECT (JavaScript) name for the ``browserContent`` object.
BROWSER_CONTENT_FIELDS: Final[tuple[tuple[str, str], ...]] = (
    ("i_no", "iNo"),
    ("code", "code"),
    ("uri", "uri"),
)


@dataclasses.dataclass(frozen=True)
class SelectedEntity:
    """An entity the user picked in the Coding Tool or the Embedded Browser.

    Mirrors the ``selectedEntity`` object of ECT. ``code`` and ``uri`` carry
    the whole postcoordinated expression when the user built one, e.g.
    ``2C25.Z&XA2UD3``.
    """

    #: Identifier of the component instance (the ``data-ctw-ino`` value).
    i_no: str = ""
    #: The classification code, empty for Foundation entities.
    code: str = ""
    #: Title of the selected entity.
    title: str = ""
    #: URI of the selection; the linearization or the foundation URI
    #: depending on the ``source`` in use.
    uri: str = ""
    #: URI of the entity in the linearization (MMS, ICF, ...).
    linearization_uri: str = ""
    #: URI of the entity in the ICD-11 Foundation.
    foundation_uri: str = ""
    #: The exact text the user clicked on (index term, matching term, ...).
    selected_text: str = ""
    #: Deprecated by WHO; kept because ECT still sends it.
    best_match_text: str = ""
    #: What the user typed in the search box (Coding Tool only).
    search_query: str = ""

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> SelectedEntity:
        """Build a SelectedEntity from a raw event payload.

        Args:
            payload: The mapping received by the event handler.

        Returns:
            The parsed selected entity; unknown keys are ignored.

        """
        payload = payload or {}
        known = {field.name for field in dataclasses.fields(cls)}
        return cls(
            **{
                key: "" if value is None else str(value)
                for key, value in payload.items()
                if key in known
            }
        )

    @property
    def is_postcoordinated(self) -> bool:
        """Whether the selection is a postcoordinated expression.

        Returns:
            True when the code or the URI combines several entities.

        """
        return "&" in self.code or "&" in self.uri


@dataclasses.dataclass(frozen=True)
class BrowserContent:
    """What the Embedded Browser is currently displaying."""

    #: Identifier of the browser instance.
    i_no: str = ""
    #: Code of the displayed entity (postcoordinated expressions included).
    code: str = ""
    #: URI of the displayed entity.
    uri: str = ""

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> BrowserContent:
        """Build a BrowserContent from a raw event payload.

        Args:
            payload: The mapping received by the event handler.

        Returns:
            The parsed browser content; unknown keys are ignored.

        """
        payload = payload or {}
        known = {field.name for field in dataclasses.fields(cls)}
        return cls(
            **{
                key: "" if value is None else str(value)
                for key, value in payload.items()
                if key in known
            }
        )


def _rename_spec(
    fields: tuple[tuple[str, str], ...],
) -> Any:
    """Build an event spec that renames the keys of a JavaScript object.

    Args:
        fields: Pairs of (python name, JavaScript name).

    Returns:
        An event spec usable with ``rx.EventHandler``.

    """

    def spec(payload: rx.Var[dict[str, str]]) -> tuple[rx.Var[dict[str, str]]]:
        source = str(payload)
        entries = ", ".join(f"{py}: {source}?.{js}" for py, js in fields)
        return (rx.Var("({" + entries + "})").to(dict[str, str]),)

    return spec


#: Event spec for ``selectedEntityFunction``.
selected_entity_spec = _rename_spec(SELECTED_ENTITY_FIELDS)

#: Event spec for ``browserChangedFunction``.
browser_content_spec = _rename_spec(BROWSER_CONTENT_FIELDS)
