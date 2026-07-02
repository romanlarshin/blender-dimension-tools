import bpy


class DIMTOOLS_UL_dimensions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        settings = context.scene.dimtools
        label = item.custom_text if item.custom_text else f"{item.name} — {item.value:.{settings.decimals}f}{settings.unit_suffix}"
        layout.label(text=label, icon="EMPTY_SINGLE_ARROW")


class DIMTOOLS_PT_panel(bpy.types.Panel):
    bl_label = "Dimension Tools"
    bl_idname = "DIMTOOLS_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dimensions"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.dimtools

        col = layout.column(align=True)
        col.operator("dimtools.linear_dimension", text="Linear Dimension", icon="EMPTY_SINGLE_ARROW")
        col.operator("dimtools.select_dimension", text="Select Dimension", icon="RESTRICT_SELECT_OFF")

        box = layout.box()
        box.label(text="Global Style")
        box.prop(settings, "text_size")
        box.prop(settings, "line_thickness")
        box.prop(settings, "arrow_size")
        box.prop(settings, "decimals")
        box.prop(settings, "unit_suffix")

        box = layout.box()
        box.label(text="Snapping / Chains")
        box.prop(settings, "snap_radius")
        box.prop(settings, "chain_magnet_radius")
        box.prop(settings, "direction_mode")
        box.label(text="Hotkeys: X/Y/Z lock, F free, Esc exit")

        box = layout.box()
        box.label(text="Dimensions")
        box.template_list("DIMTOOLS_UL_dimensions", "", settings, "dimensions", settings, "selected_index", rows=5)
        row = box.row(align=True)
        row.operator("dimtools.delete_selected_dimension", text="Delete Selected")
        row.operator("dimtools.delete_last_dimension", text="Delete Last")
        box.operator("dimtools.clear_dimensions", text="Clear All")
