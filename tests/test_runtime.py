"""Tests for the JavaScript runtime.

The behavioural tests run the runtime in node when it is available; the rest
check the source, so the suite is still meaningful without node.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import textwrap

import pytest
from reflex_icd11ect._runtime import ICD11ECT_RUNTIME_JS
from reflex_icd11ect.constants import OVERWRITABLE_SETTINGS

NODE = shutil.which("node")

HARNESS = textwrap.dedent(
    """
    const calls = [];
    const ECT = { Handler: {
      configure: (s, c) => calls.push(["configure", s]),
      overwriteConfiguration: (i, s) => calls.push(["overwrite", i, s]),
      bind: (i) => calls.push(["bind", i]),
    } };
    globalThis.window = {};
    globalThis.document = { activeElement: null };
    const refs = [];
    let refIndex = 0;
    const useRef = (value) => {
      if (refs[refIndex] === undefined) refs[refIndex] = { current: value };
      return refs[refIndex++];
    };
    let pending = [];
    const useEffect = (fn) => pending.push(fn);
    const flush = () => { const queued = pending; pending = []; queued.forEach((fn) => fn()); };
    __RUNTIME__
    const emitted = [];
    __BODY__
    const runtime = window.__reflexIcd11ect || {};
    console.log(JSON.stringify({ calls, emitted, runtime: {
      configured: runtime.configured === true,
      globalSettings: runtime.globalSettings || {},
      instances: Object.keys(runtime.instances || {}),
    }}));
    """
)


def _run(body: str) -> dict:
    script = HARNESS.replace("__RUNTIME__", ICD11ECT_RUNTIME_JS).replace(
        "__BODY__", body
    )
    result = subprocess.run(
        [NODE, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_the_runtime_disables_ect_auto_binding():
    # ECT's autoBind waits for window.onload, which never fires again in a SPA.
    assert "autoBind: false" in ICD11ECT_RUNTIME_JS


def test_the_runtime_knows_which_settings_can_be_overridden():
    assert json.dumps(list(OVERWRITABLE_SETTINGS)) in ICD11ECT_RUNTIME_JS


def test_the_runtime_routes_callbacks_by_instance():
    for callback in (
        "selectedEntityFunction",
        "browserChangedFunction",
        "browserLoadedFunction",
        "searchStartedFunction",
        "searchEndedFunction",
        "getNewTokenFunction",
    ):
        assert callback in ICD11ECT_RUNTIME_JS


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_the_syntax_is_valid():
    result = _run("flush();")
    assert result["calls"] == []


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_one_instance_configures_ect_once_and_binds_it():
    result = _run(
        """
        useIcd11ect("1", { apiServerUrl: "http://api", language: "en" }, {}, {});
        flush();
        """
    )
    assert [call[0] for call in result["calls"]] == ["configure", "bind"]
    assert result["calls"][0][1]["autoBind"] is False
    assert result["calls"][1][1] == "1"
    assert result["runtime"]["instances"] == ["1"]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_empty_settings_are_treated_as_unset():
    result = _run(
        """
        useIcd11ect("1", { apiServerUrl: "http://api", chaptersFilter: "", height: null }, {}, {});
        flush();
        """
    )
    settings = result["calls"][0][1]
    assert "chaptersFilter" not in settings
    assert "height" not in settings


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_ect_is_not_configured_before_a_server_is_known():
    result = _run(
        """
        useIcd11ect("1", { language: "en" }, {}, {});
        flush();
        """
    )
    assert result["calls"] == []
    assert result["runtime"]["configured"] is False


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_a_second_instance_only_overrides_what_differs():
    result = _run(
        """
        useIcd11ect("1", { apiServerUrl: "http://api", language: "en" }, {}, {});
        flush();
        useIcd11ect("2", { apiServerUrl: "http://api", language: "es" }, {}, {});
        flush();
        """
    )
    overrides = [call for call in result["calls"] if call[0] == "overwrite"]
    assert overrides == [["overwrite", "1", {"language": "en"}]]
    assert result["runtime"]["globalSettings"]["language"] == "es"
    assert sorted(result["runtime"]["instances"]) == ["1", "2"]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_callbacks_reach_the_right_instance():
    result = _run(
        """
        useIcd11ect("1", { apiServerUrl: "http://api" },
          { onSelect: (e) => emitted.push(["one", e.code]) }, {});
        flush();
        useIcd11ect("2", { apiServerUrl: "http://api" },
          { onSelect: (e) => emitted.push(["two", e.code]) }, {});
        flush();
        icd11ectCallbacks.selectedEntityFunction({ iNo: "2", code: "1B11" });
        icd11ectCallbacks.selectedEntityFunction({ iNo: "1", code: "5A11" });
        """
    )
    assert result["emitted"] == [["two", "1B11"], ["one", "5A11"]]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_a_callback_without_an_instance_id_is_broadcast():
    result = _run(
        """
        useIcd11ect("1", { apiServerUrl: "http://api" },
          { onBrowserLoad: () => emitted.push("one") }, {});
        flush();
        useIcd11ect("2", { apiServerUrl: "http://api" },
          { onBrowserLoad: () => emitted.push("two") }, {});
        flush();
        icd11ectCallbacks.browserLoadedFunction();
        """
    )
    assert sorted(result["emitted"]) == ["one", "two"]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_unmounting_removes_the_instance_from_the_page_configuration():
    result = _run(
        """
        useIcd11ect("1", { apiServerUrl: "http://api", language: "en" }, {}, {});
        flush();
        delete window.__reflexIcd11ect.instances["1"];
        useIcd11ect("2", { apiServerUrl: "http://api", language: "fr" }, {}, {});
        flush();
        """
    )
    assert result["runtime"]["instances"] == ["2"]
    assert result["runtime"]["globalSettings"]["language"] == "fr"
