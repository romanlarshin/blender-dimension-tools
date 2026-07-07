"""Modal tool session state for dimension placement."""

from __future__ import annotations

from dataclasses import dataclass, field

from mathutils import Vector

from .offset_engine import OFFSET_AXIS_FREE
from .snap_engine import SnapResult

PHASE_SNAP = "SNAP"
PHASE_OFFSET = "OFFSET"


@dataclass
class ModalSession:
    """Runtime state for an active linear dimension modal tool."""

    snap_result: SnapResult | None = None
    first_point: Vector | None = None
    first_snap: SnapResult | None = None
    second_snap: SnapResult | None = None
    offset_vector: Vector = field(default_factory=lambda: Vector((0.0, 0.0, 0.0)))
    offset_axis_lock: str = OFFSET_AXIS_FREE
    offset_mode: bool = False

    @property
    def phase(self) -> str:
        if self.offset_mode:
            return PHASE_OFFSET
        return PHASE_SNAP


_session: ModalSession | None = None


def start_session() -> ModalSession:
    """Create and store a new modal session."""
    global _session
    _session = ModalSession()
    return _session


def end_session() -> None:
    """Clear the active modal session."""
    global _session
    _session = None


def get_session() -> ModalSession | None:
    """Return the active modal session, if any."""
    return _session


def reset_for_next_dimension(session: ModalSession) -> None:
    """Clear placement state so another dimension can be created."""
    session.snap_result = None
    session.first_point = None
    session.first_snap = None
    session.second_snap = None
    session.offset_vector = Vector((0.0, 0.0, 0.0))
    session.offset_axis_lock = OFFSET_AXIS_FREE
    session.offset_mode = False


def undo_last_point(session: ModalSession) -> bool:
    """Step back one click in the placement workflow. Returns True when state changed."""
    if session.offset_mode:
        session.second_snap = None
        session.offset_mode = False
        session.offset_vector = Vector((0.0, 0.0, 0.0))
        session.offset_axis_lock = OFFSET_AXIS_FREE
        if session.first_snap is not None:
            session.snap_result = session.first_snap
        return True
    if session.first_snap is not None:
        session.first_snap = None
        session.first_point = None
        session.snap_result = None
        return True
    return False


def status_text(session: ModalSession | None) -> str:
    """Return a user-facing status string for the current placement phase."""
    if session is None:
        return ""
    if session.offset_mode:
        lock_names = {
            OFFSET_AXIS_FREE: "Free",
            "X": "X",
            "Y": "Y",
            "Z": "Z",
        }
        lock_label = lock_names.get(session.offset_axis_lock, "Free")
        return (
            f"Dimension: place offset ({lock_label}) | "
            "X/Y/Z/F axis lock | Click confirm | Backspace undo | Esc exit"
        )
    if session.first_snap is None:
        return "Dimension: click first point | Esc exit"
    return "Dimension: click second point | Backspace undo | Esc exit"


def register() -> None:
    """Initialize the modal engine."""


def unregister() -> None:
    """Shut down the modal engine."""
    end_session()
