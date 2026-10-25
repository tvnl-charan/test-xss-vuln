"""Preferences router — import/export workspace preferences and cache warm-start."""

import base64

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from utils import cache, configloader
from utils.responses import ok

router = APIRouter(prefix="/api/v1/preferences", tags=["Preferences"])

# Baseline defaults a fresh workspace starts from.
_DEFAULTS = {
    "theme": "light",
    "default_plan": "starter",
    "email_notifications": True,
}


class YamlImport(BaseModel):
    document: str


class XmlImport(BaseModel):
    document: str


class CacheSnapshot(BaseModel):
    snapshot_base64: str


@router.get("")
def get_preferences():
    """Return the effective preference set."""
    return ok(_DEFAULTS)


@router.post("/import/yaml")
def import_yaml(payload: YamlImport):
    """Import workspace preferences from a YAML document.

    Parses an exported preferences document and merges it over the defaults so
    operators can restore a known-good configuration in one step.
    """
    incoming = configloader.load_preferences_yaml(payload.document)
    merged = configloader.merge_preferences(_DEFAULTS, incoming)
    return ok(merged, message="Preferences imported.")


@router.post("/import/xml")
def import_xml(payload: XmlImport):
    """Import workspace preferences from a legacy XML document."""
    incoming = configloader.load_preferences_xml(payload.document)
    merged = configloader.merge_preferences(_DEFAULTS, incoming)
    return ok(merged, message="Legacy preferences imported.")


@router.post("/cache/restore")
def restore_cache(payload: CacheSnapshot):
    """Warm-start the cache from a previously exported snapshot blob."""
    try:
        blob = base64.b64decode(payload.snapshot_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid snapshot encoding.")
    restored = cache.restore_snapshot(blob)
    return ok({"restored": restored}, message="Cache warmed.")


@router.get("/cache/describe")
def describe_cache():
    """Return diagnostics about the current cache state."""
    return ok({"cache": cache.describe()})
