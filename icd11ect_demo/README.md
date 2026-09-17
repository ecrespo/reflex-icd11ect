# reflex-icd11ect demo

A Reflex app that exercises every part of the `reflex-icd11ect` component:
the Embedded Coding Tool, the Embedded Browser, several instances on one page,
custom layouts, the imperative `ECT.Handler` API and the three ways of reaching
an ICD-API server.

## Run it

```bash
# from the repository root
uv pip install -e .
cd icd11ect_demo
uv run reflex run
```

Then open http://localhost:3000.

## Which server?

The demo starts against WHO's **developer test server**, which needs no
credentials and is meant for development only.

To use the WHO **cloud API** (`https://id.who.int`), register at
<https://icd.who.int/icdapi> and export your credentials before starting:

```bash
export ICD_CLIENT_ID=...
export ICD_CLIENT_SECRET=...
```

The *Servers & auth* page then fetches tokens through
`reflex_icd11ect.IcdTokenProvider`; the secret stays on the backend and only
the short lived token reaches the browser.

To use a **local deployment** (Docker container, Windows or systemd service),
point the server URL at it and leave authentication off.
