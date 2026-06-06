# 3D Dynamic Particle Sphere

An interactive real-time 3D particle visualizer built with Python, PyGame, and OpenGL. It renders **13,000 particles** that morph between 11 different 3D shapes with smooth GPU-driven animations, dynamic color palettes, and a heartbeat pulse effect.

---

## Requirements

```
pygame
numpy
PyOpenGL
PyOpenGL_accelerate  # optional but recommended
```

Install with:

```bash
pip install pygame numpy PyOpenGL PyOpenGL_accelerate
```

> Requires a GPU that supports **OpenGL 3.3 Core Profile**.

---

## How to Run

```bash
python sphere.py
```

---

## Controls

| Action | Effect |
|---|---|
| Left Mouse Click | Morph to the next shape |
| Mouse Move | Subtly influences rotation |
| `Escape` | Quit |
| Window Resize | Viewport and projection auto-adjust |

---

## Configuration Constants

| Constant | Value | Description |
|---|---|---|
| `WIDTH` | 1280 | Window width in pixels |
| `HEIGHT` | 720 | Window height in pixels |
| `PARTICLES` | 13000 | Total number of particles rendered |
| `RADIUS` | 300 | Base render radius in world units |

---

## Shape Generators

Each function returns a flat `float32` numpy array of `PARTICLES * 3` values (x, y, z per particle). Shapes cycle in order on each left click.

| Function | Shape | Algorithm |
|---|---|---|
| `sphere_positions()` | Sphere | Fibonacci / golden angle spiral for even distribution |
| `cube_positions()` | Cube | Random points distributed across 6 faces |
| `triangle_positions()` | Triangle | Barycentric interpolation over 3 vertices, slight depth |
| `pentagon_positions()` | Pentagon | Sector-based polar mapping with 5 sides |
| `star_positions()` | Star | Alternating long/short radii across 10 angular sectors |
| `diamond_positions()` | Diamond (Octahedron) | Barycentric interpolation over 8 triangular faces |
| `torus_positions()` | Torus | Parametric torus with major radius `0.65`, minor `0.28` |
| `helix_positions()` | Double Helix | Two interleaved helical strands winding 8 full turns |
| `galaxy_positions()` | Galaxy | 3-arm logarithmic spiral with radial spread falloff |
| `cross_positions()` | 3D Cross | 6 arms along ±X, ±Y, ±Z axes with random thickness |
| `heart_positions()` | Heart | Parametric heart curve `(16sin³t, 13cos t − ...)` |

The `SHAPES` list holds references to all 11 generators and drives the morph cycle.

---

## GLSL Shaders

### Vertex Shader

Runs once per particle on the GPU.

- **Morphing**: Uses `mix(in_position, in_target, morphFactor)` to smoothly interpolate each particle between its current and target shape.
- **Wave Distortion**: Three layered vortex sine waves (`vortex1/2/3`) plus a `ripple` term create organic surface movement.
- **Beat Scale**: Multiplies the particle radius by `beatScale` to produce the heartbeat pulse.
- **Point Size**: Dynamically sized based on perspective depth — closer particles appear larger.
- **Outputs**: Passes `vWave`, `vDepth`, and `vColorT` to the fragment shader.

**Uniforms**

| Uniform | Type | Description |
|---|---|---|
| `time` | float | Elapsed time in seconds |
| `radius` | float | World-space render radius |
| `morphFactor` | float | 0.0 → 1.0 morph interpolation progress |
| `beatScale` | float | Heartbeat pulse scale factor |
| `mvp` | mat4 | Model-View-Projection matrix |
| `modelView` | mat4 | Model-View matrix (for depth calculation) |

### Fragment Shader

Runs once per pixel of each particle point sprite.

