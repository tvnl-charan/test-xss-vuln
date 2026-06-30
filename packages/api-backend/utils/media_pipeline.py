"""Media ingestion and rendition pipeline.

Coordinates turning an externally-sourced or uploaded media asset into a
delivery-ready rendition: fetching source bytes, transcoding to a target
profile, and locating stored renditions for download.
"""

from utils import remote_loader, transcoder, asset_locator

_DELIVERY_PROFILES = ("web", "thumb", "print")


def ingest_avatar(source_url: str, member_id: str) -> dict:
    """Fetch a member's avatar from a remote URL and stage it for delivery."""
    raw = normalize_and_fetch(source_url)
    return {"member_id": member_id, "bytes": len(raw), "source": source_url}


def normalize_and_fetch(source_url: str) -> bytes:
    """Trim a source URL and pull its bytes through the remote loader."""
    target = source_url.strip()
    return remote_loader.load_resource(target)


def build_transcode_job(filename: str, profile: str) -> str:
    """Validate the delivery profile and run the transcode pipeline."""
    profile = profile if profile in _DELIVERY_PROFILES else "web"
    return transcoder.prepare_pipeline(filename, profile)


def locate_rendition(key: str) -> bytes:
    """Resolve a rendition storage key to its bytes for download."""
    return asset_locator.resolve_path(key)
