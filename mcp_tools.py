"""
mcp_tools.py — MCP tool surface for blender-mcp.

SDK-free by design: each tool is a plain callable that sends a command to the
Blender socket server. `mcp_server.py` registers them with FastMCP (typed
signatures are built from the SPEC below), and `stdio_bridge.py` reuses the
same SPEC for its JSON-RPC tools/list + tools/call. One source of truth.

Param types: str, float, int, bool, vec (list of numbers), strlist, any.
"""
import inspect
import json

from blender_connection import get_blender

TOOL_FUNCTIONS = []
TOOL_META = {}          # tool_name -> {"command", "read_only", "params", "doc"}
READ_ONLY = set()       # tool names that only read scene state


def _make_tool(tool_name, command, doc, read_only, params):
    """Build a typed callable; FastMCP picks schema up from __signature__."""

    def _run(**kwargs):
        b = get_blender()
        args = {}
        for p in params:
            name = p["name"]
            if name in kwargs:
                args[name] = kwargs[name]
            elif "default" in p:
                args[name] = p["default"]
        try:
            result = b.send_command(command, args)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
        return json.dumps(result, indent=2, ensure_ascii=False)

    _run.__name__ = tool_name
    _run.__doc__ = doc
    _run.__annotations__ = {"return": str}

    sig_params = []
    for p in params:
        name = p["name"]
        ptype = p["type"]
        annotation = {
            "str": str, "float": float, "int": int, "bool": bool,
            "vec": list, "strlist": list, "any": object,
        }.get(ptype, str)
        has_default = "default" in p
        default = p.get("default")
        if default is None and has_default:
            annotation = annotation | None
        if has_default:
            sig_params.append(
                inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY,
                                  default=default, annotation=annotation))
        else:
            sig_params.append(
                inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY,
                                  annotation=annotation))
    _run.__signature__ = inspect.Signature(sig_params, return_annotation=str)

    TOOL_FUNCTIONS.append(_run)
    TOOL_META[tool_name] = {
        "command": command,
        "read_only": read_only,
        "params": params,
        "doc": doc,
    }
    if read_only:
        READ_ONLY.add(tool_name)
    return _run


def _tool(tool_name, command, doc, read_only=False, **params):
    spec = []
    for pname, ptype in params.items():
        if isinstance(ptype, dict):
            spec.append({"name": pname, **ptype})
        else:
            spec.append({"name": pname, "type": ptype})
    return _make_tool(tool_name, command, doc, read_only, spec)


# ─── Core / legacy socket commands ─────────────────────────────────────────────
_tool("get_scene_info", "get_scene_info",
      "Kondisi scene: jumlah objek, nama, tipe, lokasi.", read_only=True)
_tool("execute_blender_code", "execute_code",
      "Jalankan Python bebas di dalam Blender. Utamakan tool terstruktur; gunakan "
      "search_api_docs dulu untuk mencari API yang benar.", code="str")
_tool("get_viewport_screenshot", "get_viewport_screenshot",
      "Tangkap viewport 3D ke PNG (memerlukan UI Blender).", read_only=True)
_tool("search_api_docs", "search_api_docs",
      "Cari dokumentasi API Blender yang disertakan. Baca SEBELUM menulis kode.",
      read_only=True, query="str")
_tool("get_python_api_docs", "get_python_api_docs",
      "Dokumentasi detail topik API Blender, mis. bpy.ops.mesh.primitive_cube_add.",
      read_only=True, topic="str")
_tool("snap_and_parent", "snap_and_parent",
      "Snap obj_move ke obj_target dengan mencocokkan anchor 27-titik, lalu parent.",
      obj_move="str", obj_target="str",
      anchor_move={"type": "str", "default": "A_CENTER_CENTER_CENTER"},
      anchor_target={"type": "str", "default": "A_CENTER_CENTER_CENTER"})
_tool("snap_to_anchor", "snap_to_anchor",
      "Pindahkan objek agar salah satu dari 27 anchor-nya cocok dengan anchor objek lain.",
      obj_move="str", obj_target="str",
      anchor_move={"type": "str", "default": "A_CENTER_CENTER_CENTER"},
      anchor_target={"type": "str", "default": "A_CENTER_CENTER_CENTER"})
_tool("apply_symmetry", "apply_symmetry",
      "Tambah modifier Mirror untuk simetri industri.",
      obj_name="str", axes={"type": "strlist", "default": ["X", "Y"]})
_tool("fix_normals", "fix_normals",
      "Hitung ulang normal mesh agar konsisten (memerlukan UI).",
      obj_name="str")
