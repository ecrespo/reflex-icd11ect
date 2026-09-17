# How the bridge works

`@whoicd/icd11ect` is not a React component. Understanding what it actually does
explains every design decision in this package.

## What ECT is

ECT ships a UMD bundle with its own copy of React. It exposes one object,
`ECT.Handler`, and works by side effect:

1. `ECT.Handler.configure(settings, callbacks)` stores **one** configuration and
   **one** set of callbacks for the whole page.
2. `ECT.Handler.bind(iNo)` looks for `div.ctw-window[data-ctw-ino="<iNo>"]` (the
   Coding Tool) and `div.ctw-eb-window[data-ctw-ino="<iNo>"]` (the Embedded
   Browser) and renders itself into them with its own React.
3. Callbacks are global. `selectedEntityFunction` and `browserChangedFunction`
   receive the `iNo` of the instance that fired them;
   `searchStartedFunction`, `searchEndedFunction` and `browserLoadedFunction`
   receive nothing.
4. `ECT.Handler.overwriteConfiguration(iNo, settings, force)` overrides part of
   the configuration for one instance.

Two consequences matter:

* **Auto-binding does not work in a single-page app.** ECT's `autoBind` adds a
  `window.addEventListener("load", ...)` listener. In a Reflex app that event
  fires long before a route renders its components, so nothing ever binds. Every
  instance must be bound by hand, after the DOM is committed — which is exactly
  what WHO's own React, Angular and Vue samples do.
* **The configuration is page-global.** Components cannot each own their
  settings; something has to reconcile them.

## The runtime singleton

The component emits a JavaScript runtime once per page (deduplicated by Reflex
because every instance emits the identical string) and keeps its state on
`window.__reflexIcd11ect`:

```text
window.__reflexIcd11ect = {
  ECT,                    // the imported module
  instances: {            // one entry per mounted component
    "<ino>": { callbacks, settings, kind },
  },
  globalSettings,         // merge of every mounted instance's settings
  globalSettingsKey,      // its JSON, to detect real changes
  configured,             // whether configure() has run
  token, tokenVersion, tokenAsks, tokenWaiters, tokenConfig,
  lastIno,                // last instance that emitted, for callbacks with no iNo
  setToken(token),        // used by handler.set_token
}
```

ECT's global callbacks are registered once and dispatch to
`instances[iNo].callbacks.current[name]`, a ref that always holds the latest
event handlers, so a re-render never needs to reconfigure ECT.

## What each component emits

A component renders:

* the DOM elements ECT binds to (`input.ctw-input`, `div.ctw-window` or
  `div.ctw-eb-window`) with your `ino` as `data-ctw-ino`, and
* one hook call in the enclosing React component:

```javascript
useIcd11ect(
  "<ino>",
  { apiServerUrl: ..., language: ... },              // ECT settings, camelCase
  { onSelect: (...) => addEvents([...]), ... },      // Reflex event chains
  { kind: "codingTool", token: ... },                // bridge options
)
```

The settings object contains only the props you set, and the runtime drops empty
values, so a prop bound to state that happens to be empty behaves as unset.

## The effect

On mount, and whenever the settings change:

1. register the instance and recompute `globalSettings` as the merge of every
   **currently mounted** instance's settings, so an unmounted route stops
   contributing;
2. if `apiServerUrl` is still missing, stop and wait — a provider mounting later
   will configure everything (this is why a tool with no `api_server_url` of its
   own works);
3. `ECT.Handler.configure({ ...globalSettings, autoBind: false }, callbacks)`
   when the merged settings changed;
4. for each instance, `overwriteConfiguration(ino, differences)` — only the
   settings ECT can override per instance, and only where they differ from the
   merged configuration, so a single-instance page issues no override at all;
5. `ECT.Handler.bind(ino)`.

Cleanup removes the instance from the registry. ECT has no `unbind`, but Reflex
removes the container from the DOM, and remounting binds a fresh one.

`configure()` disables every search box on the page while it re-initialises, so
when the merged configuration changes the runtime rebinds all instances rather
than only the one whose props changed.

## Events

Reflex event chains are compiled into the hook call by the same mechanism Reflex
uses for `rx.clipboard`: the event trigger is excluded from the rendered props
and formatted into the hook instead. So `on_select=State.handle` becomes a real
arrow function in the page, closing over the state context, and no event prop
ever lands on a DOM element.

The payload is rewritten in JavaScript before it is sent to the backend, turning
ECT's `{iNo, foundationUri, ...}` into `{i_no, foundation_uri, ...}`.

Because ECT does not say which instance started a search, `on_search_start` and
`on_search_end` are routed to the instance whose `.ctw-input` has focus, falling
back to `lastIno` and finally broadcasting.

## The imperative API

`reflex_icd11ect.handler` builds its events with `rx.run_script`, which compiles
to a closure that the client evaluates when the event fires. That is why
`handler.change_language("1", State.lang)` reads the state var at that moment
rather than at render time, and why no server round trip is involved.

## Tokens

ECT asks for a token through `getNewTokenFunction`, decodes its `exp` claim and
caches it until five minutes before expiry. The runtime answers in one of two
ways:

* `token_endpoint` set: fetch it from that URL and return the JSON field.
* otherwise: the first request returns the token the `token` prop already
  provided; any later one fires `on_token_request`, waits for the `token` prop to
  change (up to `token_timeout_ms`, 15 s by default) and returns the new value.

ECT decodes the token as a JWT, so returning an empty string is an error, not a
no-op: with `api_secured=True`, make sure a token is available before the first
query. The console says so when it is not.
