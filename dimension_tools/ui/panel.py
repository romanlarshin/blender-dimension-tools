"""Main sidebar panel."""

from __future__ import annotations

import bpy

from ..core import selection as selection_core
from ..core.dimension import get_scene_state
from ..preferences import DIMTOOLS_AddonPreferences


class DIMTOOLS_PT_main(bpy.types.Panel):
    """Dimension Tools panel in the 3D Viewport sidebar."""

    bl_label = "Dimension Tools"
    bl_idname = "DIMTOOLS_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dimensions"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        prefs = context.preferences.addons[DIMTOOLS_AddonPreferences.bl_idname].preferences
        scene_state = get_scene_state(context.scene)
        selected_count = len(selection_core.get_selected(context.scene))

        col = layout.column(align=True)
        col.scale_y = 1.2
        col.operator("dimtools.start_linear_dimension", icon="DRIVER_DISTANCE")
        col.operator("dimtools.select_dimension", icon="RESTRICT_SELECT_OFF")

        row = col.row(align=True)
        row.operator("dimtools.delete_dimension", icon="TRASH")
        row.enabled = selected_count > 0

        row = layout.row(align=True)
        row.operator("dimtools.select_all_dimensions", text="All")
        row.operator("dimtools.deselect_all_dimensions", text="None")

        edit = layout.column(align=True)
        edit.enabled = selected_count > 0
        row = edit.row(align=True)
        row.operator("dimtools.move_dimension_text", text="Move Text", icon="FONT_DATA")
        row.operator("dimtools.move_dimension_offset", text="Move Offset", icon="ARROW_LEFTRIGHT")
        edit.operator("dimtools.set_dimension_text", icon="TEXT")
        edit.operator("dimtools.toggle_dimension_visibility", icon="HIDE_OFF")

        layout.separator()
        layout.label(text=f"{len(scene_state.dimensions)} dimensions | {selected_count} selected")

        box = layout.box()
        box.label(text="Style", icon="MODIFIER")
        box.prop(prefs, "text_size")
        box.prop(prefs, "arrow_size")
        box.prop(prefs, "line_width")
        box.prop(prefs, "color")
        box.prop(prefs, "extension_alpha")
        box.prop(prefs, "units")
        box.prop(prefs, "precision")
        box.prop(prefs, "show_live_preview_text")

        box = layout.box()
        box.label(text="Snapping", icon="SNAP_VERTEX")
        box.prop(prefs, "snap_radius")
        col = box.column(align=True)
        col.prop(prefs, "snap_vertex", toggle=True)
        col.prop(prefs, "snap_edge_mid", toggle=True)
        col.prop(prefs, "snap_edge", toggle=True)
        col.prop(prefs, "snap_face", toggle=True)
        col.prop(prefs, "snap_grid", toggle=True)
        col.prop(prefs, "snap_origin", toggle=True)


class DIMTOOLS_PT_dimension_list(bpy.types.Panel):
    """Scrollable list of scene dimensions."""

    bl_label = "Dimension List"
    bl_idname = "DIMTOOLS_PT_dimension_list"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dimensions"
    bl_parent_id = "DIMTOOLS_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        dimensions = get_scene_state(context.scene).dimensions
        if not dimensions:
            layout.label(text="No dimensions", icon="INFO")
            return

        for item in dimensions:
            row = layout.row(align=True)
            icon = "RESTRICT_VIEW_OFF" if item.visible else "RESTRICT_VIEW_ON"
            sub = row.row(align=True)
            sub.active = item.visible
            op = sub.operator(
                "dimtools.dimension_list_action",
                text=item.text_override or f"Dimension {item.uid[:6]}",
                depress=item.selected,
                icon="RADIOBUT_ON" if item.selected else "RADIOBUT_OFF",
            )
            op.uid = item.uid
            op.action = "SELECT"
            vis = row.operator("dimtools.dimension_list_action", text="", icon=icon)
            vis.uid = item.uid
            vis.action = "TOGGLE_VISIBLE"