_tool("get_object_anchors", "get_object_anchors",
      "Kembalikan 27 titik anchor objek dalam ruang global.",
      read_only=True, obj_name="str")
_tool("get_model_blueprint", "get_model_blueprint",
      "Blueprint teknis lengkap mesh: topologi, fisika, dimensi, anchor.",
      read_only=True, obj_name="str")
_tool("get_spatial_visual", "get_spatial_visual",
      "Telemetri spasial ASCII scene untuk agen.",
      read_only=True)
_tool("validate_geometry", "validate_geometry",
      "Laporan QC: tabrakan (BVH), z-fighting, objek mengambang.",
      read_only=True)
_tool("get_scene_property", "get_scene_property",
      "Baca properti scene apa pun.", read_only=True, prop="str")
_tool("ping", "ping",
      "Pemeriksaan liveness terhadap Blender.", read_only=True)
_tool("export_glb", "export_glb",
      "Export seluruh scene sebagai GLB.", filepath="str")
_tool("jump_to_view3d_object_by_name", "jump_to_view3d_object_by_name",
      "Frame viewport 3D ke sebuah objek (memerlukan UI).",
      name="str")

# ─── Modeling ──────────────────────────────────────────────────────────────────
_tool("create_object", "create_object",
      "Buat primitive dari nol: CUBE/PLANE/SPHERE/UVSPHERE/ICOSPHERE/"
      "CYLINDER/CONE/TORUS/MONKEY/GRID/CIRCLE/EMPTY. Aman di background.",
      type={"type": "str", "default": "CUBE"},
      name={"type": "str", "default": ""},
      location={"type": "vec", "default": (0, 0, 0)},
      size={"type": "float", "default": 1.0},
      radius={"type": "float", "default": 1.0},
      depth={"type": "float", "default": 2.0},
      vertices={"type": "int", "default": 32},
      segments={"type": "int", "default": 48},
      minor_segments={"type": "int", "default": 16},
      scale={"type": "vec", "default": (1, 1, 1)})
_tool("get_object_info", "get_object_info",
      "Info satu objek: transform, topologi, material, modifier.",
      read_only=True, name="str")
_tool("delete_object", "delete_object",
      "Hapus objek berdasarkan nama.", name="str")
_tool("transform_object", "transform_object",
      "Pindah/putar/skala objek (absolut atau relatif).",
      name="str", location="vec", rotation="vec", scale="vec",
      relative={"type": "bool", "default": False})
_tool("duplicate_object", "duplicate_object",
      "Duplikat objek (data dibagi).",
      name="str", new_name={"type": "str", "default": ""})
_tool("select_object", "select_object",
      "Pilih satu objek.", name="str")
_tool("add_modifier", "add_modifier",
      "Tambah modifier: SUBSURF/BEVEL/BOOLEAN/ARRAY/MIRROR/SOLIDIFY/SCREW/"
      "WIREFRAME/DECIMATE/REMESH/WELD/DISPLACE/... Aman di background.",
      object_name="str",
      modifier_type={"type": "str", "default": "SUBSURF"},
      operation={"type": "str", "default": "DIFFERENCE"},
      target_object={"type": "str", "default": ""},
      count={"type": "int", "default": 2},
      offset={"type": "vec", "default": (1, 0, 0)},
      levels={"type": "int", "default": 1},
      render_levels={"type": "int", "default": 0},
      width={"type": "float", "default": 0.01},
      segments={"type": "int", "default": 1},
      thickness={"type": "float", "default": 0.01},
      axes={"type": "strlist", "default": ["X"]},
      angle={"type": "float", "default": 360.0},
      steps={"type": "int", "default": 16},
      axis={"type": "str", "default": "Y"},
      ratio={"type": "float", "default": 0.5},
      octree_depth={"type": "int", "default": 6},
      merge_threshold={"type": "float", "default": 0.001},
      strength={"type": "float", "default": 1.0})
_tool("list_modifiers", "list_modifiers",
      "Daftar modifier pada objek.", read_only=True, object_name="str")
_tool("remove_modifier", "remove_modifier",
      "Hapus modifier berdasarkan nama.", object_name="str", modifier_name="str")
_tool("apply_modifiers", "apply_modifiers",
      "Bakar semua modifier ke data mesh.", object_name="str")
_tool("boolean_operation", "boolean_operation",
      "Boolean DIFFERENCE/UNION/INTERSECT antara dua mesh.",
      object_name="str", target_object="str",
      operation={"type": "str", "default": "DIFFERENCE"})
