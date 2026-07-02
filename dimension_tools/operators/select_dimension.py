import bpy
from mathutils import Vector
from ..utils.viewport import world_to_screen
from ..utils.geometry import closest_point_on_segment_2d, dist2d
from ..draw import overlay


def _hit_dimension(context, mouse_xy, settings, radius=18):
    mouse = Vector(mouse_xy)
    best = -1
    best_d = 1e9
    for i, dim in enumerate(settings.dimensions):
        pairs = [(dim.p1, dim.q1), (dim.q1, dim.q2), (dim.q2, dim.p2)]
        for a3, b3 in pairs:
            a = world_to_screen(context, a3)
            b = world_to_screen(context, b3)
            if a is None or b is None:
                continue
            c, _ = closest_point_on_segment_2d(mouse, a, b)
            d = dist2d(mouse, c)
            if d < radius and d < best_d:
                best = i
                best_d = d
    return best


class DIMTOOLS_OT_select_dimension(bpy.types.Operator):
    bl_idname = "dimtools.select_dimension"
    bl_label = "Select Dimension"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if context.area.type != "VIEW_3D":
            self.report({"ERROR"}, "Select Dimension works only in 3D View")
            return {"CANCELLED"}
        overlay.add_draw_handler()
        context.window_manager.modal_handler_add(self)
        self.report({"INFO"}, "Click a dimension to select. ESC to exit.")
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type in {"ESC", "RIGHTMOUSE"}:
            return {"CANCELLED"}
        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            settings = context.scene.dimtools
            idx = _hit_dimension(context, (event.mouse_region_x, event.mouse_region_y), settings)
            settings.selected_index = idx
            overlay.request_redraw(context)
            if idx >= 0:
                self.report({"INFO"}, f"Selected {settings.dimensions[idx].name}")
            else:
                self.report({"INFO"}, "No dimension selected")
            return {"FINISHED"}
        return {"RUNNING_MODAL"}
