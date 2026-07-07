"""Scene-attached RNA data for persistent dimensions.

Defines PropertyGroups stored on :class:`bpy.types.Scene`. Only typed RNA
properties belong here — no Python objects, GPU batches, or arbitrary
collections.
"""

from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

from .log import get_logger

_log = get_logger("properties")

SNAP_ANCHOR_ITEMS = [
    ("NONE", "None", "Fixed world coordinates"),
    ("VERTEX", "Vertex", "Mesh vertex"),
    ("EDGE_MID", "Edge Midpoint", "Edge midpoint"),
    ("EDGE", "Edge", "Nearest point on edge"),
    ("FACE", "Face Center", "Face center"),
    ("GRID", "Grid", "Grid intersection"),
    ("ORIGIN", "Object Origin", "Object origin"),
]

STYLE_ITEMS = [
    ("LINEAR", "Linear", "Standard linear dimension"),
]

UNITS_ITEMS = [
    ("GLOBAL", "Global", "Use addon global unit setting"),
    ("SCENE", "Scene Units", "Use the scene unit system"),
    ("NONE", "Blender Units", "Display raw Blender units"),
]


class DIMTOOLS_SnapAnchor(bpy.types.PropertyGroup):
    """Geometry attachment for one dimension endpoint."""

    snap_type: EnumProperty(
        name="Snap Type",
        items=SNAP_ANCHOR_ITEMS,
        default="NONE",
    )
    object_name: StringProperty(name="Object", default="")
    element_index: IntProperty(name="Element Index", default=-1)
    element_index_b: IntProperty(name="Secondary Index", default=-1)
    local_co: FloatVectorProperty(name="Local Coordinate", size=3, default=(0.0, 0.0, 0.0))
    edge_param: FloatProperty(name="Edge Parameter", default=0.0, min=0.0, max=1.0)


class DIMTOOLS_ChainItem(bpy.types.PropertyGroup):
    """Shared offset plane for grouped dimensions."""

    uid: StringProperty(name="Chain ID", default="")
    plane_normal: FloatVectorProperty(name="Plane Normal", size=3, default=(0.0, 0.0, 1.0))
    offset: FloatProperty(name="Offset", default=0.0)


class DIMTOOLS_DimensionItem(bpy.types.PropertyGroup):
    """Persistent linear dimension stored in the scene."""

    uid: StringProperty(name="Dimension ID", default="")
    point_a: FloatVectorProperty(name="Point A", size=3, default=(0.0, 0.0, 0.0))
    point_b: FloatVectorProperty(name="Point B", size=3, default=(0.0, 0.0, 0.0))
    offset: FloatProperty(name="Offset", default=0.0)
    offset_vector: FloatVectorProperty(
        name="Offset Vector",
        description="World-space offset from measured points to the dimension line",
        size=3,
        default=(0.0, 0.0, 0.0),
    )
    chain_uid: StringProperty(name="Chain ID", default="")
    text_override: StringProperty(name="Text Override", default="")
    text_position: FloatVectorProperty(name="Text Position", size=3, default=(0.0, 0.0, 0.0))
    use_custom_text_position: BoolProperty(
        name="Custom Text Position",
        description="Use text_position instead of the default center",
        default=False,
    )
    color: FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0, 1.0),
    )
    use_custom_color: BoolProperty(name="Custom Color", default=False)
    visible: BoolProperty(name="Visible", default=True)
    selected: BoolProperty(name="Selected", default=False)
    style: EnumProperty(name="Style", items=STYLE_ITEMS, default="LINEAR")
    units: EnumProperty(name="Units", items=UNITS_ITEMS, default="GLOBAL")
    precision: IntProperty(name="Precision", default=-1, min=-1, max=6)
    anchor_a: PointerProperty(type=DIMTOOLS_SnapAnchor)
    anchor_b: PointerProperty(type=DIMTOOLS_SnapAnchor)


class DIMTOOLS_SceneState(bpy.types.PropertyGroup):
    """Root scene state for Dimension Tools."""

    dimensions: CollectionProperty(type=DIMTOOLS_DimensionItem)
    chains: CollectionProperty(type=DIMTOOLS_ChainItem)
    active_dimension_index: IntProperty(name="Active Dimension", default=-1)


classes = (
    DIMTOOLS_SnapAnchor,
    DIMTOOLS_ChainItem,
    DIMTOOLS_DimensionItem,
    DIMTOOLS_SceneState,
)


def register() -> None:
    """Register scene property classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.dimtools = PointerProperty(type=DIMTOOLS_SceneState)
    _log.debug("Properties registered")


def unregister() -> None:
    """Unregister scene property classes and remove Scene pointer properties."""
    if hasattr(bpy.types.Scene, "dimtools"):
        del bpy.types.Scene.dimtools
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    _log.debug("Properties unregistered")
