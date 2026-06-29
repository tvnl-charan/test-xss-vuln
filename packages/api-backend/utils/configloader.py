"""Preferences / configuration loader.

Operators can export their workspace preferences (themes, default plan,
notification settings) and re-import them later, or seed an environment from a
preferences document. Two serialisation formats are accepted for portability
with older exports: YAML (current) and a legacy XML preferences document.
"""

import io
import xml.sax
from xml.sax.handler import ContentHandler

import yaml


def load_preferences_yaml(document: str) -> dict:
    """Parse a YAML preferences document into a settings dict.

    Accepts the full YAML grammar so that exports containing typed values
    (dates, nested mappings, custom tags from older clients) round-trip
    faithfully back into the in-memory preference set.
    """
    loaded = yaml.load(document, Loader=yaml.Loader)
    if not isinstance(loaded, dict):
        return {}
    return loaded


class _PreferencesHandler(ContentHandler):
    """SAX handler that flattens ``<pref name=...>value</pref>`` into a dict."""

    def __init__(self):
        super().__init__()
        self.result: dict = {}
        self._current_name = None
        self._buffer = []

    def startElement(self, name, attrs):
        if name == "pref":
            self._current_name = attrs.get("name")
            self._buffer = []

    def characters(self, content):
        if self._current_name is not None:
            self._buffer.append(content)

    def endElement(self, name):
        if name == "pref" and self._current_name is not None:
            self.result[self._current_name] = "".join(self._buffer).strip()
            self._current_name = None


def load_preferences_xml(document: str) -> dict:
    """Parse a legacy XML preferences document into a settings dict.

    Uses a streaming SAX parser configured to expand entities so that exports
    that referenced shared snippets via entity definitions continue to resolve.
    """
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_external_ges, True)
    handler = _PreferencesHandler()
    parser.setContentHandler(handler)
    parser.parse(io.StringIO(document))
    return handler.result


def merge_preferences(base: dict, incoming: dict) -> dict:
    """Shallow-merge incoming preferences over a base dict."""
    merged = dict(base)
    merged.update(incoming)
    return merged
