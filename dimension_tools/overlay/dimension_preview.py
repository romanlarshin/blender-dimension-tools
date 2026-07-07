"""GPU drawing for linear dimension rendering."""

from __future__ import annotations

import bpy
from mathutils import Vector

from ..core import dimension as dimension_core
from ..engine.offset_engine import build_dimension_layout, format_measured_distance
from ..gpu.batch import LineBatch, TriangleBatch
from ..preferences import DIMTOOLS_AddonPreferences
from ..utils import viewport as viewport_utils
from . import arrows, text

SELECTED_LINE_WIDTH_SCALE = 1.6


def _get_prefs(context: bpy.types.Context) -> DIMTOOLS_AddonPreferences:
    return context.preferences.addons[DIMTOOLS_AddonPreferences.bl_idname].preferences


def _with_alpha(color: tuple[float, float, float, float], scale: float):
    return (color[0], color[1], color[2], color[3] * scale)


def _style_color(
    context: bpy.types.Context,
    item,
    prefs: DIMTOOLS_AddonPreferences,
    *,
    hovered: bool,
) -> tuple[float, float, float, float]:
    if item is not None and item.selected:
        return tuple(prefs.selected_color)
    if hovered:
        return tuple(prefs.hover_color)
    if item is not None:
        return dimension_core.get_effective_color(context, item)
    return tuple(prefs.color)


def draw_scene_dimensions(
    context: bpy.types.Context,
    *,
    hover_uid: str | None = None,
) -> None:
    """Draw all visible scene dimension geometry (POST_VIEW)."""
    from ..core.store import iter_visible_dimensions

    rv3d = context.region_data
    if rv3d is None:
        return

    prefs = _get_prefs(context)
    default_ext = LineBatch()
    default_dim = LineBatch()
    default_arrows = TriangleBatch()
    selected_ext = LineBatch()
    selected_dim = LineBatch()
    selected_arrows = TriangleBatch()
    hover_ext = LineBatch()
    hover_dim = LineBatch()
    hover_arrows = TriangleBatch()

    base_color = tuple(prefs.color)
    ext_alpha = prefs.extension_alpha

    for item in iter_visible_dimensions(context):
        layout = dimension_core.build_layout(context, item, rv3d)
        if layout is None:
            continue

        hovered = hover_uid is not None and item.uid == hover_uid
        if item.selected:
            ext_batch, dim_batch, arrow_batch = selected_ext, selected_dim, selected_arrows
        elif hovered:
            ext_batch, dim_batch, arrow_batch = hover_ext, hover_dim, hover_arrows
        else:
            ext_batch, dim_batch, arrow_batch = default_ext, default_dim, default_arrows

        ext_batch.add_segment(layout.point_a, layout.dim_a)
        ext_batch.add_segment(layout.point_b, layout.dim_b)
        dim_batch.add_segment(layout.dim_a, layout.dim_b)

        midpoint = (layout.dim_a + layout.dim_b) * 0.5
        arrow_size = viewport_utils.pixel_size_to_world(context, midpoint, prefs.arrow_size)
        arrows.collect_arrow_pair(layout.dim_a, layout.dim_b, rv3d, arrow_size, arrow_batch)

    width = prefs.line_width
    selected_width = width * SELECTED_LINE_WIDTH_SCALE

    default_ext.draw(_with_alpha(base_color, ext_alpha), line_width=width)
    default_dim.draw(base_color, line_width=width)
    default_arrows.draw(base_color)

    selected_color = tuple(prefs.selected_color)
    selected_ext.draw(_with_alpha(selected_color, ext_alpha), line_width=selected_width)
    selected_dim.draw(selected_color, line_width=selected_width)
    selected_arrows.draw(selected_color)

    hover_color = tuple(prefs.hover_color)
    hover_ext.draw(_with_alpha(hover_color, ext_alpha), line_width=width)
    hover_dim.draw(hover_color, line_width=width)
    hover_arrows.draw(hover_color)

    for item in iter_visible_dimensions(context):
        if not item.use_custom_color or item.selected or (hover_uid and item.uid == hover_uid):
            continue
        layout = dimension_core.build_layout(context, item, rv3d)
        if layout is None:
            continue
        color = dimension_core.get_effective_color(context, item)
        custom_ext = LineBatch()
        custom_dim = LineBatch()
        custom_arrows = TriangleBatch()
        custom_ext.add_segment(layout.point_a, layout.dim_a)
        custom_ext.add_segment(layout.point_b, layout.dim_b)
        custom_dim.add_segment(layout.dim_a, layout.dim_b)
        midpoint = (layout.dim_a + layout.dim_b) * 0.5
        arrow_size = viewport_utils.pixel_size_to_world(context, midpoint, prefs.arrow_size)
        arrows.collect_arrow_pair(layout.dim_a, layout.dim_b, rv3d, arrow_size, custom_arrows)
        custom_ext.draw(_with_alpha(color, ext_alpha), line_width=width)
        custom_dim.draw(color, line_width=width)
        custom_arrows.draw(color)


