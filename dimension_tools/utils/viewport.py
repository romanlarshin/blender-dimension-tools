from mathutils import Vector
from bpy_extras import view3d_utils


def region_data(context):
    area = context.area
    region = context.region
    rv3d = context.space_data.region_3d
    return region, rv3d


def world_to_screen(context, point):
    region, rv3d = region_data(context)
    p = view3d_utils.location_3d_to_region_2d(region, rv3d, Vector(point))
    return p


def mouse_ray(context, event):
    region, rv3d = region_data(context)
    coord = (event.mouse_region_x, event.mouse_region_y)
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    return origin, direction