_tool("join_objects", "join_objects",
      "Gabungkan beberapa objek mesh menjadi satu.",
      object_names="strlist", new_name={"type": "str", "default": "Merged"})
_tool("merge_by_distance", "merge_by_distance",
      "Hapus vertex ganda.", object_name="str",
      distance={"type": "float", "default": 0.001})
_tool("bevel_mesh", "bevel_mesh",
      "Bevel edge atau vertex dengan bmesh.",
      object_name="str", width={"type": "float", "default": 0.01},
      segments={"type": "int", "default": 1},
      affect={"type": "str", "default": "EDGES"})
_tool("extrude_face", "extrude_face",
      "Extrude satu face sepanjang offset.",
      object_name="str", face_index={"type": "int", "default": 0},
      offset={"type": "vec", "default": (0, 0, 1)})
_tool("inset_face", "inset_face",
      "Inset satu face.",
      object_name="str", face_index={"type": "int", "default": 0},
      thickness={"type": "float", "default": 0.1},
      depth={"type": "float", "default": 0.0})
_tool("solidify_mesh", "solidify_mesh",
      "Tambah ketebalan kulit (modifier Solidify).",
      object_name="str", thickness={"type": "float", "default": 0.01},
      offset={"type": "float", "default": -1.0})
_tool("clean_mesh", "clean_mesh",
      "Hapus vertex ganda + geometri lepas.",
      object_name="str", merge_distance={"type": "float", "default": 0.001},
      delete_loose={"type": "bool", "default": True})
_tool("create_text", "create_text",
      "Buat objek teks 3D.",
      name={"type": "str", "default": "Text"},
      body={"type": "str", "default": "Hello"},
      location={"type": "vec", "default": (0, 0, 0)},
      size={"type": "float", "default": 1.0},
      extrude={"type": "float", "default": 0.0},
      font_name={"type": "str", "default": "Bfont"})
_tool("create_curve", "create_curve",
      "Buat kurva bezier/poly dari titik-titik.",
      name={"type": "str", "default": "Curve"},
      points={"type": "vec", "default": [[0, 0, 0], [1, 0, 0], [2, 1, 0]]},
      bezier={"type": "bool", "default": True},
      closed={"type": "bool", "default": False},
      location={"type": "vec", "default": (0, 0, 0)},
      extrude={"type": "float", "default": 0.0})
_tool("create_screw_profile", "create_screw_profile",
      "Lathe/screw kurva profil mengelilingi sumbu.",
      name={"type": "str", "default": "Screw"},
      profile={"type": "vec", "default": [[0, 0, 0], [0.2, 0, 0], [0.2, 0.5, 0], [0, 0.5, 0]]},
      angle={"type": "float", "default": 360.0},
      steps={"type": "int", "default": 32},
      axis={"type": "str", "default": "Y"},
      location={"type": "vec", "default": (0, 0, 0)})
_tool("create_empty", "create_empty",
      "Buat objek Empty (titik referensi/kontrol).",
      name={"type": "str", "default": "Empty"},
      location={"type": "vec", "default": (0, 0, 0)},
      display_type={"type": "str", "default": "PLAIN_AXES"})
_tool("subdivide_mesh", "subdivide_mesh",
      "Subdivide semua edge mesh (bmesh).",
      object_name="str", cuts={"type": "int", "default": 1},
      smooth={"type": "float", "default": 0.0})
_tool("loop_cut", "loop_cut",
      "Potong loop mesh sepanjang bidang (bmesh.bisect_plane).",
      object_name="str",
      plane_co={"type": "vec", "default": (0, 0, 0)},
      plane_no={"type": "vec", "default": (0, 1, 0)},
      clear_inner={"type": "bool", "default": False},
      clear_outer={"type": "bool", "default": False})
_tool("apply_transform", "apply_transform",
      "Bakar transform objek ke data mesh dan reset.",
      object_name="str")

_tool("model_from_scratch", "model_from_scratch",
      "Buat model dasar lengkap dari nol: primitive, skala, subdivision, bevel, dan smooth shading.",
      name={"type": "str", "default": "Model"},
      type={"type": "str", "default": "CUBE"},
      location={"type": "vec", "default": (0, 0, 0)},
      scale={"type": "vec", "default": None},
      subdivisions={"type": "int", "default": 0},
      bevel_width={"type": "float", "default": 0.0},
      smooth={"type": "bool", "default": False})