- **Circular Clipping**: Discards fragments outside a radius of 0.5 (makes square point sprites into circles).
- **Glow Effect**: Uses `smoothstep` to create a soft radial glow from center to edge.
- **Color Palette**: Implements the classic cosine color palette formula:  
  `color = a + b * cos(2π * (c*t + d))`  
  Two palettes (`col1`, `col2`) are blended based on depth and wave values, producing dynamic, shifting colors.

**Uniform**

| Uniform | Type | Description |
|---|---|---|
| `colorTime` | float | Drives the hue cycle of the color palette |

---

## Math Helper Functions

| Function | Description |
|---|---|
| `perspective(fov_deg, aspect, near, far)` | Builds a standard 4×4 perspective projection matrix |
| `translate(x, y, z)` | Builds a 4×4 translation matrix |
| `rot_x(a)` | 4×4 rotation matrix around the X axis |
| `rot_y(a)` | 4×4 rotation matrix around the Y axis |
| `rot_z(a)` | 4×4 rotation matrix around the Z axis |

All matrices are `numpy float32` arrays. Composition is done with `@` (matrix multiply).

---

## ParticleObject Class

Manages one full set of particles: GPU buffer, transforms, and rendering.

### `__init__(prog, base_positions, scale, rot_y_offset)`
- Allocates a VAO and VBO on the GPU.
- Stores particles as **interleaved** data: `[x, y, z, tx, ty, tz]` per particle, where `xyz` is the current position and `txyz` is the morph target.
- Two instances are created (`obj1` and `obj2`) — `obj2` is slightly smaller (`scale=0.93`) and rotated `π/4` for a layered depth effect.

### `update_target(new_positions)`
Writes new morph-target positions into the VBO (positions `[3::6]`, `[4::6]`, `[5::6]`).

### `swap_to_target()`
Copies target positions into current positions once a morph completes, resetting the base for the next transition.

### `render(view, proj, t, morph, beat, color_t)`
- Builds the model matrix from current `rx/ry/rz` rotation angles and `py` float offset.
- Uploads all uniforms and issues a `glDrawArrays(GL_POINTS, ...)` call.

---

## Main Loop (`main()`)

### Initialization
- Creates an OpenGL 3.3 Core Context via PyGame.
- Compiles vertex and fragment shaders.
- Enables `GL_PROGRAM_POINT_SIZE` (GPU-controlled point size), `GL_BLEND` with **additive blending** (`GL_SRC_ALPHA, GL_ONE`) for the glowing particle look.
- Depth test is disabled — particles layer additively instead of occluding each other.

### Per-Frame Logic

**Heartbeat Pulse** — repeats every 5 seconds:

| Phase (seconds) | Effect |
|---|---|
| 0.00 – 0.15 | Expand to 1.08× |
| 0.15 – 0.30 | Contract to 0.98× |
| 0.30 – 0.45 | Expand to 1.04× |
| 0.45 – 0.60 | Return to 1.0× |
| 0.60 – 5.00 | Hold at 1.0× |

**Morph Transition** — triggered by mouse click:
- `morphFactor` increments by `0.018` per frame (~55 frames / ~0.9 seconds for a full transition).
- On completion, `swap_to_target()` locks in the new shape.

**Rotation** — each object rotates independently on all three axes every frame. Mouse position adds a small additional tilt to `obj1`.

**Floating** — both objects bob up and down with `sin(t * 0.6) * 15` on the Y axis.

**Background** — deep dark purple: RGB `(18, 0, 58)`.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Architecture Overview

```
main()
├── PyGame + OpenGL setup
├── Compile VERTEX_SHADER + FRAGMENT_SHADER → prog
├── sphere_positions() → ParticleObject obj1 (scale 1.0)
│                      → ParticleObject obj2 (scale 0.93, rotated π/4)
└── Game Loop
    ├── Event handling (quit / click / mouse / resize)
    ├── Heartbeat beat_scale calculation
    ├── Morph factor update
    ├── Rotation + float_y update
    └── Render
        ├── glClear (dark purple)
        ├── obj1.render(...)
        └── obj2.render(...)
```
