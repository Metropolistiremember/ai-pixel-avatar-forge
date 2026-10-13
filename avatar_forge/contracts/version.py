"""Plugin API version + compatibility check."""
from __future__ import annotations

PLUGIN_API_VERSION = "3.1.0"


def is_compatible(declared: str) -> bool:
    """Major must match exactly; minor must be <= host minor."""
    try:
        host_major, host_minor, _ = (int(p) for p in PLUGIN_API_VERSION.split("."))
        d_major, d_minor, _ = (int(p) for p in declared.split("."))
    except ValueError:
        return False
    return d_major == host_major and d_minor <= host_minor