# ─── Materials / coloring ──────────────────────────────────────────────────────
_tool("create_material", "create_material",
      "Buat material PBR (Principled BSDF): warna, roughness, metallic, "
      "emisi, IOR, alpha, transmission, blend mode.",
      name={"type": "str", "default": "Material"},
      color={"type": "vec", "default": (0.8, 0.8, 0.8, 1.0)},
      roughness={"type": "float", "default": 0.5},
      metallic={"type": "float", "default": 0.0},
      emission_color={"type": "vec", "default": (1, 1, 1, 1)},
      emission_strength={"type": "float", "default": 0.0},
      ior={"type": "float", "default": 1.45},
      alpha={"type": "float", "default": 1.0},
      blend_mode={"type": "str", "default": "OPAQUE"},
      transmission={"type": "float", "default": 0.0})
_tool("assign_material", "assign_material",
      "Tetapkan material ke objek.",
      object_name="str", material_name="str")
_tool("list_materials", "list_materials",
      "Daftar semua material di file.", read_only=True)
_tool("set_color", "set_color",
      "Atur Base Color material aktif objek.",
      object_name="str", color={"type": "vec", "default": (1, 1, 1, 1)})
_tool("add_shader_node", "add_shader_node",
      "Tambah node shader: bsdf_principled/bsdf_diffuse/emission/tex_noise/"
      "tex_image/mix_shader/math/...",
      material_name="str",
      node_type={"type": "str", "default": "bsdf_principled"},
      name={"type": "str", "default": ""})
_tool("list_shader_nodes", "list_shader_nodes",
      "Daftar node shader di node tree material.",
      read_only=True, material_name="str")
_tool("set_node_value", "set_node_value",
      "Atur nilai input node shader (mis. Roughness pada Principled BSDF).",
      material_name="str", node_name="str", input_name="str",
      value={"type": "any", "default": 0.0})
_tool("connect_shader_nodes", "connect_shader_nodes",
      "Hubungkan dua socket node shader.",
      material_name="str", from_node="str", from_output="str",
      to_node="str", to_input="str")
_tool("remove_shader_node", "remove_shader_node",
      "Hapus node shader.", material_name="str", node_name="str")
_tool("create_image_texture", "create_image_texture",
      "Buat datablock gambar prosedural.",
      name={"type": "str", "default": "Texture"},
      width={"type": "int", "default": 1024},
      height={"type": "int", "default": 1024},
      color={"type": "vec", "default": (1, 1, 1, 1)})
_tool("assign_image_texture", "assign_image_texture",
      "Tambah node Image Texture dan hubungkan ke Base Color.",
      material_name="str", image_name="str",
      connect={"type": "bool", "default": True})
_tool("add_vertex_color", "add_vertex_color",
      "Tambah layer vertex color yang dicat satu warna.",
      object_name="str", layer_name={"type": "str", "default": "Col"},
      color={"type": "vec", "default": (1, 1, 1, 1)})
_tool("set_emission", "set_emission",
      "Buat material memancar (emissive).",
      material_name="str", color={"type": "vec", "default": (1, 1, 1, 1)},
      strength={"type": "float", "default": 1.0})
_tool("set_transparency", "set_transparency",
      "Buat material transparan (alpha + metode blend).",
      material_name="str", alpha={"type": "float", "default": 0.5},
      blend_mode={"type": "str", "default": "BLEND"})
_tool("colorize_from_scratch", "colorize_from_scratch",
      "Sekali jalan: buat + tetapkan material PBR ke objek.",
      object_name="str", color={"type": "vec", "default": (0.2, 0.6, 0.9, 1.0)},
      roughness={"type": "float", "default": 0.4},
      metallic={"type": "float", "default": 0.1})

# ─── Rigging ───────────────────────────────────────────────────────────────────
_tool("create_armature", "create_armature",
      "Buat objek armature (opsional tulang akar).",
      name={"type": "str", "default": "Armature"},
      location={"type": "vec", "default": (0, 0, 0)},
      add_root_bone={"type": "bool", "default": True})
_tool("add_bone", "add_bone",
      "Tambah tulang ke armature (edit mode; memerlukan UI di Blender asli).",
      armature_name="str", bone_name={"type": "str", "default": "Bone"},
      head={"type": "vec", "default": (0, 0, 0)},
      tail={"type": "vec", "default": (0, 0, 1)},
      parent={"type": "str", "default": ""},
      collection={"type": "str", "default": "MCP_Bones"})
_tool("remove_bone", "remove_bone",
      "Hapus tulang.", armature_name="str", bone_name="str")
