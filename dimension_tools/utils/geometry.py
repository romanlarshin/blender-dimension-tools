from mathutils import Vector


def dist2d(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return (dx * dx + dy * dy) ** 0.5


def closest_point_on_segment_2d(p, a, b):
    ab = b - a
    denom = ab.length_squared
    if denom == 0:
        return a, 0.0
    t = max(0.0, min(1.0, (p - a).dot(ab) / denom))
    return a + ab * t, t


def axis_vector(mode):
    if mode == "X":
        return Vector((1, 0, 0))
    if mode == "Y":
        return Vector((0, 1, 0))
    if mode == "Z":
        return Vector((0, 0, 1))
    return None


def compute_dimension_geometry(p1, p2, third_point, direction_mode="FREE", magnet_q1=None, magnet_q2=None):
    p1 = Vector(p1)
    p2 = Vector(p2)
    third_point = Vector(third_point)
    mid = (p1 + p2) * 0.5

    if magnet_q1 is not None and magnet_q2 is not None:
        qmid = (Vector(magnet_q1) + Vector(magnet_q2)) * 0.5
        offset = qmid - mid
    else:
        axis = axis_vector(direction_mode)
        raw = third_point - mid
        if axis is not None:
            offset = axis * raw.dot(axis)
            if offset.length < 1e-6:
                offset = axis * 0.25
        else:
            measure = p2 - p1
            if measure.length > 1e-6:
                mdir = measure.normalized()
                offset = raw - mdir * raw.dot(mdir)
                if offset.length < 1e-6:
                    offset = raw
            else:
                offset = raw

    q1 = p1 + offset
    q2 = p2 + offset
    text_pos = (q1 + q2) * 0.5
    return q1, q2, text_pos
