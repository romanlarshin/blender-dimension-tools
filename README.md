# Dimension Tools

Professional CAD-like linear dimension annotations for Blender 5.1+.

Dimensions are stored as scene data and rendered entirely in the viewport using GPU overlays — no Curve or Mesh objects are created.

## Features

- **Persistent modal placement** — create unlimited dimensions in one session (`Alt+D` shortcut)
- **Snapping** — vertex, edge midpoint, edge, face center, grid, object origin
- **GPU rendering** — extension lines, dimension lines, arrowheads, measurement text
- **Scene persistence** — save and reload dimensions with your `.blend` file
- **Selection & editing** — select, delete, move text, move offset, custom labels
- **Live geometry** — dimensions follow deformed or transformed mesh geometry
- **Global styling** — text size, arrow size, line width, colors, units, precision
- **Undo support** — all operators support Blender undo

## Install

1. Zip the `dimension_tools` folder (the folder itself must be at the root of the zip)
2. In Blender: **Edit → Preferences → Add-ons → Install…**
3. Select the zip file and enable **Dimension Tools**

Alternatively, symlink or copy the `dimension_tools` folder into your Blender addons directory.

## Quick Start

1. Open the **Dimensions** tab in the 3D Viewport sidebar (N-panel)
2. Click **Linear Dimension** (or press `Alt+D` in the 3D View)
3. Click two snap points on your geometry
4. Move the mouse to set the dimension offset
5. Click to confirm — repeat for more dimensions
6. Press **Esc** to exit placement mode

## Workflow

| Step | Action |
|------|--------|
| Start | Linear Dimension tool |
| Move | Snap highlight follows cursor |
| Click 1 | First point |
| Click 2 | Enter offset mode |
| Drag | Adjust offset (live measurement shown) |
| Click 3 | Dimension created |
| Repeat | Continue placing |
| Esc | Exit tool |

**During placement:** `Backspace` or `RMB` undo the last click.

## Selection & Editing

| Action | Method |
|--------|--------|
| Select | **Select Dimension** tool, click in viewport |
| Multi-select | Shift+click |
| Delete | **Delete Selected** or `Del` / `X` |
| Move text | Select → **Move Text** |
| Move offset | Select → **Move Offset** |
| Custom label | Select → **Set Dimension Text** |
| Toggle visibility | Select → **Toggle Visibility** or list panel eye icon |

## Preferences

Global settings are in the sidebar panel and in **Edit → Preferences → Add-ons → Dimension Tools**:

- Text size, arrow size, line width
- Color, extension line opacity, selection/hover colors
- Units (scene units or raw Blender units) and decimal precision
- Snap radius and per-type snap toggles

## Project Structure

```
dimension_tools/
  __init__.py          Entry point
  properties.py        Scene RNA storage
  preferences.py       Addon preferences
  core/                Domain logic (store, selection, anchors)
  engine/              Snap, offset, draw, modal, chain
  gpu/                 Batched GPU rendering
  overlay/             Arrows, text, lines, previews
  operators/           Blender operators
  ui/                  Sidebar panels
  utils/               Shared helpers
```

## Requirements

- Blender 5.1 or newer
- Python 3.x (bundled with Blender)

## License

See [LICENSE](LICENSE).
