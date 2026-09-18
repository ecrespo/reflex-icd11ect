"""Tests for the event payloads."""

from __future__ import annotations

from reflex_icd11ect import BrowserContent, SelectedEntity


def test_selected_entity_from_a_payload():
    entity = SelectedEntity.from_payload(
        {
            "i_no": "1",
            "code": "5A11",
            "title": "Type 2 diabetes mellitus",
            "foundation_uri": "http://id.who.int/icd/entity/1127435854",
            "search_query": "diabetes",
            "unexpected": "ignored",
        }
    )
    assert entity.code == "5A11"
    assert entity.search_query == "diabetes"
    assert entity.foundation_uri.endswith("1127435854")
    assert entity.best_match_text == ""
    assert not hasattr(entity, "unexpected")


def test_selected_entity_tolerates_nothing():
    assert SelectedEntity.from_payload(None).code == ""
    assert SelectedEntity.from_payload({}).title == ""


def test_postcoordination_is_detected():
    assert SelectedEntity.from_payload({"code": "2C25.Z&XA2UD3"}).is_postcoordinated
    assert not SelectedEntity.from_payload({"code": "1B11"}).is_postcoordinated


def test_browser_content_from_a_payload():
    content = BrowserContent.from_payload({"i_no": "b", "code": "1B11", "uri": "u"})
    assert (content.i_no, content.code, content.uri) == ("b", "1B11", "u")
