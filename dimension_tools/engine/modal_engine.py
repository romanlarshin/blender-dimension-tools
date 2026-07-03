"""Modal tool session state for dimension placement."""

from __future__ import annotations

from ..log import get_logger

_log = get_logger("engine.modal")


def register() -> None:
    """Initialize the modal engine.

    Intentionally empty during bootstrap so the addon loads before modal
    session management is implemented.
    """
    _log.debug("Modal engine registered")


def unregister() -> None:
    """Shut down the modal engine."""
    _log.debug("Modal engine unregistered")
