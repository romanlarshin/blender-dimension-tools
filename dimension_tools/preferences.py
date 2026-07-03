"""Addon-wide preferences.

Global display and interaction defaults that apply across all scenes. Values
will be consumed by the draw engine and snap engine when those subsystems are
implemented.
"""

from __future__ import annotations

import bpy
from bpy.props import EnumProperty, FloatProperty, FloatVectorProperty, IntProperty

from .log import get_logger

_log = get_logger("preferences")


class DIMTOOLS_AddonPreferences(bpy.types.AddonPreferences):
    """User preferences for Dimension Tools, shown in Blender's Add-ons panel."""

    bl_idname = __package__

    text_size: IntProperty(
        name="Text Size",
        description="Global dimension label size in pixels",
        default=18,
        min=8,
        max=96,
    )

    arrow_size: FloatProperty(
        name="Arrow Size",
        description="Global arrowhead size in pixels",
        default=10.0,
        min=2.0,
        max=40.0,
    )

    line_width: FloatProperty(
        name="Line Width",
        description="Global dimension line width in pixels",
        default=1.5,
        min=1.0,
        max=12.0,
    )

    color: FloatVectorProperty(
        name="Color",
        description="Global dimension color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0, 1.0),
    )

    units: EnumProperty(
        name="Units",
        description="Display unit system for dimension labels",
        items=[
            ("SCENE", "Scene Units", "Use the scene unit system"),
            ("NONE", "Blender Units", "Display raw Blender units"),
        ],
        default="SCENE",
    )

    snap_radius: FloatProperty(
        name="Snap Radius",
        description="Screen-space radius for geometry snapping",
        default=16.0,
        min=4.0,
        max=80.0,
    )

    def draw(self, context: bpy.types.Context) -> None:
        """Draw the preferences panel in Blender's Add-ons settings."""
        layout = self.layout
        layout.prop(self, "text_size")
        layout.prop(self, "arrow_size")
        layout.prop(self, "line_width")
        layout.prop(self, "color")
        layout.prop(self, "units")
        layout.prop(self, "snap_radius")


classes = (DIMTOOLS_AddonPreferences,)


def register() -> None:
    """Register addon preference classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    _log.debug("Preferences registered")


def unregister() -> None:
    """Unregister addon preference classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    _log.debug("Preferences unregistered")
