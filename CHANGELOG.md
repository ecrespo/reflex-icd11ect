# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[semantic versioning](https://semver.org/).

## [0.1.0] - 2026-09-17

First release. Wraps `@whoicd/icd11ect` 1.8.

### Added

- `Icd11ectCodingTool` / `icd11ect.coding_tool` — the ICD-11 Embedded Coding
  Tool, search box plus result window, configured and bound.
- `Icd11ectBrowser` / `icd11ect.browser` — the ICD-11 Embedded Browser, with
  `enable_select_button` defaulting to `"all"` when `on_select` is wired.
- `Icd11ectController` / `icd11ect.controller` / `icd11ect.provider` — the
  lifecycle component, for custom layouts and page-wide settings.
- `icd11ect.search_input`, `icd11ect.result_window`,
  `icd11ect.browser_window` — the bare elements ECT binds to.
- Every ECT setting as a snake_case prop, including the ones added in 1.7
  (`hierarchy_resizable`, `other_postcoordination`,
  `include_diagnostic_criteria`, `browser_advanced_search_available`,
  `browser_hierarchy_available`, ICF through `source="icf"`).
- Events `on_select`, `on_search_start`, `on_search_end`, `on_browser_load`,
  `on_browser_change` and `on_token_request`, with payloads renamed to
  snake_case on the frontend.
- `reflex_icd11ect.handler` — `ECT.Handler` as client-side Reflex events:
  `search`, `clear`, `set_browser_code`, `set_browser_uri`, `change_language`,
  `change_source`, `change_minor_version`, `overwrite_configuration`, `bind`,
  `set_token`.
- `IcdTokenProvider` — OAUTH 2.0 client credentials for the WHO cloud API,
  cached and refreshed on the backend.
- `SelectedEntity` and `BrowserContent` payload helpers, and the constants
  `MMS_CHAPTERS`, `LANGUAGES`, `SOURCES`, `SELECT_BUTTON_MODES`,
  `OVERWRITABLE_SETTINGS`, `WHO_CLOUD_API`, `WHO_DEVELOPER_TEST_API`.
- A six-page demo app under `icd11ect_demo/`.
- Documentation: `docs/settings.md`, `docs/architecture.md`,
  `docs/troubleshooting.md`, `CONTRIBUTING.md`, `SECURITY.md`.
- PEP 561 support: the package ships `py.typed` next to the generated stubs,
  so type checkers see the public API.
- Continuous integration: `tests` (Python 3.10 to 3.13), `quality` (ruff,
  coverage gate, distribution metadata) and `security` (gitleaks, bandit,
  pip-audit, CodeQL, dependency review), plus a `release` workflow that
  publishes to PyPI through Trusted Publishing.

### Security

- `IcdTokenProvider.client_secret` is excluded from `repr()`, so the ICD-API
  secret cannot reach a log line or a traceback through the dataclass repr.
