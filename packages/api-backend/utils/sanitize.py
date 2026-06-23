"""
Input sanitization utilities.

Provides HTML escaping and path validation for user inputs.
"""

import os
import re
from html import escape as html_escape


def sanitize_html(text: str) -> str:
    """Escape HTML special characters to prevent XSS."""
    return html_escape(text, quote=True)


def sanitize_filename(filename: str) -> str:
    """Remove directory traversal patterns from filenames."""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\-.]', '_', filename)
    return filename


def validate_path(path: str, base_dir: str) -> str:
    """Validate that a path stays within the base directory.

    Returns the resolved absolute path if safe, raises ValueError otherwise.
    """
    resolved = os.path.realpath(os.path.join(base_dir, path))
    if not resolved.startswith(os.path.realpath(base_dir)):
        raise ValueError(f"Path traversal detected: {path}")
    return resolved


def sanitize_sql_identifier(identifier: str) -> str:
    """Remove non-alphanumeric characters from SQL identifiers."""
    return re.sub(r'[^a-zA-Z0-9_]', '', identifier)
