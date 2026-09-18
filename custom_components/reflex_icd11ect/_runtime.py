"""The JavaScript runtime that bridges ECT to Reflex.

``@whoicd/icd11ect`` is not a React component: it is an imperative library
that renders itself into DOM nodes carrying ``data-ctw-ino`` attributes, and
it keeps a single global configuration plus a single set of callbacks for the
whole page.

This module holds the JavaScript that reconciles that model with Reflex:

* a page level singleton (``window.__reflexIcd11ect``) that owns the ECT
  configuration and routes ECT's global callbacks to the right component
  instance, keyed by ``iNo``;
* ``useIcd11ect``, the hook each component emits, which registers the
  instance, configures ECT once, applies the per instance overrides and binds
  the tool after the DOM has been committed (``autoBind`` is always disabled,
  because ECT's auto binding listens for ``window.onload``, an event that has
  long fired by the time a single page app renders a route);
* OAUTH 2.0 token plumbing: either a token endpoint fetched from the browser,
  or a round trip to the Reflex backend through the ``on_token_request``
  event.
"""

from __future__ import annotations

import json

from reflex_icd11ect.constants import OVERWRITABLE_SETTINGS

_RUNTIME_TEMPLATE = r"""
/* reflex-icd11ect runtime. Bridges the imperative @whoicd/icd11ect API to Reflex. */
const ICD11ECT_OVERWRITABLE = __OVERWRITABLE__;

const icd11ectRuntime = () => {
  if (typeof window === "undefined") return null;
  let rt = window.__reflexIcd11ect;
  if (!rt) {
    rt = window.__reflexIcd11ect = {
      instances: {},
      globalSettings: {},
      globalSettingsKey: "",
      configured: false,
      verbose: false,
      token: null,
      tokenVersion: 0,
      tokenAsks: 0,
      tokenConfig: {},
      tokenWaiters: [],
      lastIno: null,
    };
  }
  rt.ECT = ECT;
  /* Exposed on the singleton so `rx.call_script` helpers can reach them. */
  rt.setToken = icd11ectSetToken;
  rt.callbacks = icd11ectCallbacks;
  return rt;
};

const icd11ectLog = (...args) => {
  const rt = icd11ectRuntime();
  if (rt && rt.verbose) console.log("[reflex-icd11ect]", ...args);
};

const icd11ectSetToken = (token) => {
  const rt = icd11ectRuntime();
  if (!rt || !token || token === rt.token) return;
  rt.token = token;
  rt.tokenVersion += 1;
  const waiters = rt.tokenWaiters;
  rt.tokenWaiters = [];
  waiters.forEach((resolve) => resolve(token));
  icd11ectLog("token updated, version", rt.tokenVersion);
};

const icd11ectWaitForToken = (rt, timeoutMs) =>
  new Promise((resolve) => {
    let settled = false;
    const finish = (value) => {
      if (settled) return;
      settled = true;
      resolve(value || "");
    };
    const timer = setTimeout(() => finish(rt.token), timeoutMs);
    rt.tokenWaiters.push((token) => {
      clearTimeout(timer);
      finish(token);
    });
  });

const icd11ectDispatch = (iNo, name, ...args) => {
  const rt = icd11ectRuntime();
  if (!rt) return;
  if (iNo === null || iNo === undefined || iNo === "") {
    Object.keys(rt.instances).forEach((key) => icd11ectDispatch(key, name, ...args));
    return;
  }
  const instance = rt.instances[String(iNo)];
  const handler =
    instance && instance.callbacks && instance.callbacks.current
      ? instance.callbacks.current[name]
      : undefined;
  if (handler) handler(...args);
};

/* ECT does not tell us which instance started or ended a search, so fall back
   to the focused search box, then to the instance that last emitted. */
const icd11ectActiveIno = () => {
  const rt = icd11ectRuntime();
  if (!rt) return null;
  if (typeof document !== "undefined") {
    const active = document.activeElement;
    if (active && active.classList && active.classList.contains("ctw-input")) {
      const iNo = active.getAttribute("data-ctw-ino");
      if (iNo) return iNo;
    }
  }
  return rt.lastIno;
};

const icd11ectCallbacks = {
  selectedEntityFunction: (selectedEntity) => {
    const rt = icd11ectRuntime();
    if (rt && selectedEntity) rt.lastIno = String(selectedEntity.iNo);
    icd11ectDispatch(selectedEntity && selectedEntity.iNo, "onSelect", selectedEntity);
  },
  browserChangedFunction: (browserContent) => {
    icd11ectDispatch(
      browserContent && browserContent.iNo,
      "onBrowserChange",
      browserContent,
    );
  },
  browserLoadedFunction: () => icd11ectDispatch(null, "onBrowserLoad"),
  searchStartedFunction: () => icd11ectDispatch(icd11ectActiveIno(), "onSearchStart"),
  searchEndedFunction: () => icd11ectDispatch(icd11ectActiveIno(), "onSearchEnd"),
  getNewTokenFunction: async () => {
    const rt = icd11ectRuntime();
    if (!rt) return "";
    const config = rt.tokenConfig || {};
    rt.tokenAsks += 1;
    if (config.endpoint) {
      try {
        const response = await fetch(config.endpoint, config.fetchOptions || {});
        const payload = await response.json();
        const token =
          typeof payload === "string"
            ? payload
            : payload[config.field || "token"] || payload.access_token;
        icd11ectSetToken(token);
        return token || "";
      } catch (error) {
        console.error(
          "[reflex-icd11ect] could not fetch an ICD-API token from " + config.endpoint,
          error,
        );
        return rt.token || "";
      }
    }
    /* The token handed over by the backend is still the fresh one on the
       first request, ECT only asks again once it has expired. */
    if (rt.token && rt.tokenAsks === 1) return rt.token;
    const known = rt.tokenVersion;
    icd11ectDispatch(null, "onTokenRequest");
    if (rt.tokenVersion !== known) return rt.token || "";
    const token = await icd11ectWaitForToken(rt, config.timeoutMs || 15000);
    if (!token) {
      console.error(
        "[reflex-icd11ect] the ICD-API is configured with api_secured=True but no " +
          "token was provided. Set the `token` prop, handle `on_token_request`, " +
          "or set `token_endpoint`.",
      );
    }
    return token;
  },
};

/* A prop bound to state can legitimately be empty; treat that as "not set" so
   ECT keeps its own default instead of receiving an empty setting. */
const icd11ectClean = (settings) =>
  Object.fromEntries(
    Object.entries(settings || {}).filter(
      ([, value]) => value !== undefined && value !== null && value !== "",
    ),
  );

const icd11ectConfigure = (rt) => {
  const settings = rt.globalSettings || {};
  if (!settings.apiServerUrl) {
    icd11ectLog("waiting for api_server_url before configuring ECT");
    return false;
  }
  const key = JSON.stringify(settings);
  if (rt.configured && rt.globalSettingsKey === key) return true;
  rt.ECT.Handler.configure({ ...settings, autoBind: false }, icd11ectCallbacks);
  rt.configured = true;
  rt.globalSettingsKey = key;
  icd11ectLog("ECT configured", settings);
  return true;
};

/* Only the settings ECT can override per instance are worth sending, and only
   when they differ from the page wide configuration. */
const icd11ectApplyInstance = (rt, iNo, settings) => {
  const overrides = {};
  ICD11ECT_OVERWRITABLE.forEach((key) => {
    const value = settings[key];
    if (value !== undefined && JSON.stringify(value) !== JSON.stringify(rt.globalSettings[key])) {
      overrides[key] = value;
    }
  });
  if (Object.keys(overrides).length === 0) return;
  icd11ectLog("overwriteConfiguration", iNo, overrides);
  rt.ECT.Handler.overwriteConfiguration(String(iNo), overrides, true);
};

const icd11ectBind = (rt, iNo) => {
  icd11ectLog("bind", iNo);
  rt.ECT.Handler.bind(String(iNo));
};

const icd11ectBindAll = (rt) => {
  Object.keys(rt.instances).forEach((iNo) => {
    icd11ectApplyInstance(rt, iNo, rt.instances[iNo].settings || {});
    icd11ectBind(rt, iNo);
  });
};

/* Registers one Coding Tool / Embedded Browser instance and keeps ECT in sync
   with its props. */
const useIcd11ect = (iNo, settings, callbacks, options) => {
  const key = String(iNo);
  const opts = options || {};
  const callbacksRef = useRef(callbacks);
  callbacksRef.current = callbacks;
  const cleanSettings = icd11ectClean(settings);
  const settingsKey = JSON.stringify(cleanSettings);
  const token = opts.token;
  const tokenEndpoint = opts.tokenEndpoint;
  const tokenField = opts.tokenField;
  const tokenTimeout = opts.tokenTimeoutMs;
  const verbose = opts.verbose;

  useEffect(() => {
    const rt = icd11ectRuntime();
    if (!rt) return;
    if (verbose) rt.verbose = true;
    if (tokenEndpoint || tokenField || tokenTimeout) {
      rt.tokenConfig = {
        ...rt.tokenConfig,
        endpoint: tokenEndpoint,
        field: tokenField,
        timeoutMs: tokenTimeout,
      };
    }
  }, [tokenEndpoint, tokenField, tokenTimeout, verbose]);

  useEffect(() => {
    if (token) icd11ectSetToken(token);
  }, [token]);

  useEffect(() => {
    const rt = icd11ectRuntime();
    if (!rt) return undefined;
    rt.instances[key] = { callbacks: callbacksRef, settings: cleanSettings, kind: opts.kind };
    /* Page wide configuration is the merge of every mounted instance, so an
       unmounted one stops contributing. */
    rt.globalSettings = Object.keys(rt.instances).reduce(
      (merged, instanceKey) => ({ ...merged, ...(rt.instances[instanceKey].settings || {}) }),
      {},
    );
    const needsConfigure =
      !rt.configured || rt.globalSettingsKey !== JSON.stringify(rt.globalSettings);
    const cleanup = () => {
      delete rt.instances[key];
    };
    if (!icd11ectConfigure(rt)) return cleanup;
    if (needsConfigure) {
      /* configure() resets every search box on the page, rebind them all. */
      icd11ectBindAll(rt);
    } else {
      icd11ectApplyInstance(rt, key, cleanSettings);
      icd11ectBind(rt, key);
    }
    return cleanup;
  }, [key, settingsKey]);
};
"""

#: The JavaScript emitted once per page by every ICD-11 ECT component.
ICD11ECT_RUNTIME_JS: str = _RUNTIME_TEMPLATE.replace(
    "__OVERWRITABLE__", json.dumps(list(OVERWRITABLE_SETTINGS))
).strip()
