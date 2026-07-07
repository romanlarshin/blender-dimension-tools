"""Draw engine — viewport overlay orchestration.

Persistent dimension drawing will be added here later. Modal debug drawing is
currently owned by the start-dimension operator instance.
"""

from __future__ import annotations

from ..log import get_logger

_log = get_logger("engine.draw")


def register() -> None:
    """Register the draw engine."""
    _log.debug("Draw engine registered")


def unregister() -> None:
    """Unregister the draw engine."""
    _log.debug("Draw engine unregistered")