_tool("list_bones", "list_bones",
      "Daftar tulang armature.", read_only=True, armature_name="str")
_tool("rename_bone", "rename_bone",
      "Ganti nama tulang.", armature_name="str", bone_name="str", new_name="str")
_tool("add_vertex_group", "add_vertex_group",
      "Buat vertex group pada mesh.",
      object_name="str", group_name={"type": "str", "default": "Group"})
_tool("assign_vertex_weights", "assign_vertex_weights",
      "Tetapkan bobot ke vertex group (indeks opsional = semua).",
      object_name="str", group_name="str", vertex_indices="vec",
      weight={"type": "float", "default": 1.0},
      mode={"type": "str", "default": "ADD"})
_tool("remove_vertex_group", "remove_vertex_group",
      "Hapus vertex group.", object_name="str", group_name="str")
_tool("add_constraint", "add_constraint",
      "Tambah constraint (COPY_LOCATION/COPY_TRANSFORMS/TRACK_TO/IK/...).",
      object_name="str",
      constraint_type={"type": "str", "default": "COPY_LOCATION"},
      target_name="str", subtarget={"type": "str", "default": ""},
      influence={"type": "float", "default": 1.0})
_tool("setup_ik_chain", "setup_ik_chain",
      "Constraint IK pada pose bone dengan chain count dan pole target.",
      armature_name="str", bone_name="str", target_object="str",
      pole_object={"type": "str", "default": ""},
      chain_count={"type": "int", "default": 3})
_tool("auto_rig_weight", "auto_rig_weight",
      "Parent mesh ke armature dengan bobot otomatis (memerlukan UI).",
      object_name="str", armature_name="str")
_tool("mirror_bones", "mirror_bones",
      "Simetrikan tulang armature (memerlukan UI).",
      armature_name="str", axis={"type": "str", "default": "X"})
_tool("reset_pose", "reset_pose",
      "Reset transform pose bone ke posisi istirahat.",
      armature_name="str", bone_name={"type": "str", "default": ""})
_tool("pose_bone", "pose_bone",
      "Atur transform pose bone (relatif secara default).",
      armature_name="str", bone_name="str", location="vec",
      rotation="vec", scale="vec", relative={"type": "bool", "default": True})
_tool("add_armature_modifier", "add_armature_modifier",
      "Tambah modifier Armature ke mesh tanpa weight painting (background-safe).",
      object_name="str", armature_name="str")

_tool("rig_from_scratch", "rig_from_scratch",
      "Buat armature dan rantai tulang dari nol lalu ikat ke mesh. Multi-tulang di background memerlukan bobot manual.",
      object_name="str", armature_name={"type": "str", "default": ""},
      bones={"type": "any", "default": None},
      auto_weight={"type": "bool", "default": True})


# ─── Animation ─────────────────────────────────────────────────────────────────
_tool("insert_keyframe", "insert_keyframe",
      "Sisipkan keyframe (location/rotation_euler/scale/...) pada sebuah frame.",
      object_name="str", frame={"type": "int", "default": 1},
      property={"type": "str", "default": "location"})
_tool("animate_location", "animate_location",
      "Animasi objek dari A ke B antara dua frame.",
      object_name="str", start_frame={"type": "int", "default": 1},
      end_frame={"type": "int", "default": 30},
      start_loc={"type": "vec", "default": (0, 0, 0)},
      end_loc={"type": "vec", "default": (5, 0, 0)},
      interpolation={"type": "str", "default": "BEZIER"})
_tool("animate_rotation", "animate_rotation",
      "Putar objek N putaran mengelilingi sumbu.",
      object_name="str", start_frame={"type": "int", "default": 1},
      end_frame={"type": "int", "default": 30},
      revolutions={"type": "float", "default": 1.0},
      axis={"type": "str", "default": "Z"},
      start_rotation={"type": "vec", "default": (0, 0, 0)},
      interpolation={"type": "str", "default": "BEZIER"})
_tool("animate_scale", "animate_scale",
      "Animasi skala objek antara dua frame.",
      object_name="str", start_frame={"type": "int", "default": 1},
      end_frame={"type": "int", "default": 30},
      start_scale={"type": "vec", "default": (1, 1, 1)},
      end_scale={"type": "vec", "default": (2, 2, 2)},
      interpolation={"type": "str", "default": "BEZIER"})
