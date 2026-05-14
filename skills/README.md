# Claude Code Skills for blender-mcp

10 chain-loadable skills for professional 3D creation via Claude Code.

## Quick Install

```bash
for skill in skills/*/; do
    name=$(basename "$skill")
    ln -sfn "$(pwd)/$skill" "$HOME/.claude/skills/$name"
done
```

## Skills Overview

| Skill | Description |
|-------|-------------|
| **text-to-blender** | 🎯 Entry point. Detects intent and chain-loads sub-skills |
| **blender-modeling** | 🔷 Primitives, modifiers, topology, boolean operations |
| **blender-materials** | 🎨 PBR materials, Principled BSDF recipes, texture maps |
| **blender-lighting** | 💡 Three-point, HDRI, studio presets, colored gels |
| **blender-cameras** | 📷 Framing, focal length, DOF, auto-framing, tracking |
| **blender-rendering** | 🖼️ Cycles/EEVEE, resolution, color management, output |
| **blender-animation** | 🎬 Keyframes, rotation/scale/location, interpolation, actions |
| **blender-export** | 📦 GLB/GLTF, FBX, OBJ, STL, USD with pre-export checklist |
| **wireframe-to-3d** | 📐 2D wireframe → 3D, SVG import, lathe, extrude |
| **blender-pro-workflow** | 🏭 6-phase production pipeline with validation gates |

## Usage

Once installed, ask Claude Code:

> "Make a 3D model of a teapot and render it with three-point lighting"

Claude will load `text-to-blender` → detect intent → chain-load:
`modeling → materials → lighting → cameras → rendering`

## Architecture

```
User prompt
    ↓
text-to-blender (orchestrator) detects intent
    ↓
Chain-loads relevant sub-skills
    ↓ ↓ ↓
modeling → materials → lighting → cameras → rendering → animation → export
    ↓
Generated Python → execute_blender_code() → Blender
```
