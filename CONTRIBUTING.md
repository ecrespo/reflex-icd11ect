# Contributing

Thanks for taking the time. This is a small package; the workflow is short.

## Branches

- `main` — released code. Protected, only updated through a pull request.
- `develop` — integration branch. Start your branch here and target it with
  your pull request.

## Setting up

```bash
git clone git@github.com:ecrespo/reflex-icd11ect.git
cd reflex-icd11ect
uv venv
uv pip install -e ".[dev]"
```

Node 22 is needed as well: the runtime tests execute the bridge's JavaScript.

## Before you push

The same three commands CI runs:

```bash
ruff check .
ruff format --check .
pytest --cov --cov-fail-under=95
```

And, if you touched anything that talks to the network or handles the token:

```bash
uv pip install -e ".[security]"
bandit -c pyproject.toml -r custom_components
pip-audit --skip-editable
```

## Changing the components

- The `.pyi` stubs are generated, not hand-written. Regenerate them with
  `reflex component build` (from the repo root) and commit the result.
- `custom_components/reflex_icd11ect/constants.py` is the single source of
  truth for the ECT setting names. A new ECT setting means an entry there, a
  prop in `icd11ect.py`, and a line in `docs/settings.md`.
- The JavaScript bridge lives in `_runtime.py` as a template string. Keep it
  readable as JavaScript; `E501` is disabled for that file.

## Demo app

```bash
cd icd11ect_demo
reflex run
```

It points at the package in the repo, so your changes show up directly.

## Releasing

Maintainers only:

1. Bump `version` in `pyproject.toml` and `__version__` in
   `custom_components/reflex_icd11ect/__init__.py` — a test fails if they
   disagree.
2. Add the section to `CHANGELOG.md`; the release notes are extracted from it.
3. Merge into `main`, then push the tag:

   ```bash
   git tag -a v0.2.0 -m "v0.2.0"
   git push origin v0.2.0
   ```

`.github/workflows/release.yml` builds, tests, attests, creates the GitHub
release and publishes to PyPI through Trusted Publishing.
