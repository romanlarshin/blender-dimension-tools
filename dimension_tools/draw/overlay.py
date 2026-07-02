import bpy
import blf
import gpu
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from ..utils.viewport import world_to_screen

_draw_handler = None
_runtime = None


def set_runtime(runtime):
    global _runtime
    _runtime = runtime


def add_draw_handler():
    global _draw_handler
    if _draw_handler is None:
        _draw_handler = bpy.types.SpaceView3D.draw_handler_add(draw_callback, (), "WINDOW", "POST_PIXEL")


def remove_draw_handler():
    global _draw_handler
    if _draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, "WINDOW")
        _draw_handler = None


def request_redraw(context):
    if context.area:
        context.area.tag_redraw()


def _line_2d(points, color=(1, 1, 1, 1), width=1.5):
    if len(points) < 2:
        return
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINES", {"pos": points})
    gpu.state.blend_set("ALPHA")
    try:
        gpu.state.line_width_set(width)
    except Exception:
        pass
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def _text_2d(x, y, text, size=18, color=(0, 0, 0, 1)):
    font_id = 0
    blf.size(font_id, size)
    blf.color(font_id, *color)
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)


def _draw_point(context, p, color, size=8):
    sp = world_to_screen(context, p)
    if sp is None:
        return
    x, y = sp.x, sp.y
    _line_2d([(x - size, y), (x + size, y), (x, y - size), (x, y + size)], color, 2)


def _draw_dimension(context, dim, settings, selected=False):
    pts = [dim.p1, dim.q1, dim.q2, dim.p2]
    s = [world_to_screen(context, p) for p in pts]
    if any(p is None for p in s):
        return
    color = (0.05, 0.9, 1.0, 1.0) if selected else (0.02, 0.02, 0.02, 1.0)
    w = settings.line_thickness + (1.5 if selected else 0.0)
    _line_2d([(s[0].x, s[0].y), (s[1].x, s[1].y), (s[2].x, s[2].y), (s[3].x, s[3].y)], color, w)
    # arrow ticks, simple and stable in screen space
    for a, b in [(s[1], s[2]), (s[2], s[1])]:
        d = (b - a)
        if d.length == 0:
            continue
        d.normalize()
        n = Vector((-d.y, d.x))
        L = 10
        _line_2d([(a.x, a.y), (a.x + (-d.x + n.x) * L, a.y + (-d.y + n.y) * L),
                  (a.x, a.y), (a.x + (-d.x - n.x) * L, a.y + (-d.y - n.y) * L)], color, w)
    text_screen = world_to_screen(context, dim.text_pos)
    if text_screen:
        label = dim.custom_text if dim.custom_text else f"{dim.value:.{settings.decimals}f}{settings.unit_suffix}"
        _text_2d(text_screen.x + 4, text_screen.y + 4, label, settings.text_size, color)


def draw_callback():
    context = bpy.context
    if not hasattr(context.scene, "dimtools"):
        return
    settings = context.scene.dimtools
    for i, dim in enumerate(settings.dimensions):
        _draw_dimension(context, dim, settings, i == settings.selected_index)
    if _runtime:
        if _runtime.snap and _runtime.snap.valid:
            _draw_point(context, _runtime.snap.point, (1, 0.8, 0, 1), 7)
        if _runtime.p1:
            _draw_point(context, _runtime.p1, (0, 0.4, 1, 1), 8)
        if _runtime.p2:
            _draw_point(context, _runtime.p2, (0, 1, 0.2, 1), 8)
        if _runtime.preview:
            p1, q1, q2, p2 = _runtime.preview
            class Dummy: pass
            d = Dummy(); d.p1=p1; d.q1=q1; d.q2=q2; d.p2=p2; d.text_pos=(q1+q2)*0.5; d.value=(p2-p1).length; d.custom_text=""
            _draw_dimension(context, d, settings, False)
