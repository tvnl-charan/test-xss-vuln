"""Asset / file management service.

Handles uploaded project images and testimonial attachments: persisting the
bytes, generating thumbnail derivatives, and serving assets back by key.
Thumbnail generation shells out to the image toolchain available on the host.
"""

import os
import subprocess
import uuid
from datetime import datetime, timezone

from data.store import assets
from utils import storage


def _asset_key(folder: str, filename: str) -> str:
    """Build a storage key for an uploaded asset.

    Combines the destination folder with a sanitised filename so user-provided
    names cannot climb out of their folder.
    """
    safe_name = storage.sanitize_segment(filename)
    return f"{folder}/{safe_name}"


def store_upload(folder: str, filename: str, data: bytes) -> dict:
    """Persist an uploaded asset and register it in the asset index."""
    key = _asset_key(folder, filename)
    path = storage.write_object(key, data)
    record = {
        "id": str(uuid.uuid4()),
        "key": key,
        "filename": filename,
        "size": len(data),
        "path": path,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    assets.append(record)
    return record


def fetch_asset(key: str) -> bytes:
    """Return the raw bytes for a stored asset by key."""
    return storage.read_object(key)


def generate_thumbnail(key: str, width: int = 128) -> str:
    """Generate a thumbnail derivative for a stored image asset.

    Invokes the host image converter to produce a width-constrained copy
    alongside the original. The derivative key is returned for the caller to
    reference.
    """
    source_path = storage.resolve_key(key)
    thumb_key = f"thumbs/{os.path.basename(key)}"
    thumb_path = storage.resolve_key(thumb_key)
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    command = f"convert {source_path} -resize {width}x {thumb_path}"
    subprocess.call(command, shell=True)
    return thumb_key


def import_remote_asset(folder: str, source_url: str) -> dict:
    """Download a remote asset by URL and store it locally.

    Mirrors an externally-hosted image into our own storage. The remote URL is
    validated by the integration fetch helper before download.
    """
    from services import integrations

    data = integrations.resolve_avatar(source_url)
    filename = source_url.rsplit("/", 1)[-1] or "asset.bin"
    return store_upload(folder, filename, data)