_tool("keyframe_animation", "keyframe_animation",
      "Sisipkan keyframe di beberapa frame dengan nilai yang cocok.",
      object_name="str", property={"type": "str", "default": "location"},
      frames={"type": "vec", "default": [1, 30]},
      values={"type": "vec", "default": [[0, 0, 0], [5, 0, 0]]},
      interpolation={"type": "str", "default": "BEZIER"})
_tool("set_render_range", "set_render_range",
      "Atur rentang frame animasi.", start={"type": "int", "default": 1},
      end={"type": "int", "default": 250})
_tool("set_frame", "set_frame",
      "Lompat timeline ke sebuah frame.", frame={"type": "int", "default": 1})
_tool("create_action", "create_action",
      "Buat datablock Action dan tetapkan ke objek.",
      object_name="str", action_name={"type": "str", "default": ""})
_tool("list_actions", "list_actions",
      "Daftar semua action di file.", read_only=True)
_tool("set_keyframe_interpolation", "set_keyframe_interpolation",
      "Atur interpolasi CONSTANT/LINEAR/BEZIER pada action objek.",
      object_name="str", interpolation={"type": "str", "default": "LINEAR"})
_tool("add_shape_key", "add_shape_key",
      "Tambah shape key (opsional di-keyframe).",
      object_name="str", name={"type": "str", "default": "Key"},
      value={"type": "float", "default": 0.0},
      frame={"type": "int", "default": 1},
      keyframe={"type": "bool", "default": False})
_tool("list_shape_keys", "list_shape_keys",
      "Daftar shape key mesh.", read_only=True, object_name="str")
_tool("add_rigid_body", "add_rigid_body",
      "Jadikan objek rigid body (memerlukan UI).",
      object_name="str", body_type={"type": "str", "default": "ACTIVE"},
      mass={"type": "float", "default": 1.0},
      friction={"type": "float", "default": 0.5},
      bounciness={"type": "float", "default": 0.0},
      shape={"type": "str", "default": "CONVEX_HULL"},
      animate={"type": "bool", "default": False})
_tool("set_gravity", "set_gravity",
      "Atur gravitasi scene.", gravity={"type": "vec", "default": (0, 0, -9.81)})
_tool("clear_keyframes", "clear_keyframes",
      "Hapus semua keyframe properti dari action objek ('all' = semua).",
      object_name="str", property={"type": "str", "default": "location"})

_tool("animate_from_scratch", "animate_from_scratch",
      "Bersihkan animasi lama lalu buat gerak lokasi/rotasi lengkap beserta rentang frame.",
      object_name="str", start_frame={"type": "int", "default": 1},
      end_frame={"type": "int", "default": 48},
      start_loc={"type": "vec", "default": None},
      end_loc={"type": "vec", "default": None},
      revolutions={"type": "float", "default": 0.0},
      axis={"type": "str", "default": "Z"},
      interpolation={"type": "str", "default": "BEZIER"},
      set_range={"type": "bool", "default": True})


# ─── Scene / lights / camera / render ──────────────────────────────────────────
_tool("create_light", "create_light",
      "Buat cahaya POINT/SUN/SPOT/AREA.",
      name={"type": "str", "default": "Light"},
      light_type={"type": "str", "default": "POINT"},
      energy={"type": "float", "default": 10.0},
      color={"type": "vec", "default": (1, 1, 1)},
      location={"type": "vec", "default": (0, 4, 0)},
      spot_angle={"type": "float", "default": 45.0},
      area_size={"type": "float", "default": 1.0},
      shadow={"type": "bool", "default": True})
_tool("setup_three_point_lighting", "setup_three_point_lighting",
      "Cahaya key + fill + rim mengelilingi bounding box objek.",
      target_name="str", intensity={"type": "float", "default": 1.0})
_tool("create_camera", "create_camera",
      "Buat kamera.",
      name={"type": "str", "default": "Camera"},
      location={"type": "vec", "default": (5, -5, 4)},
      rotation="vec", lens={"type": "float", "default": 50.0},
      clip_start={"type": "float", "default": 0.1},
      clip_end={"type": "float", "default": 1000.0})
_tool("set_camera_target", "set_camera_target",
      "Buat kamera melacak objek target.",
      camera_name="str", target_name="str")
_tool("set_camera_active", "set_camera_active",
      "Jadikan kamera sebagai kamera aktif scene.", camera_name="str")
_tool("set_render_engine", "set_render_engine",
      "Atur engine render: CYCLES / EEVEE / WORKBENCH.",
      engine={"type": "str", "default": "CYCLES"})
_tool("set_render_resolution", "set_render_resolution",
      "Atur resolusi render.",
      width={"type": "int", "default": 1920},
      height={"type": "int", "default": 1080},
      percentage={"type": "int", "default": 100})
