import bpy
from mathutils import Vector
from ..snap.snap_engine import find_snap
from ..utils.geometry import compute_dimension_geometry, closest_point_on_segment_2d, dist2d
from ..utils.viewport import world_to_screen, mouse_ray
from ..draw import overlay


class RuntimeState:
    def __init__(self):
        self.stage = 0
        self.p1 = None
        self.p2 = None
        self.snap = None
        self.preview = None
        self.magnet = None


def _dimension_from_mouse_plane(context, event, fallback):
    origin, direction = mouse_ray(context, event)
    # plane through fallback with normal = viewport direction, stable enough for placement
    normal = context.space_data.region_3d.view_rotation @ Vector((0, 0, -1))
    denom = direction.dot(normal)
    if abs(denom) < 1e-6:
        return fallback
    t = (Vector(fallback) - origin).dot(normal) / denom
    return origin + direction * t


def _find_chain_magnet(context, mouse_xy, settings):
    if settings.chain_magnet_radius <= 0:
        return None
    mouse = Vector(mouse_xy)
    best = None
    best_d = 1e9
    for i, dim in enumerate(settings.dimensions):
        a = world_to_screen(context, dim.q1)
        b = world_to_screen(context, dim.q2)
        if a is None or b is None:
            continue
        c, _t = closest_point_on_segment_2d(mouse, a, b)
        d = dist2d(mouse, c)
        if d < settings.chain_magnet_radius and d < best_d:
            best_d = d
            best = (Vector(dim.q1), Vector(dim.q2), i)
    return best


class DIMTOOLS_OT_linear_dimension(bpy.types.Operator):
    bl_idname = "dimtools.linear_dimension"
    bl_label = "Linear Dimension"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if context.area.type != "VIEW_3D":
            self.report({"ERROR"}, "Linear Dimension works only in 3D View")
            return {"CANCELLED"}
        self.rt = RuntimeState()
        overlay.set_runtime(self.rt)
        overlay.add_draw_handler()
        context.window_manager.modal_handler_add(self)
        self.report({"INFO"}, "Dimension mode: click P1, P2, offset. ESC to exit.")
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        settings = context.scene.dimtools
        mouse_xy = (event.mouse_region_x, event.mouse_region_y)

        if event.type in {"ESC", "RIGHTMOUSE"}:
            overlay.set_runtime(None)
            overlay.request_redraw(context)
            return {"CANCELLED"}

        if event.type in {"X", "Y", "Z", "F"} and event.value == "PRESS":
            settings.direction_mode = "FREE" if event.type == "F" else event.type

        if event.type == "MOUSEMOVE":
            self.rt.snap = find_snap(context, mouse_xy, settings.snap_radius)
            self._update_preview(context, event)
            overlay.request_redraw(context)
            return {"RUNNING_MODAL"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            snap = find_snap(context, mouse_xy, settings.snap_radius)
            if self.rt.stage in {0, 1}:
                if not snap.valid:
                    self.report({"WARNING"}, "No vertex/midpoint snap under cursor")
                    return {"RUNNING_MODAL"}
                if self.rt.stage == 0:
                    self.rt.p1 = snap.point.copy()
                    self.rt.stage = 1
                else:
                    self.rt.p2 = snap.point.copy()
                    self.rt.stage = 2
                self.rt.snap = snap
                self._update_preview(context, event)
                overlay.request_redraw(context)
                return {"RUNNING_MODAL"}

            if self.rt.stage == 2:
                self._commit_dimension(context, event)
                self.rt.stage = 0
                self.rt.p1 = None
                self.rt.p2 = None
                self.rt.preview = None
                self.rt.magnet = None
                overlay.request_redraw(context)
                return {"RUNNING_MODAL"}

        return {"RUNNING_MODAL"}

    def _update_preview(self, context, event):
        if self.rt.stage == 0:
            self.rt.preview = None
            return
        if self.rt.stage == 1 and self.rt.p1 and self.rt.snap and self.rt.snap.valid:
            self.rt.preview = (self.rt.p1, self.rt.p1, self.rt.snap.point, self.rt.snap.point)
            return
        if self.rt.stage == 2 and self.rt.p1 and self.rt.p2:
            settings = context.scene.dimtools
            third = _dimension_from_mouse_plane(context, event, (self.rt.p1 + self.rt.p2) * 0.5)
            magnet = _find_chain_magnet(context, (event.mouse_region_x, event.mouse_region_y), settings)
            self.rt.magnet = magnet
            if magnet:
                q1, q2, _ = compute_dimension_geometry(self.rt.p1, self.rt.p2, third, settings.direction_mode, magnet[0], magnet[1])
            else:
                q1, q2, _ = compute_dimension_geometry(self.rt.p1, self.rt.p2, third, settings.direction_mode)
            self.rt.preview = (self.rt.p1, q1, q2, self.rt.p2)

    def _commit_dimension(self, context, event):
        settings = context.scene.dimtools
        self._update_preview(context, event)
        if not self.rt.preview:
            return
        p1, q1, q2, p2 = self.rt.preview
        dim = settings.dimensions.add()
        idx = len(settings.dimensions) - 1
        dim.name = f"Dim {idx + 1:03d}"
        dim.p1 = p1
        dim.p2 = p2
        dim.q1 = q1
        dim.q2 = q2
        dim.text_pos = (q1 + q2) * 0.5
        dim.value = (Vector(p2) - Vector(p1)).length
        settings.selected_index = idx
        self.report({"INFO"}, f"Added {dim.name}: {dim.value:.{settings.decimals}f}{settings.unit_suffix}")
