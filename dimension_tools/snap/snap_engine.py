import bpy
from mathutils import Vector
from ..utils.viewport import world_to_screen
from ..utils.geometry import dist2d


class SnapResult:
    def __init__(self, point=None, label="", screen=None, distance=1e9):
        self.point = point
        self.label = label
        self.screen = screen
        self.distance = distance

    @property
    def valid(self):
        return self.point is not None


def iter_mesh_snap_points(context):
    depsgraph = context.evaluated_depsgraph_get()
    for obj in context.visible_objects:
        if obj.type != "MESH":
            continue
        try:
            eval_obj = obj.evaluated_get(depsgraph)
            mesh = eval_obj.to_mesh()
        except Exception:
            continue
        if mesh is None:
            continue
        mw = obj.matrix_world
        verts = [mw @ v.co for v in mesh.vertices]
        for v in verts:
            yield v, "Vertex"
        for e in mesh.edges:
            try:
                yield (verts[e.vertices[0]] + verts[e.vertices[1]]) * 0.5, "Midpoint"
            except Exception:
                pass
        try:
            eval_obj.to_mesh_clear()
        except Exception:
            pass


def find_snap(context, mouse_xy, radius):
    mouse = Vector(mouse_xy)
    best = SnapResult()
    for point, label in iter_mesh_snap_points(context):
        screen = world_to_screen(context, point)
        if screen is None:
            continue
        d = dist2d(mouse, screen)
        if d < radius and d < best.distance:
            best = SnapResult(Vector(point), label, screen, d)
    return best
