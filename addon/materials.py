"""
materials.py — Perintah pewarnaan: material PBR, graf node shader,
tekstur, vertex color, transparansi, emisi. Aman di background (data API).
"""

import bpy
NODE_TYPE_MAP = {
    "bsdf_principled": "ShaderNodeBsdfPrincipled",
    "bsdf_diffuse": "ShaderNodeBsdfDiffuse",
    "bsdf_glossy": "ShaderNodeBsdfAnisotropic",
    "bsdf_transparent": "ShaderNodeBsdfTransparent",
    "bsdf_glass": "ShaderNodeBsdfGlass",
    "emission": "ShaderNodeEmission",
    "tex_image": "ShaderNodeTexImage",
    "tex_noise": "ShaderNodeTexNoise",
    "tex_wave": "ShaderNodeTexWave",
    "tex_checker": "ShaderNodeTexChecker",
    "tex_gradient": "ShaderNodeTexGradient",
    "tex_coord": "ShaderNodeTexCoord",
    "mapping": "ShaderNodeMapping",
    "mix_shader": "ShaderNodeMixShader",
    "mix_rgb": "ShaderNodeMixRGB",
    "rgb": "ShaderNodeRGB",
    "value": "ShaderNodeValue",
    "math": "ShaderNodeMath",
    "vector_math": "ShaderNodeVectorMath",
    "bump": "ShaderNodeBump",
    "normal": "ShaderNodeNormal",
    "uv_map": "ShaderNodeUVMap",
    "group": "ShaderNodeGroup",
    "separate_xyz": "ShaderNodeSeparateXYZ",
    "combine_xyz": "ShaderNodeCombineXYZ",
}


def _rgba(value, field="color"):
    if not isinstance(value, (list, tuple)) or len(value) not in (3, 4):
        raise ValueError(f"{field} harus berisi RGB atau RGBA.")
    result = tuple(float(component) for component in value)
    if len(result) == 3:
        result += (1.0,)
    if any(component < 0.0 or component > 1.0 for component in result):
        raise ValueError(f"Komponen {field} harus berada pada rentang 0..1.")
    return result


def _unit(value, field):
    result = float(value)
    if not 0.0 <= result <= 1.0:
        raise ValueError(f"{field} harus berada pada rentang 0..1.")
    return result


def _set_surface_method(material, mode):
    mode = str(mode).upper()
    if hasattr(material, "surface_render_method"):
        mapping = {
            "OPAQUE": "DITHERED",
            "CLIP": "DITHERED",
            "HASHED": "DITHERED",
            "BLEND": "BLENDED",
            "BLEND_PREVIEW": "BLENDED",
            "DITHERED": "DITHERED",
            "BLENDED": "BLENDED",
        }
        target = mapping.get(mode)
        if target is None:
            raise ValueError(f"Metode transparansi tidak valid: {mode}")
        material.surface_render_method = target
        return target
    if mode not in {"OPAQUE", "CLIP", "HASHED", "BLEND"}:
        raise ValueError(f"Blend mode tidak valid: {mode}")
    material.blend_method = mode
    return mode


def _get_material(name):
    return bpy.data.materials.get(name)


def _get_object(obj_name):
    return bpy.data.objects.get(obj_name) or bpy.context.view_layer.objects.active


