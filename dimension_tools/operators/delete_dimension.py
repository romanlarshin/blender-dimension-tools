import bpy
from ..draw import overlay


class DIMTOOLS_OT_delete_selected_dimension(bpy.types.Operator):
    bl_idname = "dimtools.delete_selected_dimension"
    bl_label = "Delete Selected Dimension"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.dimtools
        idx = settings.selected_index
        if 0 <= idx < len(settings.dimensions):
            settings.dimensions.remove(idx)
            settings.selected_index = min(idx, len(settings.dimensions) - 1)
            overlay.request_redraw(context)
            return {"FINISHED"}
        self.report({"WARNING"}, "No selected dimension")
        return {"CANCELLED"}


class DIMTOOLS_OT_delete_last_dimension(bpy.types.Operator):
    bl_idname = "dimtools.delete_last_dimension"
    bl_label = "Delete Last Dimension"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.dimtools
        if len(settings.dimensions) == 0:
            return {"CANCELLED"}
        settings.dimensions.remove(len(settings.dimensions) - 1)
        settings.selected_index = min(settings.selected_index, len(settings.dimensions) - 1)
        overlay.request_redraw(context)
        return {"FINISHED"}


class DIMTOOLS_OT_clear_dimensions(bpy.types.Operator):
    bl_idname = "dimtools.clear_dimensions"
    bl_label = "Clear Dimensions"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        settings = context.scene.dimtools
        settings.dimensions.clear()
        settings.selected_index = -1
        overlay.request_redraw(context)
        return {"FINISHED"}
