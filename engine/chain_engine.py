"""Chain attachment engine.

Will detect when a new dimension should attach to an existing dimension line
(CAD-style chains). Works in screen space and returns attachment data for the
core layer to consume.
"""

from __future__ import annotations

from ..log import get_logger

_log = get_logger("engine.chain")


def register() -> None:
    """Initialize the chain engine.

    Intentionally empty during bootstrap so the addon loads before chain
    attachment is implemented.
    """
    _log.debug("Chain engine registered")


def unregister() -> None:
    """Shut down the chain engine."""
    _log.debug("Chain engine unregistered")
