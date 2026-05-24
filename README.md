# numfields

Numerical electromagnetic field simulator — starting with an electrostatics **scene builder** (rendering + UI).

## Features

- Add **volume** bodies: sphere, cylinder, box
- Add **surface** bodies: disk, rectangle
- Add **line** bodies: segment (rendered as a thin cylinder)
- Orbit camera in the 3D viewport (LMB orbit, MMB pan, scroll zoom)
- ImGui panels: Viewport, Hierarchy, Add Body, Inspector
- Extensible body registry for future shapes and charge distributions

## Requirements

- Python 3.11+
- OpenGL 3.3+ capable GPU/drivers

## Install and run

From the **project root** (`numFields`, not `src\numfields`):

```bash
cd C:\Users\ilyan\OneDrive\Dokumente\Desktop\numFields
pip install -e .
python -m numfields
```

Or after install:

```bash
numfields
```

If you see `No module named numfields.__main__`, run `pip install -e .` again from the project root (this adds `__main__.py` support).

## Usage

1. Open **Add Body** and pick a primitive under Volume, Surface, or Line.
2. Select an object in **Hierarchy** to edit it in **Inspector**.
3. Use the **Viewport** for 3D navigation (mouse over viewport, not over other panels).
4. Press **Delete** with an object selected to remove it.

## Project layout

- `src/numfields/domain/` — scene graph, transforms, body types (no OpenGL)
- `src/numfields/geometry/` — procedural mesh generation
- `src/numfields/rendering/` — moderngl shaders, camera, renderer
- `src/numfields/ui/` — ImGui panels

## Next steps (planned)

- Charge distributions (ρ, σ, λ)
- Electrostatic field visualization and solvers
