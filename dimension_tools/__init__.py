bl_info = {
    "name": "Dimension Tools",
    "author": "Roman Larshin + GPT",
    "version": (0, 3, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Dimensions",
    "description": "CAD-like linear dimensions with vertex snapping and overlay drawing",
    "category": "3D View",
}

import bpy
import json
import math
from mathutils import Vector
from bpy_extras import view3d_utils
import gpu
from gpu_extras.batch import batch_for_shader
import blf

_draw_handle = None
_active_tool = None


def _safe_load_dimensions(scene):
    raw = getattr(scene, "dimtools_dimensions_json", "")
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def _safe_save_dimensions(scene, dims):
    scene.dimtools_dimensions_json = json.dumps(dims)


def _vec_to_list(v):
    return [float(v.x), float(v.y), float(v.z)]


def _list_to_vec(a):
    return Vector((float(a[0]), float(a[1]), float(a[2])))


def _distance_2d(a, b):
    if a is None or b is None:
        return 1e18
    dx = a.x - b.x
    dy = a.y - b.y
    return math.sqrt(dx * dx + dy * dy)


def _project(context, world_pos):
    region = context.region
    rv3d = context.region_data
    if not region or not rv3d:
        return None
    return view3d_utils.location_3d_to_region_2d(region, rv3d, world_pos)


def _mouse_vec(event):
    return Vector((event.mouse_region_x, event.mouse_region_y))


def _closest_point_on_segment_3d(p, a, b):
    ab = b - a
    denom = ab.dot(ab)
    if denom <= 1e-12:
        return a.copy()
    t = (p - a).dot(ab) / denom
    t = max(0.0, min(1.0, t))
    return a + ab * t


def _closest_screen_distance_to_segment(context, mouse, a3, b3):
    a2 = _project(context, a3)
    b2 = _project(context, b3)
    if a2 is None or b2 is None:
        return 1e18
    ab = b2 - a2
    denom = ab.dot(ab)
    if denom <= 1e-9:
        return _distance_2d(mouse, a2)
    t = (mouse - a2).dot(ab) / denom
    t = max(0.0, min(1.0, t))
    q = a2 + ab * t
    return _distance_2d(mouse, q)


def _format_length(context, length):
    unit = context.scene.unit_settings
    # For now display Blender scene units. Blender internal units are meters in Metric workflows.
    if unit.system == 'METRIC':
        return f"{length:.2f} m"
    return f"{length:.3f}"


def _iter_mesh_snap_points(context):
    depsgraph = context.evaluated_depsgraph_get()
    mode_obj = context.object
    for obj in context.visible_objects:
        if obj.type != 'MESH':
            continue
        try:
            # Use evaluated mesh in object mode. In edit mode this still gives usable base coords for v0.3.
            eval_obj = obj.evaluated_get(depsgraph)
            mesh = eval_obj.to_mesh()
        except Exception:
            mesh = obj.data
        mw = obj.matrix_world
        for v in mesh.vertices:
            yield mw @ v.co, "Vertex"
        for e in mesh.edges:
            try:
                a = mesh.vertices[e.vertices[0]].co
                b = mesh.vertices[e.vertices[1]].co
                yield mw @ ((a + b) * 0.5), "Midpoint"
            except Exception:
                pass
        try:
            if obj.type == 'MESH' and 'eval_obj' in locals():
                eval_obj.to_mesh_clear()
        except Exception:
            pass


def find_snap_point(context, event):
    settings = context.scene.dimtools_settings
    mouse = _mouse_vec(event)
    best = None
    best_dist = float(settings.snap_radius)
    for world, label in _iter_mesh_snap_points(context):
        p2 = _project(context, world)
        if p2 is None:
            continue
        d = _distance_2d(mouse, p2)
        if d < best_dist:
            best_dist = d
            best = {"world": world, "screen": p2, "label": label, "dist": d}
    return best


def _calculate_dimension_geometry(context, p1, p2, mouse_world, event):
    settings = context.scene.dimtools_settings
    mode = settings.direction_mode
    measure = p2 - p1
    if measure.length <= 1e-9:
        return None
    measure_dir = measure.normalized()
    mid = (p1 + p2) * 0.5

    offset_vec = mouse_world - _closest_point_on_segment_3d(mouse_world, p1, p2)
    offset_vec = offset_vec - measure_dir * offset_vec.dot(measure_dir)

    if mode == 'X':
        axis = Vector((1, 0, 0))
        offset_vec = axis * (mouse_world - mid).dot(axis)
    elif mode == 'Y':
        axis = Vector((0, 1, 0))
        offset_vec = axis * (mouse_world - mid).dot(axis)
    elif mode == 'Z':
        axis = Vector((0, 0, 1))
        offset_vec = axis * (mouse_world - mid).dot(axis)
    elif mode == 'RADIAL':
        obj = context.object
        if obj:
            center = obj.matrix_world.translation
        else:
            center = Vector((0, 0, 0))
        radial = mid - center
        if radial.length > 1e-9:
            radial.normalize()
            offset_vec = radial * (mouse_world - mid).dot(radial)

    # Chain magnet: if mouse is close to an existing baseline, use that baseline level.
    if settings.chain_magnet:
        mouse = _mouse_vec(event)
        best_dim = None
        best_d = float(settings.chain_magnet_radius)
        for dim in _safe_load_dimensions(context.scene):
            try:
                d1 = _list_to_vec(dim["d1"])
                d2 = _list_to_vec(dim["d2"])
                screen_d = _closest_screen_distance_to_segment(context, mouse, d1, d2)
                if screen_d < best_d:
                    best_d = screen_d
                    best_dim = (d1, d2)
            except Exception:
                pass
        if best_dim is not None:
            old_mid = (best_dim[0] + best_dim[1]) * 0.5
            offset_vec = old_mid - _closest_point_on_segment_3d(old_mid, p1, p2)
            offset_vec = offset_vec - measure_dir * offset_vec.dot(measure_dir)

    if offset_vec.length <= 1e-7:
        # Small default visible offset in view direction fallback.
        offset_vec = Vector((0, 0, 0.25))

    d1 = p1 + offset_vec
    d2 = p2 + offset_vec
    return d1, d2


def _draw_line_2d(points, color=(1, 1, 1, 1), width=1.0):
    if len(points) < 2:
        return
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(width)
    batch = batch_for_shader(shader, 'LINES', {"pos": points})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')


def _draw_polyline_segments(points2d, color, width):
    pts = []
    for a, b in points2d:
        if a is not None and b is not None:
            pts.append((a.x, a.y))
            pts.append((b.x, b.y))
    _draw_line_2d(pts, color, width)


def _draw_circle_2d(center, radius, color, width=2.0, segments=32):
    if center is None:
        return
    pts = []
    for i in range(segments):
        a1 = 2 * math.pi * i / segments
        a2 = 2 * math.pi * (i + 1) / segments
        pts.append((center.x + math.cos(a1) * radius, center.y + math.sin(a1) * radius))
        pts.append((center.x + math.cos(a2) * radius, center.y + math.sin(a2) * radius))
    _draw_line_2d(pts, color, width)


def _draw_text_2d(x, y, text, size, color=(1, 1, 1, 1)):
    font_id = 0
    blf.size(font_id, int(size))
    blf.color(font_id, color[0], color[1], color[2], color[3])
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)


