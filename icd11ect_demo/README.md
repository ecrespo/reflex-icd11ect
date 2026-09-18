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
<https://icd.who.int/icdapi>, then copy the template and fill it in:

```bash
cp .env.example .env
$EDITOR .env          # ICD_CLIENT_ID and ICD_CLIENT_SECRET
```

`rxconfig.py` loads `.env` through Reflex's `env_file`, so `reflex run` picks
the credentials up on its own. `.env` is gitignored; `.env.example` is the
committed template and holds no real values. Exporting the two variables in
your shell works too — the file is only a convenience.

The *Servers & auth* page then fetches tokens through
`reflex_icd11ect.IcdTokenProvider`; the secret stays on the backend and only
the short lived token reaches the browser.

Never put a bearer token in `.env`. Tokens last an hour, the demo fetches them
on demand from the two variables above, and a token written to a file is a
credential on disk with nothing to rotate it. Reflex also persists state to
`.states/*.pkl` while you develop, so a token handed to the component lands
there; that directory is gitignored, and deleting it is safe — Reflex rebuilds
it.

To use a **local deployment** (Docker container, Windows or systemd service),
point the server URL at it and leave authentication off.