def create_material(name="Material", color=(0.8, 0.8, 0.8, 1.0),
                    roughness=0.5, metallic=0.0, emission_color=None,
                    emission_strength=0.0, ior=1.45, alpha=1.0,
                    blend_mode="OPAQUE", transmission=0.0):
    """Buat material PBR (Principled BSDF). Aman di background."""
    if _get_material(name) is not None:
        return {"error": f"Material '{name}' sudah ada."}
    try:
        c = _rgba(color)
        roughness = _unit(roughness, "roughness")
        metallic = _unit(metallic, "metallic")
        transmission = _unit(transmission, "transmission")
        alpha = _unit(alpha, "alpha")
        ior = float(ior)
        if ior < 1.0:
            raise ValueError("ior harus >= 1.0.")
        ec = _rgba(emission_color or (1.0, 1.0, 1.0, 1.0), "emission_color")
        emission_strength = max(0.0, float(emission_strength))
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}

    mat = bpy.data.materials.new(name)
    try:
        mat.use_nodes = True
        mat.diffuse_color = c
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is None:
            bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        inputs = bsdf.inputs

        def _set(nama_alias, nilai):
            for nama in nama_alias:
                sock = inputs.get(nama)
                if sock is not None:
                    sock.default_value = nilai
                    return nama
            return None

        _set(("Base Color",), c)
        _set(("Roughness",), roughness)
        _set(("Metallic",), metallic)
        _set(("IOR",), ior)
        _set(("Alpha",), alpha)
        _set(("Transmission Weight", "Transmission"), transmission)
        if emission_strength > 0.0:
            _set(("Emission Color", "Emission"), ec)
            _set(("Emission Strength",), emission_strength)
        render_method = _set_surface_method(mat, blend_mode)
    except Exception as exc:
        bpy.data.materials.remove(mat)
        return {"error": f"Gagal membuat material: {exc}"}
    return {"status": "success", "material": mat.name,
            "color": list(c), "roughness": roughness, "metallic": metallic,
            "render_method": render_method}


def assign_material(object_name="", material_name=""):
    """Tetapkan material yang sudah ada ke data mesh/curve objek."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    mat = _get_material(material_name)
    if mat is None:
        return {"error": f"Material tidak ditemukan: {material_name}"}
    data = obj.data
    if data is None or not hasattr(data, "materials"):
        return {"error": f"{obj.name} tidak mendukung material."}
    # `mat in data.materials` melempar TypeError: koleksi Blender membandingkan
    # lewat nama, bukan lewat objeknya. Jadi dicek dari daftar nama slot.
    if mat.name not in [m.name for m in data.materials if m is not None]:
        data.materials.append(mat)
    if len(data.materials) > 0:
        # make it the active material slot
        try:
            obj.active_material_index = len(data.materials) - 1
        except Exception:
            pass
    return {"status": "success", "object": obj.name, "material": mat.name}


def list_materials():
    mats = [{"name": m.name, "users": getattr(m, "users", 0)}
            for m in bpy.data.materials]
    return {"count": len(mats), "materials": mats}


def set_color(object_name="", color=(1.0, 1.0, 1.0, 1.0)):
    """Atur Base Color material aktif objek."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    data = getattr(obj, "data", None)
    mats = getattr(data, "materials", None) if data else None
    if mats is None or len(mats) == 0:
        return {"error": f"{obj.name} belum punya material."}
    mat = mats[0]
    try:
        c = _rgba(color)
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}
    mat.diffuse_color = c
    if not mat.use_nodes:
        return {"status": "success", "object": obj.name, "material": mat.name,
                "color": list(c)}
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None or "Base Color" not in bsdf.inputs:
        return {"error": "Material tidak memiliki node Principled BSDF."}
    bsdf.inputs["Base Color"].default_value = c
    return {"status": "success", "object": obj.name, "material": mat.name,
            "color": list(c)}


def add_shader_node(material_name="", node_type="bsdf_principled", name=""):
    """Tambah node shader ke node tree material."""
    mat = _get_material(material_name)
    if mat is None:
        return {"error": f"Material tidak ditemukan: {material_name}"}
    ntype = NODE_TYPE_MAP.get(str(node_type).lower())
    if ntype is None:
        return {"error": f"Tipe node tidak dikenal: {node_type}. "
                         f"Tersedia: {', '.join(sorted(NODE_TYPE_MAP))}"}
    if not mat.use_nodes:
        mat.use_nodes = True
    tree = mat.node_tree
    node = tree.nodes.new(ntype)
    if name:
        node.name = name
    return {"status": "success", "material": mat.name, "node": node.name,
            "type": node.type}


def list_shader_nodes(material_name=""):
    mat = _get_material(material_name)
    if mat is None:
        return {"error": f"Material tidak ditemukan: {material_name}"}
    if not mat.use_nodes or mat.node_tree is None:
        return {"material": mat.name, "nodes": []}
    nodes = []
    for n in mat.node_tree.nodes:
        nodes.append({
            "name": n.name,
            "type": n.type,
            "inputs": [s.name for s in n.inputs],
            "outputs": [s.name for s in n.outputs],
        })
    return {"material": mat.name, "count": len(nodes), "nodes": nodes}