def _draw_dimension(context, dim, selected=False):
    settings = context.scene.dimtools_settings
    try:
        p1 = _list_to_vec(dim["p1"])
        p2 = _list_to_vec(dim["p2"])
        d1 = _list_to_vec(dim["d1"])
        d2 = _list_to_vec(dim["d2"])
    except Exception:
        return

    p1s, p2s, d1s, d2s = [_project(context, p) for p in (p1, p2, d1, d2)]
    color = (0.1, 0.85, 1.0, 1.0) if selected else (0.0, 0.0, 0.0, 1.0)
    width = float(settings.line_width) + (1.5 if selected else 0.0)
    _draw_polyline_segments([(p1s, d1s), (p2s, d2s), (d1s, d2s)], color, width)

    # arrowheads in screen space
    if d1s and d2s:
        v = d2s - d1s
        if v.length > 1e-6:
            v.normalize()
            perp = Vector((-v.y, v.x))
            s = float(settings.arrow_size)
            for base, sign in ((d1s, 1), (d2s, -1)):
                tip = base
                back = base + v * s * sign
                a = back + perp * s * 0.45
                b = back - perp * s * 0.45
                _draw_line_2d([(tip.x, tip.y), (a.x, a.y), (tip.x, tip.y), (b.x, b.y)], color, width)

        mid = (d1s + d2s) * 0.5
        text = dim.get("text") or _format_length(context, (p2 - p1).length)
        _draw_text_2d(mid.x + 5, mid.y + 5, text, settings.text_size, color)


