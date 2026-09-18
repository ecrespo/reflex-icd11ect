"""Tests for the packaging metadata.

These guard the things that only break once the package is published: a
version that drifted between the distribution metadata and `__init__.py`, a
missing PEP 561 marker, or an `__all__` entry that does not resolve.
"""

from __future__ import annotations

import importlib.metadata
from pathlib import Path

import reflex_icd11ect

DISTRIBUTION = "reflex-icd11ect"
ROOT = Path(__file__).resolve().parent.parent
PACKAGE = Path(reflex_icd11ect.__file__).parent


def test_version_matches_the_distribution_metadata():
    assert reflex_icd11ect.__version__ == importlib.metadata.version(DISTRIBUTION)


def test_changelog_documents_the_current_version():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{reflex_icd11ect.__version__}]" in changelog


def test_the_package_is_marked_as_typed():
    assert (PACKAGE / "py.typed").is_file()


def test_the_stubs_ship_with_the_package():
    assert {path.name for path in PACKAGE.glob("*.pyi")} >= {
        "icd11ect.pyi",
        "namespace.pyi",
    }


def test_every_exported_name_resolves():
    missing = [
        name for name in reflex_icd11ect.__all__ if not hasattr(reflex_icd11ect, name)
    ]
    assert missing == []


def test_all_has_no_duplicates():
    """Ruff's RUF022 owns the ordering; this only guards against duplicates."""
    exported = reflex_icd11ect.__all__
    assert len(set(exported)) == len(exported)


def test_the_ect_version_pin_is_documented():
    """The npm pin is part of the public contract, keep it in the README."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert reflex_icd11ect.ECT_VERSION in readme


def test_every_classifier_is_a_real_trove_classifier():
    """PyPI rejects the whole upload over one bad classifier.

    `twine check --strict` does not catch this: it validates the README and
    the metadata version, not the classifier list. Only the upload does, and
    by then the tag is already pushed.
    """
    from trove_classifiers import classifiers as known

    declared = importlib.metadata.metadata(DISTRIBUTION).get_all("Classifier") or []
    assert declared, "the distribution declares no classifiers"
    assert [c for c in declared if c not in known] == []
