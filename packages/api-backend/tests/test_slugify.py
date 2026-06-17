"""Unit tests for the slugify helper."""

from utils.slugify import slugify


def test_basic_lowercases_and_hyphenates():
    assert slugify("Hello World") == "hello-world"


def test_collapses_non_word_runs():
    assert slugify("a---b__c!!d") == "a-b-c-d"


def test_strips_leading_and_trailing_separators():
    assert slugify("  --Hello--  ") == "hello"


class TestSlugifyEdgeCases:
    def test_empty_string(self):
        assert slugify("") == ""

    def test_only_symbols(self):
        assert slugify("!!!") == ""

    def test_unicode_is_dropped(self):
        assert slugify("café crème") == "caf-cr-me"
