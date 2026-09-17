"""Constants and setting maps for the ICD-11 Embedded Classification Tools.

Every entry of the ``*_SETTINGS`` maps below is ``python_prop_name ->
ECT setting name``. They are the single source of truth used to build the
JavaScript settings object handed to ``ECT.Handler.configure`` and
``ECT.Handler.overwriteConfiguration``.

The names were verified against the ``@whoicd/icd11ect`` 1.8.0 bundle
(the ``Handler.configure`` implementation) and the WHO documentation for
ECT 1.5 through 1.8.
"""

from __future__ import annotations

from typing import Final

#: Public WHO ICD-API cloud server. Requires OAUTH 2.0 (``api_secured=True``).
WHO_CLOUD_API: Final[str] = "https://id.who.int"

#: WHO test server for software development only. No authentication needed.
#: Do not use it in production; it is rate limited and may go away.
WHO_DEVELOPER_TEST_API: Final[str] = (
    "https://icd11restapi-developer-test.azurewebsites.net"
)

#: OAUTH 2.0 token endpoint of the ICD-API access management service.
ICD_TOKEN_ENDPOINT: Final[str] = "https://icdaccessmanagement.who.int/connect/token"

#: OAUTH 2.0 scope required by the ICD-API.
ICD_TOKEN_SCOPE: Final[str] = "icdapi_access"

#: npm package wrapped by this component.
ECT_PACKAGE: Final[str] = "@whoicd/icd11ect"

#: npm version range installed in the frontend. ECT is released as
#: ``1.x`` with occasional breaking changes in the minor, so it is pinned
#: to the tested minor version.
ECT_VERSION: Final[str] = "1.8"

#: Stylesheet shipped by the npm package; required for the tools to look right.
ECT_STYLESHEET: Final[str] = f"{ECT_PACKAGE}/style.css"

# --------------------------------------------------------------------------- #
# Settings
# --------------------------------------------------------------------------- #

#: Settings shared by the Embedded Coding Tool and the Embedded Browser.
COMMON_SETTINGS: Final[dict[str, str]] = {
    "api_server_url": "apiServerUrl",
    "api_secured": "apiSecured",
    "source": "source",
    "minor_version": "minorVersion",
    "language": "language",
    "source_app": "sourceApp",
    "height": "height",
    "hierarchy_title": "hierarchyTitle",
    "hierarchy_resizable": "hierarchyResizable",
    "other_postcoordination": "otherPostcoordination",
    "enable_keyboard": "enableKeyboard",
    "include_diagnostic_criteria": "includeDiagnosticCriteria",
    "verbose": "verbose",
}

#: Settings that only affect the Embedded Coding Tool.
CODING_TOOL_SETTINGS: Final[dict[str, str]] = {
    "popup_mode": "popupMode",
    "simplified_mode": "simplifiedMode",
    "disable_hierarchy": "disableHierarchy",
    "words_available": "wordsAvailable",
    "chapters_available": "chaptersAvailable",
    "chapters_filter": "chaptersFilter",
    "subtrees_filter": "subtreesFilter",
    "flexisearch_available": "flexisearchAvailable",
    "search_by_code_or_uri": "searchByCodeOrURI",
    "medical_coding_mode": "medicalCodingMode",
    "view_selected_uri": "viewSelectedURI",
}

#: Settings that only affect the Embedded Browser.
BROWSER_SETTINGS: Final[dict[str, str]] = {
    "enable_select_button": "enableSelectButton",
    "browser_search_available": "browserSearchAvailable",
    "browser_advanced_search_available": "browserAdvancedSearchAvailable",
    "browser_hierarchy_available": "browserHierarchyAvailable",
    "browser_hierarchy_root_uris": "browserHierarchyRootURIs",
    "browser_uri": "browserURI",
    "display_other_foundation_children": "displayOtherFoundationChildren",
}

#: Every setting understood by ECT, python name -> ECT name.
ALL_SETTINGS: Final[dict[str, str]] = {
    **COMMON_SETTINGS,
    **CODING_TOOL_SETTINGS,
    **BROWSER_SETTINGS,
}