def draw_callback():
    context = bpy.context
    if not context or not context.scene:
        return
    try:
        selected = int(context.scene.dimtools_selected_index)
    except Exception:
        selected = -1
    for i, dim in enumerate(_safe_load_dimensions(context.scene)):
        _draw_dimension(context, dim, selected=(i == selected))

    tool = _active_tool
    if tool and getattr(tool, "context_area", None) == context.area:
        try:
            tool.draw_preview(context)
        except Exception:
            pass


class DIMTOOLS_PG_settings(bpy.types.PropertyGroup):
    text_size: bpy.props.IntProperty(name="Text Size", default=18, min=8, max=96)
    line_width: bpy.props.FloatProperty(name="Line Width", default=2.0, min=1.0, max=10.0)
    arrow_size: bpy.props.FloatProperty(name="Arrow Size", default=10.0, min=2.0, max=40.0)
    snap_radius: bpy.props.FloatProperty(name="Snap Radius", default=14.0, min=4.0, max=50.0)
    chain_magnet: bpy.props.BoolProperty(name="Chain Magnet", default=True)
    chain_magnet_radius: bpy.props.FloatProperty(name="Magnet Radius", default=24.0, min=4.0, max=80.0)
    direction_mode: bpy.props.EnumProperty(
        name="Direction",
        items=[
            ('FREE', "Free", "Free offset"),
            ('X', "X", "Offset along world X"),
            ('Y', "Y", "Offset along world Y"),
            ('Z', "Z", "Offset along world Z"),
            ('RADIAL', "Radial", "Offset radially from active object center"),
        ],
        default='FREE',
    )


