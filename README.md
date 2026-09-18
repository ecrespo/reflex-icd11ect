# reflex-icd11ect

[![tests](https://github.com/ecrespo/reflex-icd11ect/actions/workflows/tests.yml/badge.svg)](https://github.com/ecrespo/reflex-icd11ect/actions/workflows/tests.yml)
[![quality](https://github.com/ecrespo/reflex-icd11ect/actions/workflows/quality.yml/badge.svg)](https://github.com/ecrespo/reflex-icd11ect/actions/workflows/quality.yml)
[![security](https://github.com/ecrespo/reflex-icd11ect/actions/workflows/security.yml/badge.svg)](https://github.com/ecrespo/reflex-icd11ect/actions/workflows/security.yml)
[![PyPI](https://img.shields.io/pypi/v/reflex-icd11ect.svg)](https://pypi.org/project/reflex-icd11ect/)
[![Python](https://img.shields.io/pypi/pyversions/reflex-icd11ect.svg)](https://pypi.org/project/reflex-icd11ect/)
[![Licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

A [Reflex](https://reflex.dev) custom component for the WHO **ICD-11 Embedded
Classification Tools** ([ECT](https://icd.who.int/docs/icd-api/icd11ect/)): the
*Embedded Coding Tool* and the *Embedded Browser*, powered by the ICD-API.

It wraps [`@whoicd/icd11ect`](https://www.npmjs.com/package/@whoicd/icd11ect)
1.8 and turns its imperative, page-global JavaScript API into ordinary Reflex
components, props and event handlers.

```python
import reflex as rx
from reflex_icd11ect import icd11ect


class State(rx.State):
    code: str = ""
    title: str = ""

    @rx.event
    def on_select(self, entity: dict[str, str]):
        self.code = entity["code"]
        self.title = entity["title"]


def index() -> rx.Component:
    return rx.vstack(
        rx.heading(f"{State.code} {State.title}"),
        icd11ect.coding_tool(
            api_server_url="http://localhost",   # your ICD-API deployment
            placeholder="Search the ICD-11...",
            on_select=State.on_select,
        ),
    )
```

## Install

```bash
pip install reflex-icd11ect
# or
uv add reflex-icd11ect
```

The npm package and its stylesheet are installed into the frontend by Reflex;
there is nothing to add to `rxconfig.py`.

## What you get

| Component | Renders |
| --- | --- |
| `icd11ect.coding_tool(...)` | Search box + result window, configured and bound |
| `icd11ect.browser(...)` | The Embedded Browser |
| `icd11ect.controller(...)` | Lifecycle only, renders nothing |
| `icd11ect.provider(...)` | The controller used as page-wide settings |
| `icd11ect.search_input(ino)` | The bare `input.ctw-input` element |
| `icd11ect.result_window(ino)` | The bare `div.ctw-window` element |
| `icd11ect.browser_window(ino)` | The bare `div.ctw-eb-window` element |

Plus `reflex_icd11ect.handler` (the imperative `ECT.Handler` API as Reflex
events), `IcdTokenProvider` (OAUTH 2.0 client credentials, backend side),
`SelectedEntity` / `BrowserContent` (typed event payloads) and the constants
(`MMS_CHAPTERS`, `LANGUAGES`, `SOURCES`, ...).

The classes are available too: `Icd11ectCodingTool`, `Icd11ectBrowser`,
`Icd11ectController`.

## Choosing a server

`api_server_url` is the only required setting.

| Deployment | Settings |
| --- | --- |
| Local ICD-API (Docker, Windows or systemd service) | `api_server_url="http://localhost"`, `api_secured=False` |
| WHO cloud API | `api_server_url="https://id.who.int"`, `api_secured=True` + a token |
| WHO developer test server (development only) | `api_server_url=WHO_DEVELOPER_TEST_API`, `api_secured=False` |

```bash
# a local deployment, no credentials, no data leaving your network
docker run -p 80:80 -e acceptLicense=true -e saveAnalytics=true whoicd/icd-api
```

## Events

| Prop | ECT callback | Payload |
| --- | --- | --- |
| `on_select` | `selectedEntityFunction` | `code`, `title`, `uri`, `linearization_uri`, `foundation_uri`, `selected_text`, `search_query`, `i_no` |
| `on_search_start` | `searchStartedFunction` | none |
| `on_search_end` | `searchEndedFunction` | none |
| `on_browser_load` | `browserLoadedFunction` | none |
| `on_browser_change` | `browserChangedFunction` | `code`, `uri`, `i_no` |
| `on_token_request` | `getNewTokenFunction` | none |

Payload keys are snake_case; wrap them for attribute access:

```python
from reflex_icd11ect import SelectedEntity

@rx.event
def on_select(self, entity: dict[str, str]):
    selected = SelectedEntity.from_payload(entity)
    if selected.is_postcoordinated:
        ...
```

`on_search_start` / `on_search_end` carry no instance id in ECT, so with several
instances on a page they are delivered to the instance whose search box has
focus, falling back to the one that last emitted an event.

## Driving the tool from the backend

```python
from reflex_icd11ect import handler


class State(rx.State):
    @rx.event
    def code_fever(self):
        return handler.search("1", "fever")

    @rx.event
    def show_tuberculosis(self):
        return handler.set_browser_code("browser", "1B11")

    @rx.event
    def spanish(self):
        return handler.change_language("1", "es")
```

`search`, `clear`, `set_browser_code`, `set_browser_uri`, `change_language`,
`change_source`, `change_minor_version`, `overwrite_configuration`, `bind` and
`set_token` are available. They run entirely on the client, with no extra round
trip.

## OAUTH 2.0 with the WHO cloud API

Register at <https://icd.who.int/icdapi> for a client id and secret, then keep
the secret on the backend:

```python
from reflex_icd11ect import IcdTokenProvider, icd11ect

provider = IcdTokenProvider.from_env()   # ICD_CLIENT_ID / ICD_CLIENT_SECRET


class Auth(rx.State):
    token: str = ""

    @rx.event(background=True)
    async def refresh_token(self):
        token = await provider.async_token()
        async with self:
            self.token = token


icd11ect.coding_tool(
    api_server_url="https://id.who.int",
    api_secured=True,
    token=Auth.token,
    on_token_request=Auth.refresh_token,   # fired when the token expires
    on_select=State.on_select,
)
```

`IcdTokenProvider` caches the token and refreshes it five minutes before it
expires. Only the short-lived token reaches the browser.

If you prefer the pattern WHO documents, where the browser fetches the token
itself, set `token_endpoint="/api/icd/token"` (and `token_field` when the JSON
field is not named `token`) instead of `token`.

## Custom layouts

`coding_tool` is a `controller` with the two elements as children. Split them
when the search box and the results belong in different places:

```python
rx.fragment(
    icd11ect.controller(ino="dx", api_server_url=..., on_select=State.on_select),
    rx.hstack(
        rx.text("Diagnosis"),
        icd11ect.search_input("dx", placeholder="..."),
    ),
    rx.card(icd11ect.result_window("dx")),
)
```

The search box must stay uncontrolled: ECT writes into its value and disables it
while it loads, so do not bind `value` to your state.

## Several instances

`ino` is ECT's `data-ctw-ino`; it identifies an instance and must be unique on
the page. ECT keeps a single configuration per page, so the component merges the
settings of every mounted instance and applies what an instance sets differently
through `ECT.Handler.overwriteConfiguration`:

```python
icd11ect.coding_tool(ino="a", language="en", chapters_filter="")
icd11ect.coding_tool(ino="b", language="es", chapters_filter="06")
icd11ect.browser(ino="c", enable_select_button="categories")
```

Only part of ECT's settings can differ per instance: `api_server_url`,
`api_secured`, `source`, `minor_version`, `language`, `popup_mode`,
`simplified_mode`, `disable_hierarchy`, `words_available`, `chapters_available`,
`chapters_filter`, `subtrees_filter`, `flexisearch_available`,
`search_by_code_or_uri`, `hierarchy_title` and `height`
(`reflex_icd11ect.OVERWRITABLE_SETTINGS`). The rest is page-wide and takes the
value of the last instance that set it.

## Settings

Every ECT setting is a prop, snake_case instead of camelCase. Props you do not
set are not sent, so ECT keeps its own defaults; an empty string is treated the
same way, which makes state-driven props easy.

**Shared** — `api_server_url`, `api_secured`, `source` (`"mms"`, `"icf"`,
`"foundation"`), `minor_version`, `language`, `source_app`, `height`,
`hierarchy_title`, `hierarchy_resizable`, `other_postcoordination`,
`enable_keyboard`, `include_diagnostic_criteria`, `verbose`.

**Coding Tool** — `popup_mode`, `simplified_mode`, `disable_hierarchy`,
`words_available`, `chapters_available`, `chapters_filter`, `subtrees_filter`,
`flexisearch_available`, `search_by_code_or_uri`, `medical_coding_mode`,
`view_selected_uri`.

**Embedded Browser** — `enable_select_button` (`"none"`, `"categories"`,
`"all"`, `"allButRoot"`), `browser_search_available`,
`browser_advanced_search_available`, `browser_hierarchy_available`,
`browser_hierarchy_root_uris`, `browser_uri`,
`display_other_foundation_children`.

Every component accepts every setting: ECT keeps a single configuration per
page, so a Coding Tool setting passed to a browser would still take effect on
the page's Coding Tools, and hiding it would only mislead.

Bridge-only props: `token`, `token_endpoint`, `token_field`,
`token_timeout_ms`, `ino`, plus `placeholder`, `input_props` and `window_props`
for styling the elements.

`docs/settings.md` has the full table with ECT names and per-instance support.

## How it works

ECT is not a React component: it renders itself into DOM nodes carrying
`data-ctw-ino`, and keeps one global configuration and one set of callbacks for
the whole page. The component therefore:

* renders the markup ECT looks for, with your `ino`;
* emits a page-level runtime (`window.__reflexIcd11ect`) that owns the ECT
  configuration and routes ECT's global callbacks to the right instance;
* configures ECT with `autoBind: false` and calls `ECT.Handler.bind(ino)` from a
  `useEffect`, because ECT's auto-binding waits for `window.onload`, an event
  that has already fired by the time a single-page app renders a route;
* re-applies settings and rebinds whenever your props change.

`docs/architecture.md` goes into detail.

## Demo app

```bash
git clone https://github.com/ecrespo/reflex-icd11ect
cd reflex-icd11ect
uv pip install -e .
cd icd11ect_demo && uv run reflex run
```

Six pages: the Coding Tool with every setting live, the Embedded Browser,
several instances side by side, custom layouts, server and OAUTH 2.0 handling,
and a generated API reference.

## Documentation

* [`docs/settings.md`](docs/settings.md) — every prop, its ECT name and whether
  it can differ per instance
* [`docs/architecture.md`](docs/architecture.md) — how the bridge works
* [`docs/troubleshooting.md`](docs/troubleshooting.md) — what to check when
  nothing renders
* [ECT documentation](https://icd.who.int/docs/icd-api/icd11ect/) — WHO
* [ICD-API documentation](https://icd.who.int/docs/icd-api/) — WHO
* [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to set up, test and release
* [`SECURITY.md`](SECURITY.md) — reporting a vulnerability, and how to keep
  the ICD-API credentials out of the browser

## Requirements

* Python >= 3.10, Reflex >= 0.9
* An ICD-API server (local deployment or the WHO cloud API)

## Licence

MIT for this component. The ICD-11 and the Embedded Classification Tools are
published by the World Health Organization under their own licence: see
<https://icd.who.int/en/docs/icd11-license.pdf> and the
[ICD-API terms](https://icd.who.int/icdapi).
