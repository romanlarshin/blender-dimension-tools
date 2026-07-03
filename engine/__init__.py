"""Runtime engines — snap, chain attachment, and viewport drawing.

Coordinates interactive subsystems during modal tool use. The draw engine will
own the View3D draw handler and delegate primitive drawing to the overlay
package when rendering is implemented.
"""

from __future__ import annotations

from ..log import get_logger
from . import chain_engine, draw_engine, snap_engine

_log = get_logger("engine")

__all__ = (
    "chain_engine",
    "draw_engine",
    "snap_engine",
)


def register() -> None:
    """Register all engine subsystems."""
    snap_engine.register()
    chain_engine.register()
    draw_engine.register()
    _log.debug("Engine registered")


def unregister() -> None:
    """Unregister all engine subsystems."""
    draw_engine.unregister()
    chain_engine.unregister()
    snap_engine.unregister()
    _log.debug("Engine unregistered")
