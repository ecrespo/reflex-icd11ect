# Settings reference

Generated from the component, against `@whoicd/icd11ect` 1.8.

Every prop is optional except `api_server_url`. A prop you do not set, or set to an empty string, is not sent to ECT, which then applies its own default; that makes it safe to bind a prop to a state var that starts empty.

Every component accepts every setting. ECT keeps a single configuration for the whole page, so a Coding Tool setting passed to an Embedded Browser still takes effect on the Coding Tools of that page, and hiding it would only be misleading.

**Per instance** says whether `ECT.Handler.overwriteConfiguration` can give the setting a different value for one instance. Page-wide settings take the value of the last mounted instance that sets them.

## Shared settings

They apply to both tools.

| Prop | ECT setting | Per instance | Description |
| --- | --- | --- | --- |
| `api_server_url` | `apiServerUrl` | yes | URL of the ICD-API server, e.g. `https://id.who.int` for the WHO cloud or `http://localhost` for a local deployment. Required, unless another instance on the page already provides it. |
| `api_secured` | `apiSecured` | yes | Whether the server requires an OAUTH 2.0 bearer token. `True` for the WHO cloud API, `False` for a local deployment. |
| `source` | `source` | yes | Classification to use: `"mms"` (ICD-11 MMS), `"icf"` (ECT >= 1.7) or `"foundation"` (Embedded Browser only). Defaults to `"mms"`. |
| `minor_version` | `minorVersion` | yes | Release to use, e.g. `"2025-01"`. Defaults to the latest release the server reports. |
| `language` | `language` | yes | ISO 639-1 language code of the content and of the interface. |
| `source_app` | `sourceApp` | page-wide | Name of your application, reported to WHO's usage analytics. |
| `height` | `height` | yes | Maximum height of the tool, in CSS `px` or `vh` units. |
| `hierarchy_title` | `hierarchyTitle` | yes | Title shown above the hierarchy panel. |
| `hierarchy_resizable` | `hierarchyResizable` | page-wide | Whether the hierarchy panel can be resized with the mouse (ECT >= 1.7). |
| `other_postcoordination` | `otherPostcoordination` | page-wide | Whether the extended postcoordination options are offered (ECT >= 1.7). |
| `enable_keyboard` | `enableKeyboard` | page-wide | Whether keyboard navigation is enabled. Always off on mobile. |
| `include_diagnostic_criteria` | `includeDiagnosticCriteria` | page-wide | Whether diagnostic requirements are included in the content (ECT >= 1.7). |
| `verbose` | `verbose` | page-wide | Whether ECT logs what it does to the browser console. |

## Embedded Coding Tool settings

They shape the search box and its results.

| Prop | ECT setting | Per instance | Description |
| --- | --- | --- | --- |
| `popup_mode` | `popupMode` | yes | Whether the results are shown as a dropdown below the search box instead of a block in the page flow. |
| `simplified_mode` | `simplifiedMode` | yes | Whether to show a stripped down output with codes and titles only. Implies `disable_hierarchy` and turns the word list, the chapter filter and flexisearch off. |
| `disable_hierarchy` | `disableHierarchy` | yes | Whether to hide the ICD-11 hierarchy browser. |
| `words_available` | `wordsAvailable` | yes | Whether the list of related words is shown. |
| `chapters_available` | `chaptersAvailable` | yes | Whether the chapter filter is offered to the user (MMS only). |
| `chapters_filter` | `chaptersFilter` | yes | Chapters the search is limited to, semicolon separated, e.g. `"01;02;21"`. See :data:`~reflex_icd11ect.constants.MMS_CHAPTERS`. |
| `subtrees_filter` | `subtreesFilter` | yes | Foundation URIs the search is limited to, comma separated. |
| `flexisearch_available` | `flexisearchAvailable` | yes | Whether the flexible search is used when the strict search finds nothing. |
| `search_by_code_or_uri` | `searchByCodeOrURI` | yes | Whether typing a code or a URI searches for that entity. |
| `medical_coding_mode` | `medicalCodingMode` | page-wide | Medical coding mode. Undocumented ECT setting, use with care. |
| `view_selected_uri` | `viewSelectedURI` | page-wide | Show the URI of the selection instead of its code. Undocumented ECT setting, use with care. |

## Embedded Browser settings

They shape the embedded browser.

| Prop | ECT setting | Per instance | Description |
| --- | --- | --- | --- |
| `enable_select_button` | `enableSelectButton` | page-wide | Which entities get a select button: `"none"` (the ECT default), `"categories"`, `"all"` or `"allButRoot"`. |
| `browser_search_available` | `browserSearchAvailable` | page-wide | Whether the browser shows its own search box. |
| `browser_advanced_search_available` | `browserAdvancedSearchAvailable` | page-wide | Whether the advanced search is offered (ECT >= 1.7). |
| `browser_hierarchy_available` | `browserHierarchyAvailable` | page-wide | Whether the hierarchy panel is shown (ECT >= 1.7). |
| `browser_hierarchy_root_uris` | `browserHierarchyRootURIs` | page-wide | Foundation URIs the hierarchy is restricted to. |
| `browser_uri` | `browserURI` | page-wide | URI of the entity shown when the browser loads. |
| `display_other_foundation_children` | `displayOtherFoundationChildren` | page-wide | Whether children that are not part of the linearization are listed. |

## Bridge-only props

These configure the Reflex wrapper rather than ECT.

| Prop | Description |
| --- | --- |
| `ino` | Instance identifier, rendered as `data-ctw-ino`. Unique per page. |
| `token` | A valid OAUTH 2.0 bearer token (a JWT). Required when `api_secured=True` unless `token_endpoint` is set. Keep it in your state and refresh it from `on_token_request`. |
| `token_endpoint` | URL the browser fetches a token from, the pattern WHO documents. The response must be JSON; see `token_field`. |
| `token_field` | Key of the JSON field holding the token in `token_endpoint`'s response. Defaults to `"token"`, falling back to `"access_token"`. |
| `token_timeout_ms` | How long to wait, in milliseconds, for the backend to answer `on_token_request` before giving up. Defaults to 15000. |
| `placeholder` | Placeholder of the search box (`coding_tool` only). |
| `input_props` | Props forwarded to the search box element. |
| `window_props` | Props forwarded to the result / browser container. |

## Events

| Prop | ECT callback | Payload keys |
| --- | --- | --- |
| `on_select` | `selectedEntityFunction` | `i_no`, `code`, `title`, `uri`, `linearization_uri`, `foundation_uri`, `selected_text`, `best_match_text`, `search_query` |
| `on_search_start` | `searchStartedFunction` | none |
| `on_search_end` | `searchEndedFunction` | none |
| `on_browser_load` | `browserLoadedFunction` | none |
| `on_browser_change` | `browserChangedFunction` | `i_no`, `code`, `uri` |
| `on_token_request` | `getNewTokenFunction` | none |

## ECT versions

ECT is released as 1.x and occasionally adds settings in a minor version. This component installs the version in `reflex_icd11ect.ECT_VERSION` (currently `1.8`) and covers the settings up to it:

* **1.5 / 1.6** — the Coding Tool and the Embedded Browser, with everything below except the entries noted next.
* **1.7** — `hierarchy_resizable`, `other_postcoordination`, `browser_advanced_search_available`, `browser_hierarchy_available`, `include_diagnostic_criteria`, and ICF support through `source="icf"`.
* **1.8** — the current release. `language` became overwritable per instance, so several instances can run in different languages.

`medical_coding_mode` and `view_selected_uri` exist in the ECT bundle but are absent from WHO's documentation; they are exposed for completeness and may change without notice.

