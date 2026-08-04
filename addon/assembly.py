import bpy
import mathutils
from mathutils import Vector, Matrix

class AssemblyEngine:
    """Motor de ensamblaje paramétrico para posicionamiento determinista."""
    
    @staticmethod
    def get_bbox_anchors(obj):
        """Calcula los 27 puntos de ancla de un objeto en espacio global (v2.0)."""
        bpy.context.view_layer.update()  # matrix_world puede estar desfasado
        mw = obj.matrix_world
        # El bbox se calcula en espacio LOCAL y se lleva a mundo UNA sola vez
        # al construir cada ancla. Transformar los córners aquí y volver a
        # multiplicar por matrix_world abajo aplicaba la matriz dos veces, y
        # las anclas caían lejos del objeto en cuanto éste no estaba en el
        # origen.
        corners = [Vector(c) for c in obj.bound_box]
        min_x = min(c.x for c in corners)
        max_x = max(c.x for c in corners)
        min_y = min(c.y for c in corners)
        max_y = max(c.y for c in corners)
        min_z = min(c.z for c in corners)
        max_z = max(c.z for c in corners)

        xs = {"MIN": min_x, "CENTER": (min_x + max_x) / 2, "MAX": max_x}
        ys = {"MIN": min_y, "CENTER": (min_y + max_y) / 2, "MAX": max_y}
        zs = {"MIN": min_z, "CENTER": (min_z + max_z) / 2, "MAX": max_z}

        anchors = {}
        for xk, xv in xs.items():
            for yk, yv in ys.items():
                for zk, zv in zs.items():
                    anchors[f"A_{xk}_{yk}_{zk}"] = mw @ Vector((xv, yv, zv))
        return anchors

    @staticmethod
    def snap_to_anchor(obj_move, obj_target, anchor_move_key, anchor_target_key):
        """Mueve un objeto para que un ancla específica coincida con la de otro objeto."""
        anchors_move = AssemblyEngine.get_bbox_anchors(obj_move)
        anchors_target = AssemblyEngine.get_bbox_anchors(obj_target)
        
        if anchor_move_key not in anchors_move or anchor_target_key not in anchors_target:
            return {"error": f"Anchor tidak valid: {anchor_move_key} atau {anchor_target_key}"}
            
        target_pos = anchors_target[anchor_target_key]
        current_pos = anchors_move[anchor_move_key]
        
        translation = target_pos - current_pos
        obj_move.location += translation
        
        return {"status": "SUCCESS", "translation": list(translation)}

    @staticmethod
    def snap_and_parent(obj_move, obj_target, anchor_move_key, anchor_target_key):
        """Snap determinista y vinculación jerárquica automática."""
        result = AssemblyEngine.snap_to_anchor(obj_move, obj_target, anchor_move_key, anchor_target_key)
        if "error" in result:
            return result
            
        # Vincular manteniendo la transformación global.
        # matrix_world sólo refleja el snap que acabamos de hacer si el
        # depsgraph se reevalúa; sin esto se capturaba la matriz ANTERIOR al
        # movimiento y la línea siguiente la restauraba, anulando el snap.
        bpy.context.view_layer.update()
        mw_orig = obj_move.matrix_world.copy()
        obj_move.parent = obj_target
        obj_move.matrix_world = mw_orig
        
        return {"status": "SUCCESS_PARENTED", "parent": obj_target.name}

    @staticmethod
    def apply_symmetry(obj, axes=('X', 'Y')):
        """Aplica un modificador Mirror para asegurar simetría industrial."""
        mod_name = "AXIOM_Mirror"
        mod = obj.modifiers.get(mod_name) or obj.modifiers.new(mod_name, 'MIRROR')
        mod.use_axis[0] = 'X' in axes
        mod.use_axis[1] = 'Y' in axes
        mod.use_axis[2] = 'Z' in axes
        return {"status": "MIRROR_APPLIED", "axes": axes}

    @staticmethod
    def fix_normals(obj):
        """Recalcula las normales para asegurar colisiones correctas."""
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            return {"status": "NORMALS_FIXED"}
        return {"error": "Objek bukan mesh"}

    @staticmethod
    def _bounds(obj):
        """Extremos del bounding box en espacio global.

        Mutar `location` NO actualiza `matrix_world`: Blender lo recalcula al
        evaluar el depsgraph. Sin este update, cualquier medida tomada justo
        después de mover un objeto lee la posición anterior.
        """
        bpy.context.view_layer.update()
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        lo = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
        hi = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
        return lo, hi

    @staticmethod
    def align(objects, axis="Z", mode="MIN", reference=None):
        """Alinea objetos sobre un eje usando su bounding box real.

        Igualar `location` no alinea nada cuando los objetos tienen tamaños u
        orígenes distintos: hay que operar sobre el bbox.

        mode: MIN | CENTER | MAX  (cara inferior, centro o cara superior)
        reference: objeto que define el destino; por defecto el primero.
        """
        axis = axis.upper()
        mode = mode.upper()
        if axis not in ("X", "Y", "Z"):
            return {"error": f"Eje no válido: {axis}"}
        if mode not in ("MIN", "CENTER", "MAX"):
            return {"error": f"Modo no válido: {mode}"}
        if len(objects) < 2:
            return {"error": "Se necesitan al menos 2 objetos"}

        i = "XYZ".index(axis)

        def coord(obj):
            lo, hi = AssemblyEngine._bounds(obj)
            if mode == "MIN":
                return lo[i]
            if mode == "MAX":
                return hi[i]
            return (lo[i] + hi[i]) / 2

        ref = reference or objects[0]
        target = coord(ref)

        moved = []
        for obj in objects:
            if obj is ref:
                continue
            delta = target - coord(obj)
            if abs(delta) > 1e-9:
                obj.location[i] += delta
                moved.append({"name": obj.name, "delta": round(delta, 6)})
        return {"status": "ALIGNED", "axis": axis, "mode": mode,
                "reference": ref.name, "moved": moved}

    @staticmethod
    def distribute(objects, axis="X", spacing=None):
        """Reparte objetos a lo largo de un eje.

        spacing=None → separación uniforme entre los dos extremos actuales.
        spacing=<m>  → hueco fijo en metros entre bbox consecutivos.
        """
        axis = axis.upper()
        if axis not in ("X", "Y", "Z"):
            return {"error": f"Eje no válido: {axis}"}
        if len(objects) < 3 and spacing is None:
            return {"error": "Se necesitan al menos 3 objetos (o indica 'spacing')"}

        i = "XYZ".index(axis)
        ordered = sorted(objects, key=lambda o: AssemblyEngine._bounds(o)[0][i])

        placed = []
        if spacing is None:
            # Conserva los extremos y reparte el resto a intervalos iguales.
            first_c = sum(AssemblyEngine._bounds(ordered[0])[k][i] for k in (0, 1)) / 2
            last_c = sum(AssemblyEngine._bounds(ordered[-1])[k][i] for k in (0, 1)) / 2
            step = (last_c - first_c) / (len(ordered) - 1)
            for n, obj in enumerate(ordered[1:-1], start=1):
                lo, hi = AssemblyEngine._bounds(obj)
                center = (lo[i] + hi[i]) / 2
                obj.location[i] += (first_c + step * n) - center
                placed.append(obj.name)
        else:
            cursor = AssemblyEngine._bounds(ordered[0])[1][i]
            for obj in ordered[1:]:
                lo, hi = AssemblyEngine._bounds(obj)
                obj.location[i] += (cursor + spacing) - lo[i]
                cursor = cursor + spacing + (hi[i] - lo[i])
                placed.append(obj.name)

        return {"status": "DISTRIBUTED", "axis": axis,
                "spacing": spacing, "order": [o.name for o in ordered],
                "moved": placed}

    @staticmethod
    def array(obj, count=3, axis="X", gap=0.0, linked=False):
        """Duplica un objeto en fila, separado por su propio tamaño más `gap`.

        A diferencia del modificador Array, produce objetos reales
        seleccionables e independientes.
        """
        axis = axis.upper()
        if axis not in ("X", "Y", "Z"):
            return {"error": f"Eje no válido: {axis}"}
        if count < 2:
            return {"error": "count debe ser >= 2"}

        i = "XYZ".index(axis)
        lo, hi = AssemblyEngine._bounds(obj)
        pitch = (hi[i] - lo[i]) + gap

        created = []
        for n in range(1, count):
            copy = obj.copy()
            # linked comparte la malla: barato en memoria, edición compartida.
            if not linked and obj.data is not None:
                copy.data = obj.data.copy()
            for coll in obj.users_collection:
                coll.objects.link(copy)
            copy.location[i] += pitch * n
            created.append(copy.name)

        return {"status": "ARRAYED", "source": obj.name, "axis": axis,
                "count": count, "pitch": round(pitch, 6), "created": created}
