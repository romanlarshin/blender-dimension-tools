"""Centralized logging for the Dimension Tools addon.

Blender routes Python logging to its system console. This module configures a
single stream handler on the addon root logger so repeated enable/disable
cycles do not accumulate duplicate handlers.
"""

from __future__ import annotations

import logging

_ROOT_LOGGER_NAME = "dimtools"
_handler: logging.Handler | None = None


def get_logger(name: str = "") -> logging.Logger:
    """Return a logger under the ``dimtools`` namespace.

    Args:
        name: Optional submodule suffix (for example ``"engine.draw"``).

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    if name:
        return logging.getLogger(f"{_ROOT_LOGGER_NAME}.{name}")
    return logging.getLogger(_ROOT_LOGGER_NAME)


def configure(level: int = logging.INFO) -> None:
    """Attach a console handler to the addon root logger once.

    Args:
        level: Logging level for the addon root logger.
    """
    global _handler

    logger = get_logger()
    logger.setLevel(level)

    if _handler is not None:
        return

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
    )
    logger.addHandler(handler)
    _handler = handler


def shutdown() -> None:
    """Remove the addon stream handler during :func:`unregister`."""
    global _handler

    logger = get_logger()
    if _handler is None:
        return

    logger.removeHandler(_handler)
    _handler.close()
    _handler = None
