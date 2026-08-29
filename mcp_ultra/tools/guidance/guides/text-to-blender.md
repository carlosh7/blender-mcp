# text-to-blender — Orchestrator Skill

Entry point for natural language → Blender scene generation.
Chain-loads sub-skills based on user intent.

## Intent Detection

Parse user request and decide which sub-skills to load:

```
User: "create a red chair with three-point lighting and render"
→ modeling + materials + lighting + cameras + rendering

User: "animate the sphere moving from left to right"
→ animation

User: "export the scene as glTF"
→ export

User: "make a 3D model from this wireframe sketch"
→ wireframe-to-3d
```

## Workflow Sequence (Pro Mode)

1. **Block-out**: Create primitive shapes with correct proportions
2. **Camera**: Set up framing and composition
3. **Lighting**: Add environment or artificial lights
4. **Forms**: Refine geometry with modifiers
5. **Materials**: Apply colors and PBR materials
6. **Detail**: Add edge loops, bevels, subdivisions
7. **Render**: Configure engine, resolution, output
8. **Composite**: Post-processing (optional)
9. **Export**: GLTF/FBX/USD/STL

## Conventions

- Use execute_blender_code() for all geometry operations
- Name objects with prefixes: GEO_ (geometry), MAT_ (material), LGT_ (light), CAM_ (camera)
- Always apply transforms before exporting
- Validate with get_viewport_screenshot_image() after each phase

## Example Chain

```
text-to-blender
  → blender-pro-workflow (sequencing)
  → blender-modeling
  → blender-materials
  → blender-lighting
  → blender-cameras
  → blender-rendering
  → blender-export
```
