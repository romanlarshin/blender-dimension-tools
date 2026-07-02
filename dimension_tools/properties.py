import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    StringProperty,
)


class DIMTOOLS_PG_dimension(bpy.types.PropertyGroup):
    name: StringProperty(name="Name", default="Dimension")
    p1: FloatVectorProperty(name="P1", size=3, subtype="XYZ")
    p2: FloatVectorProperty(name="P2", size=3, subtype="XYZ")
    q1: FloatVectorProperty(name="Q1", size=3, subtype="XYZ")
    q2: FloatVectorProperty(name="Q2", size=3, subtype="XYZ")
    text_pos: FloatVectorProperty(name="Text Position", size=3, subtype="XYZ")
    value: FloatProperty(name="Value", default=0.0)
    custom_text: StringProperty(name="Custom Text", default="")
    selected: BoolProperty(name="Selected", default=False)


class DIMTOOLS_PG_settings(bpy.types.PropertyGroup):
    dimensions: CollectionProperty(type=DIMTOOLS_PG_dimension)
    selected_index: IntProperty(name="Selected Dimension", default=-1)

    text_size: IntProperty(name="Text Size", default=18, min=8, max=96)
    line_thickness: FloatProperty(name="Line Thickness", default=1.5, min=1.0, max=12.0)
    snap_radius: FloatProperty(name="Snap Radius", default=16.0, min=4.0, max=80.0)
    chain_magnet_radius: FloatProperty(name="Chain Magnet", default=22.0, min=0.0, max=120.0)
    arrow_size: FloatProperty(name="Arrow Size", default=0.12, min=0.01, max=2.0)
    decimals: IntProperty(name="Decimals", default=2, min=0, max=4)
    unit_suffix: StringProperty(name="Unit Suffix", default=" m")

    direction_mode: EnumProperty(
        name="Direction",
        items=[
            ("FREE", "Free", "Use mouse position"),
            ("X", "X", "Lock offset to world X"),
            ("Y", "Y", "Lock offset to world Y"),
            ("Z", "Z", "Lock offset to world Z"),
        ],
        default="FREE",
    )


def register_props():
    bpy.types.Scene.dimtools = bpy.props.PointerProperty(type=DIMTOOLS_PG_settings)


def unregister_props():
    if hasattr(bpy.types.Scene, "dimtools"):
        del bpy.types.Scene.dimtools
