# Orbit asset handoff

Authored with GPT-6 Astra and Blender 3.4.1 on 1 November 2026 from the owner's original Orbit sprite sheet. No external model, asset purchase or paid generation service was used. Original source artwork and metadata were preserved.

## Runtime contract

- Asset: `public/assets/orbit/orbit.glb`.
- One glTF unit is one metre. Runtime up is **+Y**, forward is **+Z**. Blender source forward is -Y and up is +Z.
- Ground-contact origin. Rest dimensions: **0.620 m wide × 1.17734 m high × 0.475 m deep**. Scale the character instance uniformly for the miniature world.
- **18,150 triangles; one skinned mesh; six material primitives; six materials; one 256 × 256 embedded visor texture; 15 bones.** The editable Blender file retains 33 named components.
- Skeleton: root, body, head, two ears, paired upper arms / forearms, thighs / shins / feet. Headset components have rigid head weights. Body and joint surfaces have skin weights.

| Clip | Duration | Playback |
| --- | ---: | --- |
| `idle` | 3.2 s | Loop |
| `walk` | 0.8 s | Loop, in place |
| `ask_wait` | 2.4 s | Loop; head tilt and raised paw |
| `interact` | 1.6 s | Once; reaches forward and returns |
| `celebrate` | 1.8 s | Once; raised arms and small hop |

Recommended walk translation speed at native scale is **0.375 m/s × instance scale × animation timeScale**. The 0.15 m alternating steps use a 0.05 m swing lift. If the app moves faster, increase clip timeScale accordingly. Translation belongs to the game. Blend clips over about 0.15–0.25 seconds; clip blending and hardware presentation still require application verification.

## Editable sources and rebuild

- `assets/orbit/blender/orbit.blend`: editable components, skeleton, actions, preview camera and lights.
- `scripts/build_orbit.py`: complete procedural authoring, rigging, animation and GLB export.
- `assets/orbit/blender/verify_orbit.py`: independent exported-GLB re-import, deformation sampling, structural checks and render.
- `assets/orbit/blender/render_previews.py`: actual MP4 turntable and motion renders.
- `assets/orbit/blender/package_previews.ps1`: original-cell reference extraction and motion contact sheets using Windows System.Drawing.

From the workspace root, run the installed Blender 3.4 executable with `--background --python scripts/build_orbit.py -- --render --motion`. Then run the verification and preview scripts using `--background --python`. Run the PowerShell packaging script after the PNG renders finish. Blender 2.79 is also installed but is not used.

## Review evidence

- `source-reference.png`: neutral, right/left locomotion, waiting and jump poses cropped directly from the original sheet.
- `front.png`, `three-quarter.png`, `side.png`, `back.png`: actual source-scene renders.
- `glb-reimport.png`: actual render of the shipped GLB imported into a new scene.
- `walk-contact-sheet.png`, `ask_wait-contact-sheet.png`, `interact-contact-sheet.png`, `celebrate-contact-sheet.png`: eight equally spaced motion phases each.
- `walk.mp4`, `ask_wait.mp4`, `interact.mp4`, `celebrate.mp4`: 30 fps actual renders, two clip cycles each.
- `turntable.mp4`: three-second actual 360-degree render.
- `glb-verification.json`: 25 sampled deformations per exported clip, finite-vertex checks, foot heights, topology and exact exported clip times.

Inspection led to corrections for inward-leaning ear tips, detached-looking belly geometry, local bone rotation axes, subtle stride amplitude, and a visor shading defect visible only after GLB re-import. Welding the collapsed parametric centre vertices fixed that exported shading defect and reduced triangles. Final walk foot heights range from approximately zero to 0.05 m. The idle sway and interaction can produce submillimetre ground variation (less than 0.4 mm at native scale).

## Limits and remaining integration checks

This is a stylised authored interpretation of 2D artwork, not a reconstructed scan. Back surfaces are conservative; no prominent tail was invented. The compact limbs use simple soft skinning rather than anatomical muscle deformation. The walk is deliberately broader than the initial version so it reads at miniature scale, but is a walk rather than the reference sheet's faster run. Visor highlights combine a baked gradient with the runtime renderer's lighting, so appearance changes with the app's tone mapping and lights.

Blender source renders, contact sheets and an independent GLB re-import render were visually inspected. Automated exported-geometry checks were run. Browser animation blending, loading behavior and actual Quest hardware performance belong to the lead's integration checks; this handoff does not claim those tests happened. MP4 files are supplied for normal-speed human review; visual inspection here was of their rendered frame sequences.