class DIMTOOLS_OT_linear_dimension(bpy.types.Operator):
    bl_idname = "dimtools.linear_dimension"
    bl_label = "Linear Dimension"
    bl_description = "Create linear dimensions. Stays active until Esc"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        global _active_tool
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Run this in a 3D View")
            return {'CANCELLED'}
        self.stage = 0
        self.p1 = None
        self.p2 = None
        self.snap = None
        self.mouse_world = None
        self.context_area = context.area
        _active_tool = self
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set("Dimension Tool: click P1, P2, offset. ESC exits. X/Y/Z/F/R set direction")
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global _active_tool
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            context.area.header_text_set(None)
            if _active_tool is self:
                _active_tool = None
            context.area.tag_redraw()
            return {'CANCELLED'}

        settings = context.scene.dimtools_settings
        if event.type == 'X' and event.value == 'PRESS':
            settings.direction_mode = 'X'
        elif event.type == 'Y' and event.value == 'PRESS':
            settings.direction_mode = 'Y'
        elif event.type == 'Z' and event.value == 'PRESS':
            settings.direction_mode = 'Z'
        elif event.type == 'F' and event.value == 'PRESS':
            settings.direction_mode = 'FREE'
        elif event.type == 'R' and event.value == 'PRESS':
            settings.direction_mode = 'RADIAL'

        if event.type == 'MOUSEMOVE':
            self.snap = find_snap_point(context, event)
            depth = self.p2 or self.p1 or (context.object.matrix_world.translation if context.object else Vector((0, 0, 0)))
            self.mouse_world = view3d_utils.region_2d_to_location_3d(
                context.region, context.region_data, (event.mouse_region_x, event.mouse_region_y), depth
            )
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.stage == 0:
                if self.snap:
                    self.p1 = self.snap["world"].copy()
                    self.stage = 1
            elif self.stage == 1:
                if self.snap:
                    self.p2 = self.snap["world"].copy()
                    if (self.p2 - self.p1).length > 1e-7:
                        self.stage = 2
            elif self.stage == 2:
                if self.mouse_world is not None:
                    geom = _calculate_dimension_geometry(context, self.p1, self.p2, self.mouse_world, event)
                    if geom:
                        d1, d2 = geom
                        dims = _safe_load_dimensions(context.scene)
                        dims.append({
                            "p1": _vec_to_list(self.p1),
                            "p2": _vec_to_list(self.p2),
                            "d1": _vec_to_list(d1),
                            "d2": _vec_to_list(d2),
                            "text": "",
                        })
                        _safe_save_dimensions(context.scene, dims)
                        context.scene.dimtools_selected_index = len(dims) - 1
                    self.stage = 0
                    self.p1 = None
                    self.p2 = None
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def draw_preview(self, context):
        settings = context.scene.dimtools_settings
        if self.snap:
            _draw_circle_2d(self.snap["screen"], 7, (1.0, 0.8, 0.0, 1.0), 2.0)
            _draw_text_2d(self.snap["screen"].x + 10, self.snap["screen"].y + 10, self.snap["label"], 12, (1, 0.8, 0, 1))
        if self.p1:
            p1s = _project(context, self.p1)
            _draw_circle_2d(p1s, 8, (0.0, 0.7, 1.0, 1.0), 2.0)
        if self.p2:
            p2s = _project(context, self.p2)
            _draw_circle_2d(p2s, 8, (0.0, 1.0, 0.4, 1.0), 2.0)
        if self.stage == 1 and self.p1 and self.snap:
            p1s = _project(context, self.p1)
            p2s = self.snap["screen"]
            _draw_line_2d([(p1s.x, p1s.y), (p2s.x, p2s.y)], (0, 0.8, 1, 1), settings.line_width)
        if self.stage == 2 and self.p1 and self.p2 and self.mouse_world is not None:
            class E: pass
            # fake event is not needed for preview except mouse coords; use current window mouse not available here.
            # draw free preview without magnet in callback; actual placement still uses magnet.
            measure = self.p2 - self.p1
            if measure.length > 1e-7:
                md = measure.normalized()
                offset = self.mouse_world - _closest_point_on_segment_3d(self.mouse_world, self.p1, self.p2)
                offset = offset - md * offset.dot(md)
                d1 = self.p1 + offset
                d2 = self.p2 + offset
                temp = {"p1": _vec_to_list(self.p1), "p2": _vec_to_list(self.p2), "d1": _vec_to_list(d1), "d2": _vec_to_list(d2), "text": ""}
                _draw_dimension(context, temp, selected=True)