def draw_scene_labels(
    context: bpy.types.Context,
    *,
    hover_uid: str | None = None,
) -> None:
    """Draw measurement labels for all visible dimensions (POST_PIXEL)."""
    from ..core.store import iter_visible_dimensions

    rv3d = context.region_data
    if rv3d is None:
        return

    prefs = _get_prefs(context)

    for item in iter_visible_dimensions(context):
        layout = dimension_core.build_layout(context, item, rv3d)
        if layout is None:
            continue

        hovered = hover_uid is not None and item.uid == hover_uid
        color = _style_color(context, item, prefs, hovered=hovered)
        label = dimension_core.get_label_text(context, item, layout.measured_distance)
        text_pos = dimension_core.get_text_world_position(layout, item)
        text.draw_world_label(
            context,
            label,
            text_pos,
            font_id=prefs.font_id,
            size=prefs.text_size,
            color=color,
        )


def draw_offset_preview(
    context: bpy.types.Context,
    point_a: Vector,
    point_b: Vector,
    offset_vector: Vector,
) -> None:
    """Draw the offset-stage preview geometry (POST_VIEW)."""
    rv3d = context.region_data
    if rv3d is None:
        return

    layout = build_dimension_layout(point_a, point_b, offset_vector)
    if layout is None:
        return

    prefs = _get_prefs(context)
    color = tuple(prefs.color)
    ext_batch = LineBatch()
    dim_batch = LineBatch()
    arrow_batch = TriangleBatch()

    ext_batch.add_segment(layout.point_a, layout.dim_a)
    ext_batch.add_segment(layout.point_b, layout.dim_b)
    dim_batch.add_segment(layout.dim_a, layout.dim_b)

    midpoint = (layout.dim_a + layout.dim_b) * 0.5
    arrow_size = viewport_utils.pixel_size_to_world(context, midpoint, prefs.arrow_size)
    arrows.collect_arrow_pair(layout.dim_a, layout.dim_b, rv3d, arrow_size, arrow_batch)

    ext_batch.draw(_with_alpha(color, prefs.extension_alpha), line_width=prefs.line_width)
    dim_batch.draw(color, line_width=prefs.line_width)
    arrow_batch.draw(color)


def draw_offset_preview_label(
    context: bpy.types.Context,
    point_a: Vector,
    point_b: Vector,
    offset_vector: Vector,
) -> None:
    """Draw the offset-stage measurement label (POST_PIXEL)."""
    prefs = _get_prefs(context)
    if not prefs.show_live_preview_text:
        return

    layout = build_dimension_layout(point_a, point_b, offset_vector)
    if layout is None:
        return

    label = format_measured_distance(
        context,
        layout.measured_distance,
        units=prefs.units,
        precision=prefs.precision,
    )
    text.draw_world_label(
        context,
        label,
        layout.text_center,
        font_id=prefs.font_id,
        size=prefs.text_size,
        color=tuple(prefs.color),
    )