_tool("set_render_samples", "set_render_samples",
      "Atur sample untuk engine aktif (Cycles/EEVEE).",
      samples={"type": "int", "default": 64})
_tool("set_cycles_device", "set_cycles_device",
      "Atur device Cycles: CPU / GPU / OPTIX / CUDA / HIP / METAL.",
      device={"type": "str", "default": "CPU"})
_tool("render_frame", "render_frame",
      "Render frame saat ini (write_still).",
      filepath={"type": "str", "default": ""})
_tool("render_viewport_to_path", "render_viewport_to_path",
      "Render ke path file eksplisit.", filepath="str")
_tool("scene_summary", "scene_summary",
      "Ringkasan scene lengkap: jumlah, rentang frame, engine.",
      read_only=True)
_tool("cleanup_scene", "cleanup_scene",
      "Bersihkan datablock yatim dan normalkan nama.",
      purge_unused={"type": "bool", "default": True})
_tool("purge_orphans", "purge_orphans",
      "Hapus datablock yang tidak dipakai.")
_tool("select_by_type", "select_by_type",
      "Pilih semua objek sesuai tipe.", object_type={"type": "str", "default": "MESH"})
_tool("hide_object", "hide_object",
      "Sembunyikan/tampilkan objek.", object_name="str",
      hide={"type": "bool", "default": True})
_tool("unhide_all", "unhide_all",
      "Tampilkan semua objek.")
_tool("set_scene_name", "set_scene_name",
      "Ganti nama scene saat ini.", name={"type": "str", "default": "Scene"})

# ─── UV / texturing ────────────────────────────────────────────────────────────
_tool("add_uv_map", "add_uv_map",
      "Tambah layer UV ke mesh.",
      object_name="str", name={"type": "str", "default": "UVMap"})
_tool("unwrap_object", "unwrap_object",
      "Unwrap mesh: proyeksi SMART/PLANAR/CUBE/SPHERE/CYLINDER. Aman di background.",
      object_name="str", method={"type": "str", "default": "SMART"},
      name={"type": "str", "default": "UVMap"})
_tool("list_uv_maps", "list_uv_maps",
      "Daftar layer UV mesh.", read_only=True, object_name="str")
_tool("remove_uv_map", "remove_uv_map",
      "Hapus layer UV.", object_name="str", name="str")
_tool("texel_density", "texel_density",
      "Skala ulang UV menuju texel density.",
      object_name="str", density={"type": "float", "default": 10.0})

# ─── 3D printing ───────────────────────────────────────────────────────────────
_tool("check_manifold", "check_manifold",
      "Analisis watertight: edge boundary/non-manifold, lubang, Euler.",
      read_only=True, object_name="str")
_tool("set_dimensions_mm", "set_dimensions_mm",
      "Skala objek ke dimensi milimeter presisi.",
      object_name="str", width_mm="float", height_mm="float", depth_mm="float")
_tool("add_wall_thickness", "add_wall_thickness",
      "Ketebalan kulit via Solidify (mm).",
      object_name="str", thickness_mm={"type": "float", "default": 2.0})
_tool("bed_layout", "bed_layout",
      "Susun objek dalam grid di print bed.",
      object_names="strlist",
      bed_width_mm={"type": "float", "default": 220.0},
      bed_height_mm={"type": "float", "default": 220.0},
      margin_mm={"type": "float", "default": 5.0})
_tool("export_stl_mm", "export_stl_mm",
      "Export STL dalam milimeter.",
      filepath="str", object_name={"type": "str", "default": ""})

# ─── Batch ─────────────────────────────────────────────────────────────────────
_tool("batch_rename", "batch_rename",
      "Ganti nama objek: prefix+indeks atau search/replace.",
      prefix={"type": "str", "default": ""},
      search={"type": "str", "default": ""},
      replace={"type": "str", "default": ""},
      start_index={"type": "int", "default": 1})
_tool("batch_delete_by_type", "batch_delete_by_type",
      "Hapus semua objek sesuai tipe.",
      object_type={"type": "str", "default": "EMPTY"})
_tool("apply_transforms_all", "apply_transforms_all",
      "Bakar transform untuk semua objek mesh.",
      types={"type": "strlist", "default": ["MESH"]})
_tool("batch_duplicate", "batch_duplicate",
      "Duplikat objek N kali dengan offset linear.",
      object_name="str", count={"type": "int", "default": 2},
      offset={"type": "vec", "default": (1, 0, 0)})
