"""Addon-wide preferences.

Global display and interaction defaults that apply across all scenes.
"""

from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
)

from .log import get_logger

_log = get_logger("preferences")


class DIMTOOLS_AddonPreferences(bpy.types.AddonPreferences):
    """User preferences for Dimension Tools."""

    bl_idname = __package__

    text_size: IntProperty(
        name="Text Size",
        description="Dimension label size in pixels",
        default=16,
        min=8,
        max=96,
    )

    arrow_size: FloatProperty(
        name="Arrow Size",
        description="Arrowhead size in pixels",
        default=12.0,
        min=2.0,
        max=48.0,
    )

    line_width: FloatProperty(
        name="Line Width",
        description="Dimension line width in pixels",
        default=2.0,
        min=1.0,
        max=12.0,
    )

    color: FloatVectorProperty(
        name="Color",
        description="Primary dimension color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.05, 0.05, 0.05, 1.0),
    )

    extension_alpha: FloatProperty(
        name="Extension Line Opacity",
        description="Opacity multiplier for extension lines",
        default=0.65,
        min=0.1,
        max=1.0,
    )

    selected_color: FloatVectorProperty(
        name="Selected Color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.15, 0.45, 0.95, 1.0),
    )

    hover_color: FloatVectorProperty(
        name="Hover Color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.35, 0.75, 1.0, 1.0),
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

    precision: IntProperty(
        name="Precision",
        description="Decimal places for dimension labels",
        default=2,
        min=0,
        max=6,
    )

    font_id: IntProperty(
        name="Font",
        description="Font identifier used by blf for dimension labels",
        default=0,
        min=0,
        max=10,
    )

    snap_radius: FloatProperty(
        name="Snap Radius",
        description="Screen-space radius for geometry snapping in pixels",
        default=20.0,
        min=4.0,
        max=80.0,
    )

    snap_vertex: BoolProperty(name="Snap to Vertices", default=True)
    snap_edge_mid: BoolProperty(name="Snap to Edge Midpoints", default=True)
    snap_edge: BoolProperty(name="Snap to Edges", default=True)
    snap_face: BoolProperty(name="Snap to Face Centers", default=True)
    snap_grid: BoolProperty(name="Snap to Grid", default=True)
    snap_origin: BoolProperty(name="Snap to Object Origins", default=True)

    show_live_preview_text: BoolProperty(
        name="Live Measurement Preview",
        description="Show measurement text while placing a dimension",
        default=True,
    )

    def draw(self, context: bpy.types.Context) -> None:
        """Draw the preferences panel in Blender's Add-ons settings."""
        layout = self.layout
        box = layout.box()
        box.label(text="Display")
        box.prop(self, "text_size")
        box.prop(self, "arrow_size")
        box.prop(self, "line_width")
        box.prop(self, "color")
        box.prop(self, "extension_alpha")
        box.prop(self, "selected_color")
        box.prop(self, "hover_color")
        box.prop(self, "units")
        box.prop(self, "precision")
        box.prop(self, "font_id")
        box.prop(self, "show_live_preview_text")

        box = layout.box()
        box.label(text="Snapping")
        box.prop(self, "snap_radius")
        col = box.column(align=True)
        col.prop(self, "snap_vertex")
        col.prop(self, "snap_edge_mid")
        col.prop(self, "snap_edge")
        col.prop(self, "snap_face")
        col.prop(self, "snap_grid")
        col.prop(self, "snap_origin")


classes = (DIMTOOLS_AddonPreferences,)


def register() -> None:
    """Register addon preference classes."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    """Unregister addon preference classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
