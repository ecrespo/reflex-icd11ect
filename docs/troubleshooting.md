# Troubleshooting

Set `verbose=True` on any instance first: ECT and this bridge then log what they
do to the browser console (`[reflex-icd11ect] ...`).

## Nothing renders in the result window

* **Is `api_server_url` set?** The console shows
  `waiting for api_server_url before configuring ECT` until a component or a
  provider supplies it.
* **Is the search box inside the same instance?** The `input.ctw-input` and the
  `div.ctw-window` must carry the same `ino`.
* **Is the `ino` unique?** Two components sharing an `ino` overwrite each other
  in the registry.

## The search box does nothing / clears itself

Do not bind `value` to your state. ECT writes into the input, disables it while
it initialises and animates its placeholder; a controlled React input fights it.
Use `on_select` to read the result instead.

## `401` or `403` from the API

* `api_secured=True` is required for `https://id.who.int`, and forbidden for a
  local deployment.
* A token must be available before the first query. Pass `token=...` (and answer
  `on_token_request`) or set `token_endpoint`.
* Tokens last about an hour; ECT refreshes five minutes early, which is when
  `on_token_request` fires.
* `Token is empty` in the console means `on_token_request` did not answer within
  `token_timeout_ms`.

## CORS errors

ECT queries the ICD-API from the browser. A local deployment has to allow your
app's origin; the ICD-API container does by default. Note that the WHO developer
test server is for development only and can be rate limited.

## Nothing happens when I select in the Embedded Browser

`enable_select_button` defaults to `"none"` in ECT, so there is no select button
at all. Passing `on_select` sets it to `"all"` for you, but an explicit
`enable_select_button="none"` wins.

## A setting is ignored on one instance

Only part of ECT's settings can differ per instance
(`reflex_icd11ect.OVERWRITABLE_SETTINGS`). Anything else is page-wide and takes
the value of the last mounted instance that sets it — including
`enable_select_button`, `include_diagnostic_criteria` and the `browser_*`
settings.

## `on_search_start` fires on the wrong instance

ECT does not report an instance id for search callbacks. The bridge uses the
focused search box, then the instance that last emitted an event. With several
instances, prefer `on_select` when you need certainty.

## Styling

ECT ships its own stylesheet, imported for you. Override it in your app's
stylesheet with the `ctw-` classes, or pass `input_props` and `window_props` to
style the elements this component renders. `height` (a prop) limits the tool's
height; the hierarchy panel can be resized by the user unless
`hierarchy_resizable=False`.

Arabic and Hebrew get an `rtl` class from ECT automatically.

## Upgrading ECT

`reflex_icd11ect.ECT_VERSION` pins the npm minor version the component was
tested against. To try another one, install it in the frontend yourself
(`lib_dependencies` in a subclass, or an entry in your app's `package.json`
overrides) and report back if a setting has moved.