def set_node_value(material_name="", node_name="", input_name="", value=None):
    """Atur nilai default input node."""
    mat = _get_material(material_name)
    if mat is None:
        return {"error": f"Material tidak ditemukan: {material_name}"}
    if not mat.use_nodes or mat.node_tree is None:
        return {"error": "Material tidak memakai node."}
    node = mat.node_tree.nodes.get(node_name)
    if node is None:
        return {"error": f"Node tidak ditemukan: {node_name}"}
    socket = node.inputs.get(input_name)
    if socket is None:
        return {"error": f"Input '{input_name}' tidak ada di {node_name}. "
                         f"Tersedia: {[s.name for s in node.inputs]}"}
    socket.default_value = value
    return {"status": "success", "material": mat.name, "node": node.name,
            "input": input_name, "value": value}


def connect_shader_nodes(material_name="", from_node="", from_output="",
                         to_node="", to_input=""):
    """Hubungkan dua socket node."""
    mat = _get_material(material_name)
    if mat is None:
        return {"error": f"Material tidak ditemukan: {material_name}"}
    if not mat.use_nodes or mat.node_tree is None:
        return {"error": "Material tidak memakai node."}
    tree = mat.node_tree
    src = tree.nodes.get(from_node)
    dst = tree.nodes.get(to_node)
    if src is None:
        return {"error": f"Node sumber tidak ditemukan: {from_node}"}
    if dst is None:
        return {"error": f"Node tujuan tidak ditemukan: {to_node}"}
    out_sock = src.outputs.get(from_output)
    in_sock = dst.inputs.get(to_input)
    if out_sock is None:
        return {"error": f"Output '{from_output}' tidak ada di {from_node}."}
    if in_sock is None:
        return {"error": f"Input '{to_input}' tidak ada di {to_node}."}
    tree.links.new(out_sock, in_sock)
    return {"status": "success", "link": f"{from_node}.{from_output} -> "
                                        f"{to_node}.{to_input}"}


def remove_shader_node(material_name="", node_name=""):
    mat = _get_material(material_name)
    if mat is None:
        return {"error": f"Material tidak ditemukan: {material_name}"}
    if not mat.use_nodes or mat.node_tree is None:
        return {"error": "Material tidak memakai node."}
    node = mat.node_tree.nodes.get(node_name)
    if node is None:
        return {"error": f"Node tidak ditemukan: {node_name}"}
    mat.node_tree.nodes.remove(node)
    return {"status": "success", "removed": node_name}


def create_image_texture(name="Texture", width=1024, height=1024,
                         color=(1.0, 1.0, 1.0, 1.0)):
    """Buat datablock gambar prosedural dengan warna awal."""
    try:
        width, height = int(width), int(height)
        if width < 1 or height < 1:
            raise ValueError("Ukuran gambar harus positif.")
        rgba = _rgba(color)
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}
    img = bpy.data.images.new(name, width, height)
    img.generated_color = rgba
    return {"status": "success", "image": img.name, "size": list(img.size),
            "color": list(rgba)}


def assign_image_texture(material_name="", image_name="", connect=True):
    """Tambah node Image Texture ke material dan opsional menghubungkannya."""
    mat = _get_material(material_name)
    if mat is None:
        return {"error": f"Material tidak ditemukan: {material_name}"}
    img = bpy.data.images.get(image_name)
    if img is None:
        return {"error": f"Gambar tidak ditemukan: {image_name}"}
    if not mat.use_nodes:
        mat.use_nodes = True
    tree = mat.node_tree
    node = tree.nodes.new("ShaderNodeTexImage")
    node.image = img
    if connect:
        bsdf = tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            # Base Color adalah sambungan utamanya; tanpa ini tekstur yang
            # sudah ditempel tidak terlihat sama sekali saat render.
            if node.outputs.get("Color") and bsdf.inputs.get("Base Color"):
                tree.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
            if node.outputs.get("Alpha") and bsdf.inputs.get("Alpha"):
                tree.links.new(node.outputs["Alpha"], bsdf.inputs["Alpha"])
    return {"status": "success", "material": mat.name, "node": node.name,
            "image": img.name, "connected": bool(connect)}