class DIMTOOLS_OT_select_dimension(bpy.types.Operator):
    bl_idname = "dimtools.select_dimension"
    bl_label = "Select Dimension"
    bl_description = "Click a dimension line to select it"

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set("Select Dimension: click a dimension line. ESC exits")
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            context.area.header_text_set(None)
            return {'CANCELLED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            mouse = _mouse_vec(event)
            best_i = -1
            best_d = 18.0
            for i, dim in enumerate(_safe_load_dimensions(context.scene)):
                try:
                    d1 = _list_to_vec(dim["d1"])
                    d2 = _list_to_vec(dim["d2"])
                    d = _closest_screen_distance_to_segment(context, mouse, d1, d2)
                    if d < best_d:
                        best_d = d
                        best_i = i
                except Exception:
                    pass
            context.scene.dimtools_selected_index = best_i
            context.area.header_text_set(None)
            context.area.tag_redraw()
            return {'FINISHED'}
        return {'RUNNING_MODAL'}


class DIMTOOLS_OT_delete_selected(bpy.types.Operator):
    bl_idname = "dimtools.delete_selected"
    bl_label = "Delete Selected Dimension"

    def execute(self, context):
        dims = _safe_load_dimensions(context.scene)
        idx = int(context.scene.dimtools_selected_index)
        if 0 <= idx < len(dims):
            dims.pop(idx)
            _safe_save_dimensions(context.scene, dims)
            context.scene.dimtools_selected_index = min(idx, len(dims) - 1)
        return {'FINISHED'}


class DIMTOOLS_OT_delete_last(bpy.types.Operator):
    bl_idname = "dimtools.delete_last"
    bl_label = "Delete Last Dimension"

    def execute(self, context):
        dims = _safe_load_dimensions(context.scene)
        if dims:
            dims.pop()
            _safe_save_dimensions(context.scene, dims)
            context.scene.dimtools_selected_index = len(dims) - 1
        return {'FINISHED'}


class DIMTOOLS_OT_clear_dimensions(bpy.types.Operator):
    bl_idname = "dimtools.clear_dimensions"
    bl_label = "Clear All Dimensions"

    def execute(self, context):
        _safe_save_dimensions(context.scene, [])
        context.scene.dimtools_selected_index = -1
        return {'FINISHED'}


class DIMTOOLS_PT_panel(bpy.types.Panel):
    bl_label = "Dimension Tools"
    bl_idname = "DIMTOOLS_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dimensions"

    def draw(self, context):
        layout = self.layout
        s = context.scene.dimtools_settings
        dims = _safe_load_dimensions(context.scene)
        layout.operator("dimtools.linear_dimension", icon='DRIVER_DISTANCE')
        layout.operator("dimtools.select_dimension", icon='RESTRICT_SELECT_OFF')
        layout.separator()
        layout.prop(s, "direction_mode")
        layout.prop(s, "chain_magnet")
        if s.chain_magnet:
            layout.prop(s, "chain_magnet_radius")
        layout.prop(s, "snap_radius")
        layout.prop(s, "text_size")
        layout.prop(s, "line_width")
        layout.prop(s, "arrow_size")
        layout.separator()
        layout.label(text=f"Dimensions: {len(dims)}")
        layout.prop(context.scene, "dimtools_selected_index", text="Selected")
        row = layout.row(align=True)
        row.operator("dimtools.delete_selected", icon='X')
        row.operator("dimtools.delete_last", icon='LOOP_BACK')
        layout.operator("dimtools.clear_dimensions", icon='TRASH')
        layout.separator()
        layout.label(text="Hotkeys while active:")
        layout.label(text="X/Y/Z axis, F free, R radial")
        layout.label(text="Esc exits")


classes = (
    DIMTOOLS_PG_settings,
    DIMTOOLS_OT_linear_dimension,
    DIMTOOLS_OT_select_dimension,
    DIMTOOLS_OT_delete_selected,
    DIMTOOLS_OT_delete_last,
    DIMTOOLS_OT_clear_dimensions,
    DIMTOOLS_PT_panel,
)


def register():
    global _draw_handle
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.dimtools_settings = bpy.props.PointerProperty(type=DIMTOOLS_PG_settings)
    bpy.types.Scene.dimtools_dimensions_json = bpy.props.StringProperty(name="Dimension Data", default="[]")
    bpy.types.Scene.dimtools_selected_index = bpy.props.IntProperty(name="Selected Dimension", default=-1)
    if _draw_handle is None:
        _draw_handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback, (), 'WINDOW', 'POST_PIXEL')


def unregister():
    global _draw_handle, _active_tool
    _active_tool = None
    if _draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        _draw_handle = None
    for prop in ("dimtools_selected_index", "dimtools_dimensions_json", "dimtools_settings"):
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
