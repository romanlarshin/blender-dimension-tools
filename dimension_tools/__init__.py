"""Dimension Tools — CAD-like viewport dimensions for Blender 5.1+."""

bl_info = {
    "name": "Dimension Tools",
    "author": "Dimension Tools Contributors",
    "version": (1, 0, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Dimensions",
    "description": "Professional CAD-like linear dimensions drawn as GPU viewport overlays",
    "category": "3D View",
    "doc_url": "",
    "tracker_url": "",
}

from . import core, engine, log, operators, overlay, preferences, properties, ui

_log = log.get_logger()


def register() -> None:
    """Register all addon classes and runtime subsystems."""
    log.configure()
    _log.info("Registering Dimension Tools v%s", ".".join(str(v) for v in bl_info["version"]))

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
    log.shutdown()