#: Settings that ``ECT.Handler.overwriteConfiguration`` can change for a
#: single instance. Anything else is global to the page and is applied
#: through ``ECT.Handler.configure``.
OVERWRITABLE_SETTINGS: Final[tuple[str, ...]] = (
    "apiServerUrl",
    "apiSecured",
    "source",
    "minorVersion",
    "language",
    "popupMode",
    "simplifiedMode",
    "disableHierarchy",
    "wordsAvailable",
    "chaptersAvailable",
    "chaptersFilter",
    "subtreesFilter",
    "flexisearchAvailable",
    "searchByCodeOrURI",
    "hierarchyTitle",
    "height",
)

# --------------------------------------------------------------------------- #
# Enumerations (plain strings, so they stay usable from rx.Var)
# --------------------------------------------------------------------------- #

#: ``source`` values. ``mms`` is the ICD-11 MMS linearization, ``icf`` the
#: International Classification of Functioning (ECT >= 1.7), ``foundation``
#: the ICD-11 Foundation (Embedded Browser only).
SOURCE_MMS: Final[str] = "mms"
SOURCE_ICF: Final[str] = "icf"
SOURCE_FOUNDATION: Final[str] = "foundation"
SOURCES: Final[tuple[str, ...]] = (SOURCE_MMS, SOURCE_ICF, SOURCE_FOUNDATION)

#: ``enable_select_button`` values for the Embedded Browser.
SELECT_BUTTON_NONE: Final[str] = "none"
SELECT_BUTTON_CATEGORIES: Final[str] = "categories"
SELECT_BUTTON_ALL: Final[str] = "all"
SELECT_BUTTON_ALL_BUT_ROOT: Final[str] = "allButRoot"
SELECT_BUTTON_MODES: Final[tuple[str, ...]] = (
    SELECT_BUTTON_NONE,
    SELECT_BUTTON_CATEGORIES,
    SELECT_BUTTON_ALL,
    SELECT_BUTTON_ALL_BUT_ROOT,
)

#: Languages the ICD-11 API serves, ISO 639-1 code -> English name.
#: Availability depends on the release and on the server deployment.
LANGUAGES: Final[dict[str, str]] = {
    "ar": "Arabic",
    "cs": "Czech",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ru": "Russian",
    "tr": "Turkish",
    "uz": "Uzbek",
    "zh": "Chinese",
}

#: Languages written right to left. ECT adds the ``rtl`` class for these.
RTL_LANGUAGES: Final[tuple[str, ...]] = ("ar", "he")

#: ICD-11 MMS chapters, code -> title. Use the keys with ``chapters_filter``.
MMS_CHAPTERS: Final[dict[str, str]] = {
    "01": "Certain infectious or parasitic diseases",
    "02": "Neoplasms",
    "03": "Diseases of the blood or blood-forming organs",
    "04": "Diseases of the immune system",
    "05": "Endocrine, nutritional or metabolic diseases",
    "06": "Mental, behavioural or neurodevelopmental disorders",
    "07": "Sleep-wake disorders",
    "08": "Diseases of the nervous system",
    "09": "Diseases of the visual system",
    "10": "Diseases of the ear or mastoid process",
    "11": "Diseases of the circulatory system",
    "12": "Diseases of the respiratory system",
    "13": "Diseases of the digestive system",
    "14": "Diseases of the skin",
    "15": "Diseases of the musculoskeletal system or connective tissue",
    "16": "Diseases of the genitourinary system",
    "17": "Conditions related to sexual health",
    "18": "Pregnancy, childbirth or the puerperium",
    "19": "Certain conditions originating in the perinatal period",
    "20": "Developmental anomalies",
    "21": "Symptoms, signs or clinical findings, not elsewhere classified",
    "22": "Injury, poisoning or certain other consequences of external causes",
    "23": "External causes of morbidity or mortality",
    "24": "Factors influencing health status or contact with health services",
    "25": "Codes for special purposes",
    "26": "Supplementary Chapter Traditional Medicine Conditions - Module I",
    "V": "Supplementary section for functioning assessment",
    "X": "Extension Codes",
}
