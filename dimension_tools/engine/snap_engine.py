"""Snap engine — cursor-to-geometry snapping with spatial acceleration."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector
from mathutils.kdtree import KDTree

from ..preferences import DIMTOOLS_AddonPreferences
from ..utils import viewport as viewport_utils

SNAP_VERTEX = "VERTEX"
SNAP_EDGE_MID = "EDGE_MID"
SNAP_EDGE = "EDGE"
SNAP_FACE = "FACE"
SNAP_GRID = "GRID"
SNAP_ORIGIN = "ORIGIN"

KDTree_THRESHOLD = 256


@dataclass(frozen=True)
class SnapResult:
    """Nearest geometry target under the cursor."""

    world_co: Vector
    snap_type: str = SNAP_VERTEX
    object_name: str = ""
    element_index: int = -1
    element_index_b: int = -1
    local_co: Vector | None = None
    edge_param: float = 0.0


@dataclass(frozen=True)
class SnapSettings:
    """Active snap configuration."""

    radius: float
    vertex: bool = True
    edge_mid: bool = True
    edge: bool = True
    face: bool = True
    grid: bool = True
    origin: bool = True


def get_snap_settings(context: bpy.types.Context) -> SnapSettings:
    """Build snap settings from addon preferences."""
    prefs = context.preferences.addons[DIMTOOLS_AddonPreferences.bl_idname].preferences
    return SnapSettings(
        radius=float(prefs.snap_radius),
        vertex=prefs.snap_vertex,
        edge_mid=prefs.snap_edge_mid,
        edge=prefs.snap_edge,
        face=prefs.snap_face,
        grid=prefs.snap_grid,
        origin=prefs.snap_origin,
    )


@contextmanager
def view3d_snap_context(context: bpy.types.Context):
    """Yield a context whose region and region_data refer to the 3D View window."""
    area = context.area
    if area is None or area.type != "VIEW_3D":
        yield context
        return

    window_region = next((region for region in area.regions if region.type == "WINDOW"), None)
    space = (
        context.space_data
        if context.space_data is not None and context.space_data.type == "VIEW_3D"
        else area.spaces.active
    )
    rv3d = space.region_3d if space is not None else None

    if window_region is None or rv3d is None:
        yield context
        return

    with context.temp_override(
        area=area,
        region=window_region,
        space_data=space,
        region_data=rv3d,
    ):
        yield context


def _iter_view3d_mesh_objects(context: bpy.types.Context) -> Iterator[bpy.types.Object]:
    """Yield mesh objects visible in the active 3D Viewport."""
    if context.region is None or context.region_data is None:
        return
    if context.space_data is None or context.space_data.type != "VIEW_3D":
        return
    for obj in context.visible_objects:
        if obj.type != "MESH" or obj.display_type == "WIRE":
            continue
        yield obj


def _screen_distance(region, rv3d, mouse_co: Vector, world_co: Vector) -> float | None:
    screen_co = view3d_utils.location_3d_to_region_2d(region, rv3d, world_co)
    if screen_co is None:
        return None
    return (mouse_co - screen_co).length


def _closest_point_on_segment(point: Vector, start: Vector, end: Vector) -> tuple[Vector, float]:
    segment = end - start
    length_sq = segment.length_squared
    if length_sq < 1e-12:
        return start.copy(), 0.0
    t = max(0.0, min(1.0, (point - start).dot(segment) / length_sq))
    return start + segment * t, t


def _object_near_mouse(region, rv3d, mouse_co: Vector, obj: bpy.types.Object, margin: float) -> bool:
    for corner in obj.bound_box:
        world_co = obj.matrix_world @ Vector(corner)
        dist = _screen_distance(region, rv3d, mouse_co, world_co)
        if dist is not None and dist <= margin:
            return True
    return False


def _consider_best(
    best: SnapResult | None,
    best_dist: float,
    dist: float | None,
    result: SnapResult,
) -> tuple[SnapResult | None, float]:
    if dist is not None and dist < best_dist:
        return result, dist
    return best, best_dist


def _snap_grid(context: bpy.types.Context, event: bpy.types.Event, snap_radius: float) -> SnapResult | None:
    region = context.region
    rv3d = context.region_data
    space = context.space_data
    if region is None or rv3d is None or space is None:
        return None

    mouse_co = Vector((event.mouse_region_x, event.mouse_region_y))
    depth_location = rv3d.view_matrix.inverted().translation
    world_co = view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_co, depth_location)
    if world_co is None:
        return None

    grid_scale = max(space.overlay.grid_scale, 1e-6)
    snapped = Vector(tuple(round(world_co[i] / grid_scale) * grid_scale for i in range(3)))
    dist = _screen_distance(region, rv3d, mouse_co, snapped)
    if dist is None or dist >= snap_radius:
        return None
    return SnapResult(world_co=snapped, snap_type=SNAP_GRID, local_co=snapped.copy())


def _snap_vertices_brute(
    region,
    rv3d,
    mouse_co: Vector,
    matrix,
    mesh,
    obj_name: str,
    best: SnapResult | None,
    best_dist: float,
) -> tuple[SnapResult | None, float]:
    for vert_index, vert in enumerate(mesh.vertices):
        world_co = matrix @ vert.co
        best, best_dist = _consider_best(
            best,
            best_dist,
            _screen_distance(region, rv3d, mouse_co, world_co),
            SnapResult(
                world_co=world_co,
                snap_type=SNAP_VERTEX,
                object_name=obj_name,
                element_index=vert_index,
                local_co=vert.co.copy(),
            ),
        )
    return best, best_dist


def _snap_vertices_kdtree(
    context: bpy.types.Context,
    region,
    rv3d,
    mouse_co: Vector,
    matrix,
    mesh,
    obj_name: str,
    best: SnapResult | None,
    best_dist: float,
) -> tuple[SnapResult | None, float]:
    mouse_world = view3d_utils.region_2d_to_location_3d(
        region,
        rv3d,
        mouse_co,
        matrix @ mesh.vertices[0].co if mesh.vertices else matrix.translation,
    )
    if mouse_world is None:
        return _snap_vertices_brute(region, rv3d, mouse_co, matrix, mesh, obj_name, best, best_dist)

    world_radius = viewport_utils.pixel_size_to_world(context, mouse_world, best_dist)
    kd = KDTree(len(mesh.vertices))
    for vert_index, vert in enumerate(mesh.vertices):
        kd.insert(matrix @ vert.co, vert_index)
    kd.balance()

    for world_co, vert_index, _dist in kd.find_range(mouse_world, world_radius):
        vert = mesh.vertices[vert_index]
        best, best_dist = _consider_best(
            best,
            best_dist,
            _screen_distance(region, rv3d, mouse_co, world_co),
            SnapResult(
                world_co=world_co,
                snap_type=SNAP_VERTEX,
                object_name=obj_name,
                element_index=vert_index,
                local_co=vert.co.copy(),
            ),
        )
    return best, best_dist


def find_nearest_snap(
    context: bpy.types.Context,
    event: bpy.types.Event,
    snap_radius: float | None = None,
    *,
    settings: SnapSettings | None = None,
) -> SnapResult | None:
    """Return the closest enabled snap target within the snap radius."""
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return None
    if context.space_data is None or context.space_data.type != "VIEW_3D":
        return None

    cfg = settings or get_snap_settings(context)
    radius = snap_radius if snap_radius is not None else cfg.radius

    mouse_co = Vector((event.mouse_region_x, event.mouse_region_y))
    depsgraph = context.evaluated_depsgraph_get()
    best: SnapResult | None = None
    best_dist = radius
    object_margin = radius * 4.0

    if cfg.origin:
        for obj in context.visible_objects:
            if obj.display_type == "WIRE":
                continue
            if not _object_near_mouse(region, rv3d, mouse_co, obj, object_margin):
                continue
            origin = obj.matrix_world.translation
            best, best_dist = _consider_best(
                best,
                best_dist,
                _screen_distance(region, rv3d, mouse_co, origin),
                SnapResult(world_co=origin.copy(), snap_type=SNAP_ORIGIN, object_name=obj.name),
            )

    for obj in _iter_view3d_mesh_objects(context):
        if not _object_near_mouse(region, rv3d, mouse_co, obj, object_margin):
            continue

        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.data
        if mesh is None:
            continue

        matrix = eval_obj.matrix_world
        matrix_inv = matrix.inverted()

        if cfg.vertex:
            if len(mesh.vertices) >= KDTree_THRESHOLD:
                best, best_dist = _snap_vertices_kdtree(
                    context, region, rv3d, mouse_co, matrix, mesh, obj.name, best, best_dist,
                )
            else:
                best, best_dist = _snap_vertices_brute(
                    region, rv3d, mouse_co, matrix, mesh, obj.name, best, best_dist,
                )

        if cfg.edge_mid or cfg.edge:
            for edge_index, edge in enumerate(mesh.edges):
                v0 = matrix @ mesh.vertices[edge.vertices[0]].co
                v1 = matrix @ mesh.vertices[edge.vertices[1]].co

                if cfg.edge_mid:
                    midpoint = (v0 + v1) * 0.5
                    best, best_dist = _consider_best(
                        best,
                        best_dist,
                        _screen_distance(region, rv3d, mouse_co, midpoint),
                        SnapResult(
                            world_co=midpoint,
                            snap_type=SNAP_EDGE_MID,
                            object_name=obj.name,
                            element_index=edge_index,
                            element_index_b=edge.vertices[1],
                            local_co=(mesh.vertices[edge.vertices[0]].co + mesh.vertices[edge.vertices[1]].co) * 0.5,
                        ),
                    )

                if cfg.edge:
                    mouse_world = view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_co, (v0 + v1) * 0.5)
                    if mouse_world is not None:
                        closest, edge_param = _closest_point_on_segment(mouse_world, v0, v1)
                        best, best_dist = _consider_best(
                            best,
                            best_dist,
                            _screen_distance(region, rv3d, mouse_co, closest),
                            SnapResult(
                                world_co=closest,
                                snap_type=SNAP_EDGE,
                                object_name=obj.name,
                                element_index=edge_index,
                                element_index_b=edge.vertices[1],
                                local_co=matrix_inv @ closest,
                                edge_param=edge_param,
                            ),
                        )

        if cfg.face:
            for face_index, face in enumerate(mesh.polygons):
                center = matrix @ face.center
                best, best_dist = _consider_best(
                    best,
                    best_dist,
                    _screen_distance(region, rv3d, mouse_co, center),
                    SnapResult(
                        world_co=center,
                        snap_type=SNAP_FACE,
                        object_name=obj.name,
                        element_index=face_index,
                        local_co=matrix_inv @ center,
                    ),
                )

    if cfg.grid:
        grid_result = _snap_grid(context, event, radius)
        if grid_result is not None:
            best, best_dist = _consider_best(
                best,
                best_dist,
                _screen_distance(region, rv3d, mouse_co, grid_result.world_co),
                grid_result,
            )

    return best


def find_nearest_vertex(
    context: bpy.types.Context,
    event: bpy.types.Event,
    snap_radius: float,
) -> SnapResult | None:
    """Return the closest mesh vertex within ``snap_radius`` pixels of the mouse."""
    cfg = get_snap_settings(context)
    vertex_only = SnapSettings(
        radius=snap_radius,
        vertex=True,
        edge_mid=False,
        edge=False,
        face=False,
        grid=False,
        origin=False,
    )
    return find_nearest_snap(context, event, snap_radius, settings=vertex_only)


def copy_snap_result(snap: SnapResult) -> SnapResult:
    """Return a copy of a snap result with duplicated vectors."""
    return SnapResult(
        world_co=snap.world_co.copy(),
        snap_type=snap.snap_type,
        object_name=snap.object_name,
        element_index=snap.element_index,
        element_index_b=snap.element_index_b,
        local_co=snap.local_co.copy() if snap.local_co is not None else None,
        edge_param=snap.edge_param,
    )


def register() -> None:
    """Initialize the snap engine."""


def unregister() -> None:
    """Shut down the snap engine."""
