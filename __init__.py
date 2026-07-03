"""Dimension Tools — CAD-like viewport dimensions for Blender 5.1+.

Entry point: registers all subsystems in dependency order and exposes ``bl_info``.
"""

bl_info = {
    "name": "Dimension Tools",
    "author": "Dimension Tools Contributors",
    "version": (0, 1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Dimensions",
    "description": "CAD-like dimension annotations drawn in the viewport",
    "category": "3D View",
    "doc_url": "",
    "tracker_url": "",
}

from . import core, engine, log, operators, overlay, preferences, properties, ui

_log = log.get_logger()


def register() -> None:
    """Register all addon classes and runtime subsystems."""
    log.configure()
    _log.info("Registering Dimension Tools")

    preferences.register()
    properties.register()
    core.register()
    overlay.register()
    engine.register()
    operators.register()
    ui.register()

    _log.info("Dimension Tools registered")


def unregister() -> None:
    """Unregister all addon classes and runtime subsystems."""
    _log.info("Unregistering Dimension Tools")

    ui.unregister()
    operators.unregister()
    engine.unregister()
    overlay.unregister()
    core.unregister()
    properties.unregister()
    preferences.unregister()
    _log.info("Dimension Tools unregistered")
    log.shutdown()
