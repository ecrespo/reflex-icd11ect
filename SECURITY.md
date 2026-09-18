# Security policy

## Supported versions

The latest released version on PyPI is the only one that receives fixes.

| Version | Supported |
| --- | --- |
| 0.1.x | ✅ |

## Reporting a vulnerability

Report privately through
[GitHub Security Advisories](https://github.com/ecrespo/reflex-icd11ect/security/advisories/new),
or by email to <ecrespo@gmail.com> if you cannot use that form. Please do not
open a public issue for a vulnerability.

Include what you did, what you expected and what happened, and a minimal
reproduction if you have one. You can expect a first answer within seven days.

## Scope

This package wraps WHO's `@whoicd/icd11ect` and talks to an ICD-API server.
Vulnerabilities in the ICD-API itself or in the npm package belong to WHO;
report those through <https://icd.who.int/icdapi>.

## Handling credentials

The WHO cloud ICD-API uses the OAUTH 2.0 client credentials grant, and that
grant is only safe on a server:

- **Never ship the client id and secret to the browser.** Keep them in
  environment variables read by your Reflex backend. `IcdTokenProvider.from_env()`
  is built for that; its `client_secret` is kept out of `repr()` so it does not
  leak into a log line or a traceback.
- **Only the access token reaches the frontend**, over the Reflex websocket,
  via the `token` prop. It is short-lived; refresh it from `on_token_request`.
- **Do not commit tokens.** Reflex serialises state to `.states/*.pkl` during
  development, so a token used in a demo lands on disk. Those files are
  gitignored; delete them before sharing a working copy.
- A local ICD-API deployment (Docker, Windows service, systemd) needs no
  credentials at all: set `api_secured=False` and nothing leaves your network.

## Automated checks

Every push and pull request runs, under `.github/workflows/security.yml`:

- `gitleaks` over the history and the working tree (secrets),
- `bandit` over the shipped package (SAST),
- `pip-audit` over the resolved dependency tree (known CVEs),
- CodeQL with the `security-and-quality` queries,
- `dependency-review` on pull requests.

Releases are published to PyPI with
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/) — no long-lived
API token is stored in this repository — and each artifact carries a
[build provenance attestation](https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations).