_tool("select_all", "select_all",
      "Pilih atau batalkan semua objek.",
      action={"type": "str", "default": "SELECT"})
_tool("batch_set_scale", "batch_set_scale",
      "Atur skala semua objek dengan tipe tertentu.",
      scale={"type": "vec", "default": (1, 1, 1)},
      types={"type": "strlist", "default": ["MESH", "CURVE"]})
_tool("batch_set_location", "batch_set_location",
      "Geser semua objek dengan vektor.",
      offset={"type": "vec", "default": (0, 0, 0)})

# ─── Analysis ──────────────────────────────────────────────────────────────────
_tool("get_objects_summary", "get_objects_summary",
      "Ringkasan per objek seluruh scene.", read_only=True)
_tool("get_object_detail_summary", "get_object_detail_summary",
      "Ringkasan mendalam satu objek: topologi, material, UV, tulang, ...",
      read_only=True, name="str")
_tool("get_blendfile_summary_datablocks", "get_blendfile_summary_datablocks",
      "Inventaris datablock file blend.", read_only=True)
_tool("mesh_analysis", "mesh_analysis",
      "Kualitas topologi: tris/quads/ngons, non-manifold, geometri lepas.",
      read_only=True, object_name="str")
_tool("analyze_performance", "analyze_performance",
      "Laporan anggaran poligon scene.", read_only=True)

# ─── Geometry nodes ────────────────────────────────────────────────────────────
_tool("add_geometry_nodes_modifier", "add_geometry_nodes_modifier",
      "Pasang modifier Geometry Nodes + node group ke objek.",
      object_name="str", name={"type": "str", "default": "GeometryNodes"})
_tool("list_gn_modifiers", "list_gn_modifiers",
      "Daftar modifier GN pada objek.", read_only=True, object_name="str")
_tool("scatter_instances", "scatter_instances",
      "Sebarkan objek instance di permukaan via GN.",
      object_name="str", instance_object="str",
      count={"type": "int", "default": 100},
      seed={"type": "int", "default": 0},
      scale={"type": "vec", "default": (1, 1, 1)})
_tool("gn_add_node", "gn_add_node",
      "Tambah node ke GN node group objek.",
      object_name="str",
      node_type={"type": "str", "default": "GeometryNodeTransform"},
      name={"type": "str", "default": ""})

# ─── Import / export ───────────────────────────────────────────────────────────
_tool("list_export_formats", "list_export_formats",
      "Daftar format export yang didukung.", read_only=True)
_tool("export_scene", "export_scene",
      "Export scene: glb/gltf/fbx/obj/stl/ply/usd/usdz/dae/x3d.",
      filepath="str", format={"type": "str", "default": "glb"})
_tool("export_selected", "export_selected",
      "Export objek yang dipilih.",
      filepath="str", format={"type": "str", "default": "glb"})
_tool("import_file", "import_file",
      "Import glb/gltf/fbx/obj/stl/ply/usd/usdz/dae.",
      filepath="str", format={"type": "str", "default": ""})


def run_tool(tool_name, arguments=None):
    """Dispatch a tool call (used by stdio_bridge). Returns a dict."""
    meta = TOOL_META.get(tool_name)
    if meta is None:
        return {"error": f"Tool tidak dikenal: {tool_name}"}
    args = arguments or {}
    b = get_blender()
    params = {}
    for p in meta["params"]:
        if p["name"] in args:
            params[p["name"]] = args[p["name"]]
        elif "default" in p:
            params[p["name"]] = p["default"]
    try:
        return b.send_command(meta["command"], params)
    except Exception as e:
        return {"error": str(e)}


def tool_schema():
    """JSON-RPC tools/list payload for SDK-less bridges."""
    out = []
    for name, meta in TOOL_META.items():
        props = {}
        required = []
        for p in meta["params"]:
            ptype = p["type"]
            schema_type = {
                "str": "string", "float": "number", "int": "integer",
                "bool": "boolean", "vec": "array", "strlist": "array",
            }.get(ptype)
            prop = {}
            if schema_type is not None:
                prop["type"] = schema_type
            if ptype in ("vec", "strlist"):
                prop["items"] = {"type": "number"} if ptype == "vec" \
                    else {"type": "string"}
            if "default" in p:
                prop["default"] = p["default"]
            else:
                required.append(p["name"])
            props[p["name"]] = prop
        out.append({
            "name": name,
            "description": meta["doc"],
            "inputSchema": {"type": "object", "properties": props,
                            "required": required},
        })
    return out
