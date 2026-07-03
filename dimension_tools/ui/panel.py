"""Main sidebar panel.

Exposes global style settings in the 3D Viewport sidebar. Tool operators will
be added here as they are implemented.
"""

from __future__ import annotations

import bpy

from ..preferences import DIMTOOLS_AddonPreferences


class DIMTOOLS_PT_main(bpy.types.Panel):
    """Dimension Tools panel in the 3D Viewport sidebar."""

    bl_label = "Dimension Tools"
    bl_idname = "DIMTOOLS_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dimensions"

    def draw(self, context: bpy.types.Context) -> None:
        """Draw the panel layout."""
        layout = self.layout
        prefs = context.preferences.addons[
            DIMTOOLS_AddonPreferences.bl_idname
        ].preferences

        layout.operator(
            "dimtools.start_linear_dimension",
            text="Start Linear Dimension",
            icon="DRIVER_DISTANCE",
        )
        layout.label(text="Linear Dimension Mode (ESC to Exit)", icon="INFO")
        layout.separator()

        layout.label(text="Global Style", icon="MODIFIER")
        box = layout.box()
        box.prop(prefs, "text_size")
        box.prop(prefs, "arrow_size")
        box.prop(prefs, "line_width")
        box.prop(prefs, "color")
        box.prop(prefs, "units")