def add_vertex_color(object_name="", layer_name="Col", color=(1.0, 1.0, 1.0, 1.0),
                     domain="CORNER", data_type="FLOAT_COLOR"):
    """Tambah layer warna dan cat seluruh elemennya dengan `color`.

    Memakai `color_attributes` (Blender 3.2+), bukan `vertex_colors` yang
    sudah usang dan terkunci di Byte/CORNER. Lewat sini domain POINT dan
    presisi float ikut tersedia, dan `vertex_colors` tetap dipakai sebagai
    cadangan untuk Blender lama.
    """
    obj = _get_object(object_name)
    if obj is None or obj.type != "MESH" or obj.data is None:
        return {"error": f"Objek mesh tidak ditemukan: {object_name}"}
    mesh = obj.data
    try:
        c = _rgba(color)
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}

    dom = str(domain).upper()
    if dom not in ("CORNER", "POINT"):
        return {"error": f"domain harus CORNER atau POINT, bukan: {domain}"}
    dtype = str(data_type).upper()
    if dtype not in ("FLOAT_COLOR", "BYTE_COLOR"):
        return {"error": f"data_type harus FLOAT_COLOR atau BYTE_COLOR, bukan: {data_type}"}

    if hasattr(mesh, "color_attributes"):
        existing = mesh.color_attributes.get(layer_name)
        if existing is not None:
            mesh.color_attributes.remove(existing)
        layer = mesh.color_attributes.new(name=layer_name, type=dtype, domain=dom)
        api = "color_attributes"
    else:
        layer = mesh.vertex_colors.new(name=layer_name)
        dom, dtype, api = "CORNER", "BYTE_COLOR", "vertex_colors"

    painted = 0
    for item in layer.data:
        try:
            item.color = c
            painted += 1
        except Exception:
            break

    # Layer aktif menentukan warna mana yang dipakai saat render/ekspor.
    try:
        if api == "color_attributes":
            mesh.color_attributes.active_color = layer
    except Exception:
        pass

    return {"status": "success", "object": obj.name, "layer": layer.name,
            "api": api, "domain": dom, "data_type": dtype,
            "painted": painted, "color": list(c)}


def set_emission(material_name="", color=(1.0, 1.0, 1.0, 1.0), strength=1.0):
    """Buat material memancar (emissive) via input Principled BSDF."""
    mat = _get_material(material_name)
    if mat is None:
        return {"error": f"Material tidak ditemukan: {material_name}"}
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        return {"error": "Material tidak memiliki Principled BSDF."}
    try:
        rgba = _rgba(color)
        strength = max(0.0, float(strength))
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}
    emission_socket = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    strength_socket = bsdf.inputs.get("Emission Strength")
    if emission_socket is None or strength_socket is None:
        return {"error": "Socket emisi tidak tersedia pada Principled BSDF."}
    emission_socket.default_value = rgba
    strength_socket.default_value = strength
    return {"status": "success", "material": mat.name, "strength": strength}


def set_transparency(material_name="", alpha=0.5, blend_mode="BLEND"):
    """Buat material transparan (alpha + metode blend)."""
    mat = _get_material(material_name)
    if mat is None:
        return {"error": f"Material tidak ditemukan: {material_name}"}
    if not mat.use_nodes:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    try:
        alpha = _unit(alpha, "alpha")
        render_method = _set_surface_method(mat, blend_mode)
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}
    if bsdf is not None and "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
    diffuse = tuple(mat.diffuse_color)
    mat.diffuse_color = (*diffuse[:3], alpha)
    return {"status": "success", "material": mat.name, "alpha": alpha,
            "render_method": render_method}


def colorize_from_scratch(object_name="", color=(0.2, 0.6, 0.9, 1.0),
                          roughness=0.4, metallic=0.1):
    """Sekali jalan: buat + tetapkan material PBR ke objek."""
    obj = _get_object(object_name)
    if obj is None:
        return {"error": f"Objek tidak ditemukan: {object_name}"}
    mat_name = f"Mat_{obj.name}"
    mat = _get_material(mat_name)
    if mat is None:
        r = create_material(mat_name, color, roughness, metallic)
        if "error" in r:
            return r
        mat = _get_material(mat_name)
    assign_material(obj.name, mat.name)
    return {"status": "success", "object": obj.name, "material": mat.name,
            "color": list(color), "roughness": roughness, "metallic": metallic}
