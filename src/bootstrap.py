"""Initialisation SSL — redirige vers startup.py (compatibilite)."""

import src.startup  # noqa: F401

from src.startup import ca_bundle_path, project_root, ssl_context

__all__ = ["ca_bundle_path", "project_root", "ssl_context"]
