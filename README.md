# Blender Dimension Tools

CAD-like dimension annotation addon for Blender.

Current prototype goals:
- persistent Linear Dimension mode until `Esc`
- snap to vertices and edge midpoints
- draw dimensions as viewport overlay, not Curve objects
- global text size and line thickness
- chain magnet by nearest existing dimension line
- select and delete individual dimensions

## Install
Zip the `dimension_tools` folder and install it via Blender:
`Edit > Preferences > Add-ons > Install`.

## Development
This addon stores only simple registered Blender properties in `Scene`.
Runtime preview state is kept in Python memory only.
