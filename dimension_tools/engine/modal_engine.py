"""Modal tool session state for dimension placement."""

from __future__ import annotations

from dataclasses import dataclass

from mathutils import Vector

from ..log import get_logger
from .snap_engine import SnapResult

_log = get_logger("engine.modal")

_session: "ModalSession | None" = None


@dataclass
class ModalSession:
    """Runtime state for an active linear dimension modal tool."""

    snap_result: SnapResult | None = None
    first_point: Vector | None = None
    second_point: Vector | None = None


def start_session() -> ModalSession:
    """Create and store a new modal session."""
    global _session
    _session = ModalSession()
    _log.debug("Modal session started")
    return _session


def end_session() -> None:
    """Clear the active modal session."""
    global _session
    _session = None
    _log.debug("Modal session ended")


def get_session() -> ModalSession | None:
    """Return the active modal session, if any."""
    return _session


def register() -> None:
    """Initialize the modal engine."""
    _log.debug("Modal engine registered")


def unregister() -> None:
    """Shut down the modal engine."""
    end_session()
    _log.debug("Modal engine unregistered")
