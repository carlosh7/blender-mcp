# blender-pro-workflow — Professional Production Workflow

Multi-phase production workflow for professional 3D asset creation.

## Phase 1: Brief & Planning

- Understand the deliverable (format, poly count, texture resolution)
- Gather references (images, sketches, dimensions)
- Plan naming convention: `GEO_`, `MAT_`, `LGT_`, `CAM_`, `TEX_`, `COL_`

## Phase 2: Block-out

```
Goal: Rough proportions and composition
- Use simple primitives at correct scale
- Focus on silhouette and proportions
- Set up camera angle
- Present block-out for approval
```

## Phase 3: High-Poly Modeling

```
Goal: Detailed mesh with proper topology
- Add edge loops for support
- Apply bevels and subdivisions
- Boolean operations for cuts
- Check mesh quality with mesh_analysis()
```

## Phase 4: UV & Texturing

```
Goal: Proper UV layout and PBR materials
- Unwrap with smart project or manual seams
- Ensure UVs are within 0-1 space
- Apply PBR materials
- Bake if needed
```

## Phase 5: Look-Dev

```
Goal: Final appearance with lighting and materials
- Set up three-point or environment lighting
- Fine-tune material values
- Add camera DOF if needed
- Validate with screenshot
```

## Phase 6: Export & Delivery

```
Goal: Clean, optimized deliverable
- Apply all transforms
- Purge orphan data
- Name everything consistently
- Export in requested format
- Verify exported file
```

## Naming Convention

| Prefix | Type | Example |
|--------|------|---------|
| GEO_ | Geometry | GEO_Sword_Blade |
| MAT_ | Material | MAT_Gold_01 |
| LGT_ | Light | LGT_Key_Top |
| CAM_ | Camera | CAM_Hero_Shot |
| TEX_ | Texture | TEX_Brick_Wall |
| COL_ | Collection | COL_Props |

## Validation Gates

Each phase must pass before moving to next:
1. Block-out: ✅ Proportions match reference
2. Modeling: ✅ Manifold, no N-gons, clean topology
3. UV: ✅ No overlaps, efficient packing
4. Look-Dev: ✅ Matches reference lighting
5. Export: ✅ File opens correctly in target app
