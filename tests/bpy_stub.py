"""
bpy_stub.py — Headless fake of bpy/bmesh/mathutils for offline tests.

Mirrors the *stable, documented* Blender data API surface used by the
blender-mcp command modules. Never a substitute for real Blender validation
(validate_tools.py against `blender -b` does that), but it proves dispatch
wiring, parameter handling, return shapes, and absence of NameError /
AttributeError across the whole command surface.

Target API level: Blender 4.2 LTS .. 5.x.
"""
import sys
import math
import types
from contextlib import contextmanager


# ─────────────────────────────────────────────────────────────────────────────
# mathutils
# ─────────────────────────────────────────────────────────────────────────────
class Vector:
    __slots__ = ("_v",)

    def __init__(self, values=(0.0, 0.0, 0.0)):
        self._v = [float(x) for x in values]

    @property
    def x(self):
        return self._v[0] if len(self._v) > 0 else 0.0

    @property
    def y(self):
        return self._v[1] if len(self._v) > 1 else 0.0

    @property
    def z(self):
        return self._v[2] if len(self._v) > 2 else 0.0

    @property
    def w(self):
        return self._v[3] if len(self._v) > 3 else 1.0

    @x.setter
    def x(self, v):
        while len(self._v) < 3:
            self._v.append(0.0)
        self._v[0] = float(v)

    @y.setter
    def y(self, v):
        while len(self._v) < 3:
            self._v.append(0.0)
        self._v[1] = float(v)

    @z.setter
    def z(self, v):
        while len(self._v) < 3:
            self._v.append(0.0)
        self._v[2] = float(v)

    def __len__(self):
        return len(self._v)

    def __iter__(self):
        return iter(self._v)

    def __getitem__(self, i):
        return self._v[i]

    def __setitem__(self, i, v):
        self._v[i] = float(v)

    def __add__(self, other):
        return Vector(a + b for a, b in zip(self._v, other))

    def __radd__(self, other):
        return Vector(a + b for a, b in zip(other, self._v))

    def __sub__(self, other):
        return Vector(a - b for a, b in zip(self._v, other))

    def __neg__(self):
        return Vector(-a for a in self._v)

    def __abs__(self):
        return Vector(abs(a) for a in self._v)

    def __mul__(self, other):
        if isinstance(other, Vector):
            return Vector(a * b for a, b in zip(self._v, other))
        return Vector(a * other for a in self._v)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        return Vector(a / other for a in self._v)

    def __matmul__(self, other):
        # matrix @ vector
        if isinstance(other, Vector):
            m = self if isinstance(self, Matrix) else None
            if isinstance(self, Matrix):
                return m._transform(other)
        if isinstance(self, Matrix):
            return self._transform(other)
        raise TypeError("Vector @ requires a Matrix")

    def __eq__(self, other):
        return list(self._v) == list(other)

    def __hash__(self):
        return hash(tuple(self._v))

    def __repr__(self):
        return f"Vector({tuple(round(v, 4) for v in self._v)})"

    def __str__(self):
        return f"<Vector {tuple(round(v, 4) for v in self._v)}>"

    @property
    def length(self):
        return math.sqrt(sum(a * a for a in self._v))

    @property
    def length_squared(self):
        return sum(a * a for a in self._v)

    def normalize(self):
        l = self.length
        if l > 1e-12:
            self._v = [a / l for a in self._v]
        return self

    def normalized(self):
        v = Vector(self._v)
        return v.normalize()

    def copy(self):
        return Vector(self._v)

    def dot(self, other):
        return sum(a * b for a, b in zip(self._v, other))

    def cross(self, other):
        return Vector(
            (
                self._v[1] * other[2] - self._v[2] * other[1],
                self._v[2] * other[0] - self._v[0] * other[2],
                self._v[0] * other[1] - self._v[1] * other[0],
            )
        )

    def lerp(self, other, t):
        return Vector(a + (b - a) * t for a, b in zip(self._v, other))

    def to_tuple(self):
        return tuple(self._v)

    def to_list(self):
        return list(self._v)

    def xyz(self):
        return Vector(self._v[:3])


class Matrix:
    def __init__(self, rows=None):
        self._m = rows if rows is not None else [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]

    @staticmethod
    def Identity(n=4):
        return Matrix(
            [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        )

    @staticmethod
    def Translation(vec):
        m = Matrix.Identity(4)
        for i in range(3):
            m._m[i][3] = float(vec[i])
        return m

    @staticmethod
    def Rotation(angle, size, axis=None):
        # size=4 -> 4x4 rotation about axis
        if size == 4 and axis is not None:
            a = float(angle)
            c, s = math.cos(a), math.sin(a)
            x, y, z = axis
            m = Matrix.Identity(4)
            m._m[0][0] = c + x * x * (1 - c)
            m._m[0][1] = x * y * (1 - c) - z * s
            m._m[0][2] = x * z * (1 - c) + y * s
            m._m[1][0] = y * x * (1 - c) + z * s
            m._m[1][1] = c + y * y * (1 - c)
            m._m[1][2] = y * z * (1 - c) - x * s
            m._m[2][0] = z * x * (1 - c) - y * s
            m._m[2][1] = z * y * (1 - c) + x * s
            m._m[2][2] = c + z * z * (1 - c)
            return m
        return Matrix.Identity(4)

    @staticmethod
    def Scale(vec):
        m = Matrix.Identity(4)
        for i in range(3):
            m._m[i][i] = float(vec[i])
        return m

    def __getitem__(self, i):
        return self._m[i]

    def __iter__(self):
        return iter(self._m)

    def __len__(self):
        return len(self._m)

    def copy(self):
        return Matrix([row[:] for row in self._m])

    @property
    def translation(self):
        return Vector((self._m[0][3], self._m[1][3], self._m[2][3]))

    @translation.setter
    def translation(self, vec):
        for i in range(3):
            self._m[i][3] = float(vec[i])

    def _transform(self, v):
        out = []
        for row in self._m[:3]:
            out.append(sum(row[j] * v[j] for j in range(3)) + row[3])
        return Vector(out)

    def __matmul__(self, other):
        if isinstance(other, Vector):
            return self._transform(other)
        if isinstance(other, Matrix):
            a, b = self._m, other._m
            res = [[0.0] * 4 for _ in range(4)]
            for i in range(4):
                for j in range(4):
                    res[i][j] = sum(a[i][k] * b[k][j] for k in range(4))
            return Matrix(res)
        raise TypeError("Matrix @ requires Matrix or Vector")

    def to_3x3(self):
        return Matrix([row[:3] + [0.0] for row in self._m])

    def to_quaternion(self):
        return Quaternion()

    def __repr__(self):
        return f"Matrix({self._m})"


class Euler:
    def __init__(self, x=0.0, y=0.0, z=0.0, order="XYZ"):
        self.x, self.y, self.z, self.order = float(x), float(y), float(z), order

    def to_quaternion(self):
        return Quaternion()

    def copy(self):
        return Euler(self.x, self.y, self.z, self.order)

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getitem__(self, i):
        return (self.x, self.y, self.z)[i]

    def __len__(self):
        return 3


class Quaternion:
    def __init__(self, w=1.0, x=0.0, y=0.0, z=0.0):
        self.w, self.x, self.y, self.z = float(w), float(x), float(y), float(z)

    def to_euler(self, order="XYZ"):
        return Euler()

    def copy(self):
        return Quaternion(self.w, self.x, self.y, self.z)


class _BvhTree:
    def overlap(self, other):
        return []


def _bvhtree_from_object(obj, dg=None):
    return _BvhTree()


# ─────────────────────────────────────────────────────────────────────────────
# bpy registry plumbing
# ─────────────────────────────────────────────────────────────────────────────
def _unique_name(registry, name):
    base = name
    i = 1
    while any(getattr(d, "name", None) == name for d in registry):
        name = f"{base}.{i:03d}"
        i += 1
    return name


_SHARED_OBJECTS = []  # satu daftar untuk bpy.data.objects + scene/view_layer


class Registry:
    """dict-like datablock collection mirroring bpy.data.<type>."""

    def __init__(self, factory=None):
        self._items = []
        self._factory = factory

    def new(self, name, data=None, **kw):
        if data is None and kw:
            data = kw.get("type") or kw.get("object") or next(iter(kw.values()), None)
        if self._factory is not None:
            obj = self._factory(_unique_name(self._items, name), data)
        else:
            obj = _Data(name)
        obj.users = 1
        self._items.append(obj)
        return obj

    def get(self, name, default=None):
        for d in self._items:
            if d.name == name:
                return d
        return default

    def remove(self, item, do_unlink=True, do_id_user=True, do_ui_user=True):
        if item in self._items:
            self._items.remove(item)

    def values(self):
        return list(self._items)

    def __getitem__(self, name):
        for d in self._items:
            if d.name == name:
                return d
        raise KeyError(name)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __contains__(self, name):
        return any(d.name == name for d in self._items)

    def __repr__(self):
        return f"Registry({[d.name for d in self._items]})"


class _Data:
    def __init__(self, name):
        self.name = name
        self.users = 1

    def __repr__(self):
        return f"<{type(self).__name__} {self.name!r}>"


# ─────────────────────────────────────────────────────────────────────────────
# data structures
# ─────────────────────────────────────────────────────────────────────────────
class Vertex:
    def __init__(self, co, index=0):
        self.co = Vector(co)
        self.index = index
        self.hide = False
        self.select = False

    @property
    def normal(self):
        return Vector((0.0, 0.0, 1.0))


class Edge:
    def __init__(self, vertices, index=0):
        self.vertices = vertices
        self.index = index
        self.select = False

    @property
    def is_manifold(self):
        return False


class Loop:
    def __init__(self, vert, face, index=0):
        self.vert = vert
        self.face = face
        self.index = index
        self._uv = {}

    def __getitem__(self, uv_layer):
        if uv_layer not in self._uv:
            self._uv[uv_layer] = _UV(uv_layer)
        return self._uv[uv_layer]


class _UV:
    def __init__(self, layer):
        self.uv = Vector((0.0, 0.0))
        self.layer = layer


class Polygon:
    def __init__(self, vertices, index=0):
        self.vertices = vertices  # list[int]
        self.index = index
        self.material_index = 0
        self.select = False

    @property
    def normal(self):
        if len(self.vertices) >= 3:
            # first non-degenerate triangle
            vs = self.vertices
            return _tri_normal(vs[0].co, vs[1].co, vs[2].co)
        return Vector((0.0, 0.0, 1.0))

    @property
    def loop_total(self):
        return len(self.vertices)

    @property
    def loops(self):
        return [Loop(v, self, i) for i, v in enumerate(self.vertices)]

    @property
    def center(self):
        if not self.vertices:
            return Vector()
        return sum((v.co for v in self.vertices), Vector()) / len(self.vertices)


def _tri_normal(a, b, c):
    n = (b - a).cross(c - a)
    l = n.length
    if l < 1e-12:
        return Vector((0.0, 0.0, 1.0))
    return n / l


class UVLayer:
    def __init__(self, name):
        self.name = name


class VertexColorLayer:
    def __init__(self, name):
        self.name = name
        self.data = []


class MaterialList:
    def __init__(self):
        self._items = []

    def append(self, mat):
        self._items.append(mat)

    def clear(self):
        self._items.clear()

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]


class _MeshRegistry(Registry):
    """bpy.data.meshes — adds new_from_object (Blender 4.0+)."""

    def new_from_object(self, obj):
        src = obj.data
        if src is None or not hasattr(src, "vertices"):
            m = self.new(obj.name + "_eval")
            m.vertices = []
            return m
        m = self.new(obj.name + "_eval")
        m.vertices = [Vertex(v.co, i) for i, v in enumerate(src.vertices)]
        m.edges = [Edge(list(e.vertices)) for e in src.edges]
        m.polygons = [Polygon(list(p.vertices)) for p in src.polygons]
        return m


class BlendData:
    def __init__(self):
        self.objects = Registry(lambda n, d: Object(n, d))
        self.objects._items = _SHARED_OBJECTS
        self.meshes = _MeshRegistry(Mesh)
        self.materials = Registry(_Material)
        self.armatures = Registry(Armature)
        self.actions = Registry(Action)
        self.cameras = Registry(Camera)
        self.lights = Registry(lambda n, d: Light(n, d or "POINT"))
        self.curves = Registry(
            lambda n, d: TextCurve(n) if (d or "CURVE") == "FONT" else Curve(n, d or "CURVE")
        )
        self.images = Registry(Image)
        self.node_groups = Registry(lambda n, d: NodeTree(n, d or "GeometryNodeTree"))
        self.texts = Registry(_Data)
        self.fonts = Registry(lambda n, d: _Data(n))
        self.purge_orphans = lambda: None



class Mesh(_Data):
    def __init__(self, name, data=None):
        super().__init__(name)
        self.vertices = []
        self.edges = []
        self.polygons = []
        self.uv_layers = _ListWithNew(UVLayer)
        self.vertex_colors = _ListWithNew(VertexColorLayer)
        self.materials = MaterialList()
        self.shape_keys = None
        self.use_auto_smooth = False

    def from_pydata(self, vertices, edges, faces):
        self.vertices = [Vertex(v, i) for i, v in enumerate(vertices)]
        for i, e in enumerate(edges):
            self.edges.append(Edge(list(e), i))
        for i, f in enumerate(faces):
            self.polygons.append(Polygon(list(f), i))

    def update(self):
        pass

    @property
    def loop_triangles(self):
        return [p for p in self.polygons if len(p.vertices) == 3]


class Curve(_Data):
    def __init__(self, name, curve_type="CURVE"):
        super().__init__(name)
        self.curve_type = curve_type
        self.splines = _Splines()
        self.materials = MaterialList()
        self.extrude = 0.0
        self.bevel_depth = 0.0
        self.dimensions = "3D"
        self.size = 1.0
        self.font = None

    @property
    def body(self):
        return getattr(self, "_body", "")

    @body.setter
    def body(self, value):
        self._body = value


class Spline:
    def __init__(self, spline_type="BEZIER"):
        self.type = spline_type
        self.points = []
        self.bezier_points = []
        self.use_cyclic_u = False


class _Splines:
    def __init__(self):
        self._items = []

    def new(self, spline_type="BEZIER"):
        s = Spline(spline_type)
        self._items.append(s)
        return s

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class TextCurve(Curve):
    def __init__(self, name):
        super().__init__(name, "FONT")
        self._body = ""


class Armature(_Data):
    def __init__(self, name, data=None):
        super().__init__(name)
        self.bones = _BoneDict()
        self.edit_bones = _EditBones(self)
        self.pose = _Pose(self)
        self.collections = _ListWithNew(BoneCollection)
        self.layers = [True] + [False] * 31
        self.use_auto_ik = False


class Bone:
    def __init__(self, name):
        self.name = name
        self.head = Vector()
        self.tail = Vector((0.0, 0.0, 1.0))
        self.parent = None
        self.children = []
        self.use_deform = True
        self.use_connect = False
class EditBone(Bone):
    def __init__(self, name):
        super().__init__(name)
        self.roll = 0.0

    @property
    def length(self):
        return (self.tail - self.head).length


class _BoneDict:
    def __init__(self):
        self._items = {}

    def get(self, name, default=None):
        return self._items.get(name, default)

    def __getitem__(self, name):
        return self._items[name]

    def __iter__(self):
        return iter(self._items.values())

    def __len__(self):
        return len(self._items)

    def __contains__(self, name):
        return name in self._items


class _EditBones(_BoneDict):
    def __init__(self, armature):
        super().__init__()
        self._arm = armature

    def new(self, name=None):
        b = EditBone(name or "Bone")
        b.name = _unique_name(list(self._arm.bones._items.values()), b.name)
        self._items[b.name] = b
        self._arm.bones._items[b.name] = Bone(b.name)
        return b

    def remove(self, bone):
        self._items.pop(bone.name, None)
        self._arm.bones._items.pop(bone.name, None)


class BoneCollection:
    def __init__(self, name):
        self.name = name
        self.color = (0.0, 0.0, 0.0, 1.0)
        self.bones = []

    def assign(self, bone):
        """Blender 4.0+: BoneCollection.assign(bone) — terima Bone/EditBone."""
        if bone not in self.bones:
            self.bones.append(bone)
        return 1

class PoseBone:
    def __init__(self, bone):
        self.bone = bone
        self.name = bone.name
        self.constraints = _Constraints()
        self.matrix_basis = Matrix.Identity(4)
        self.parent = None
        self.location = Vector()
        self.rotation_euler = Euler()
        self.scale = Vector((1.0, 1.0, 1.0))

    @property
    def head(self):
        return Vector(self.bone.head)

    @property
    def tail(self):
        return Vector(self.bone.tail)

    @property
    def matrix(self):
        return Matrix.Identity(4)


class _Pose:
    def __init__(self, armature):
        self.bones = _PoseBoneDict(armature)


class _PoseBoneDict(_BoneDict):
    def __init__(self, armature):
        super().__init__()
        self._arm = armature

    def get(self, name, default=None):
        if name in self._items:
            return self._items[name]
        rest = self._arm.bones.get(name)
        if rest is not None:
            self._items[name] = PoseBone(rest)
            return self._items[name]
        return default

    def __getitem__(self, name):
        b = self.get(name)
        if b is None:
            raise KeyError(name)
        return b


class Constraint:
    def __init__(self, ctype):
        self.name = ctype
        self.type = ctype
        self.target = None
        self.targets = []
        self.subtarget = ""
        self.chain_count = 0
        self.pole_target = None
        self.pole_angle = 0.0
        self.influence = 1.0
        self.operation = None
        self.mix_mode = "REPLACE"


class _Constraints:
    def __init__(self):
        self._items = []

    def new(self, ctype):
        c = Constraint(ctype)
        c.name = _unique_name([x for x in self._items], ctype)
        self._items.append(c)
        return c

    def remove(self, c):
        if c in self._items:
            self._items.remove(c)

    def get(self, name, default=None):
        for c in self._items:
            if c.name == name:
                return c
        return default

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class Modifier:
    def __init__(self, name, mtype):
        self.name = name
        self.type = mtype
        self.use_axis = [True, False, False]
        self.operation = "DIFFERENCE"
        self.object = None
        self.count = 2
        self.relative_offset_displace = Vector((1.0, 0.0, 0.0))
        self.thickness = 0.01
        self.angle_degrees = 360.0
        self.steps = 16
        self.axis = "Y"
        self.levels = 1
        self.render_levels = 1
        self.width = 0.01
        self.segments = 1
        self.ratio = 0.5
        self.node_group = None
        self.offset = 0.0
        self.strength = 1.0
        self.vertex_group = ""
        self.use_apply_as_scale = False
        self.show_viewport = True


class _Modifiers:
    def __init__(self):
        self._items = []

    def new(self, name, mtype=None, type=None):
        if mtype is None:
            mtype = type
        m = Modifier(name, mtype)
        m.name = _unique_name([x for x in self._items], name)
        self._items.append(m)
        return m

    def remove(self, mod):
        if mod in self._items:
            self._items.remove(mod)

    def get(self, name, default=None):
        for m in self._items:
            if m.name == name:
                return m
        return default

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __contains__(self, name):
        return any(m.name == name for m in self._items)


class VertexGroup:
    def __init__(self, name):
        self.name = name
        self._weights = {}

    def add(self, indices, weight, vtype="ADD"):
        for i in indices:
            self._weights[int(i)] = float(weight)

    def weight(self, index):
        return self._weights.get(int(index), 0.0)

    def remove(self, indices=None):
        if indices is None:
            self._weights.clear()
        else:
            for i in indices:
                self._weights.pop(int(i), None)


class _VertexGroups:
    def __init__(self):
        self._items = []

    def new(self, name=None):
        vg = VertexGroup(name or "Group")
        vg.name = _unique_name([x for x in self._items], vg.name)
        self._items.append(vg)
        return vg

    def remove(self, vg):
        if vg in self._items:
            self._items.remove(vg)

    def get(self, name, default=None):
        for vg in self._items:
            if vg.name == name:
                return vg
        return default

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class Action(_Data):
    def __init__(self, name, data=None):
        super().__init__(name)
        self.fcurves = []
        self.groups = []
        self.frame_range = (0.0, 0.0)


class FCurve:
    def __init__(self, data_path="", index=0):
        self.data_path = data_path
        self.index = index
        self.interpolation = "BEZIER"
        self.keyframe_points = []

    def update(self):
        return None

class KeyframePoint:
    def __init__(self, frame, value=0.0):
        self.co = (float(frame), float(value))
        self.interpolation = "BEZIER"


class KeyBlock:
    def __init__(self, name):
        self.name = name
        self.value = 0.0
        self.keyframe_insert = None


class ShapeKeys:
    def __init__(self):
        self.key_blocks = _ListWithNew(KeyBlock)
        self.animation_data = None


class AnimationData:
    def __init__(self):
        self.action = None
        self.nla_tracks = []

    def action_create(self, name=None):
        self.action = Action(name or "Action")
        return self.action

    def action_ensure(self):
        return self.action

    def action_clear(self):
        self.action = None


class Image(_Data):
    def __init__(self, name, width=1024, height=1024):
        super().__init__(name)
        self.size = (width, height)
        self.filepath = ""
        self.source = "GENERATED"


class Camera(_Data):
    def __init__(self, name, data=None):
        super().__init__(name)
        self.lens = 50.0
        self.clip_start = 0.1
        self.clip_end = 1000.0
        self.type = "PERSP"
        self.angle = 0.7
        self.angle_x = 0.7
        self.angle_y = 0.5


class Light(_Data):
    def __init__(self, name, light_type="POINT"):
        super().__init__(name)
        self.type = light_type
        self.energy = 10.0
        self.color = (1.0, 1.0, 1.0)
        self.spot_size = math.radians(45.0)
        self.spot_blend = 0.15
        self.size = 1.0
        self.size_y = 1.0
        self.use_shadow = True


class Object(_Data):
    _DATA_TYPE = {
        "Mesh": "MESH", "Armature": "ARMATURE", "Camera": "CAMERA",
        "Light": "LIGHT", "Curve": "CURVE", "TextCurve": "FONT",
    }

    def __init__(self, name, object_data=None):
        super().__init__(name)
        self.type = self._DATA_TYPE.get(
            object_data.__class__.__name__, "EMPTY") if object_data else "EMPTY"
        self.data = object_data
        self._location = Vector()
        self._rotation_euler = Euler()
        self._rotation_quaternion = Quaternion()
        self._scale = Vector((1.0, 1.0, 1.0))
        self._matrix_world = Matrix.Identity(4)
        self.parent = None
        self.children = []
        self.constraints = _Constraints()
        self.modifiers = _Modifiers()
        self.vertex_groups = _VertexGroups()
        self.animation_data = None
        self.hide_viewport = False
        self.empty_display_type = "PLAIN_AXES"
        self.rotation_mode = "XYZ"
        self.use_shape_key_edit_mode = False
        self.lock_location = [False, False, False]
        self.lock_rotation = [False, False, False]
        self.lock_scale = [False, False, False]

    @property
    def pose(self):
        arm = getattr(self.data, "pose", None)
        if arm is None and self.type == "ARMATURE":
            arm = _Pose(self.data)
            self.data.pose = arm
        return arm
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, v):
        self._location = Vector(v)

    @property
    def rotation_euler(self):
        return self._rotation_euler

    @rotation_euler.setter
    def rotation_euler(self, v):
        if isinstance(v, Euler):
            self._rotation_euler = v
        else:
            self._rotation_euler = Euler(*v)

    @property
    def rotation_quaternion(self):
        return self._rotation_quaternion

    @rotation_quaternion.setter
    def rotation_quaternion(self, v):
        if isinstance(v, Quaternion):
            self._rotation_quaternion = v
        else:
            self._rotation_quaternion = Quaternion(*v)

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, v):
        self._scale = Vector(v)

    @property
    def matrix_world(self):
        m = Matrix.Translation(self._location)
        for i in range(3):
            m[i][i] *= self._scale[i]
        return m

    @matrix_world.setter
    def matrix_world(self, m):
        self._matrix_world = Matrix(m)
        self._location = Vector(self._matrix_world.translation)

    @property
    def bound_box(self):
        # 8 corners of a unit-ish box centered at origin, scaled
        s = self._scale
        hw = abs(s.x) * 0.5
        hh = abs(s.y) * 0.5
        hd = abs(s.z) * 0.5
        return [
            Vector((hw, hh, hd)), Vector((hw, hh, -hd)),
            Vector((hw, -hh, hd)), Vector((hw, -hh, -hd)),
            Vector((-hw, hh, hd)), Vector((-hw, hh, -hd)),
            Vector((-hw, -hh, hd)), Vector((-hw, -hh, -hd)),
        ]

    @property
    def dimensions(self):
        bb = self.bound_box
        xs = [v.x for v in bb]
        ys = [v.y for v in bb]
        zs = [v.z for v in bb]
        return Vector((max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))

    def hide_set(self, value, viewport=None):
        self.hide_viewport = bool(value)

    def hide_get(self):
        return self.hide_viewport

    def select_set(self, value, view_layer=None):
        self._selected = bool(value)

    def select_get(self):
        return getattr(self, "_selected", False)

    def select(self, value):
        self._selected = bool(value)

    def animation_data_create(self):
        if self.animation_data is None:
            self.animation_data = AnimationData()
        return self.animation_data

    def animation_data_ensure(self):
        return self.animation_data_create()

    def keyframe_insert(self, data_path, frame=-1, index=-1):
        ad = self.animation_data_create()
        if ad.action is None:
            action = Action(f"{self.name}Action")
            ad.action = action
        fc = next((f for f in ad.action.fcurves if f.data_path == data_path), None)
        if fc is None:
            fc = FCurve(data_path)
            ad.action.fcurves.append(fc)
        fc.keyframe_points.append(KeyframePoint(frame))
        return None

    def shape_key_add(self, name=None, from_mix=False):
        mesh = self.data
        if mesh is None:
            return None
        if mesh.shape_keys is None:
            mesh.shape_keys = ShapeKeys()
        kb = mesh.shape_keys.key_blocks.new(name or "Key")
        if not mesh.shape_keys.key_blocks._items:
            pass
        return kb

    def copy(self):
        dup = Object(_unique_name([], self.name), self.data)
        dup.location = Vector(self.location)
        dup.rotation_euler = Euler(self.rotation_euler.x, self.rotation_euler.y, self.rotation_euler.z)
        dup.scale = Vector(self.scale)
        return dup

    def evaluated_get(self, dg=None):
        return self

    def to_mesh(self):
        return self.data


class _ListWithNew:
    def __init__(self, factory):
        self._factory = factory
        self._items = []

    def new(self, name=None):
        obj = self._factory(name or self._factory.__name__)
        obj.name = _unique_name([x for x in self._items], obj.name)
        self._items.append(obj)
        return obj

    def get(self, name, default=None):
        for o in self._items:
            if o.name == name:
                return o
        return default

    def remove(self, item):
        if item in self._items:
            self._items.remove(item)

    def clear(self):
        self._items.clear()

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __contains__(self, name):
        return any(o.name == name for o in self._items)


class ObjectCollection:
    def __init__(self):
        self._items = _SHARED_OBJECTS
        self.active = None

    def link(self, obj):
        if obj not in self._items:
            self._items.append(obj)

    def unlink(self, obj):
        if obj in self._items:
            self._items.remove(obj)

    def get(self, name, default=None):
        for o in self._items:
            if o.name == name:
                return o
        return default

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __contains__(self, obj):
        return obj in self._items


class Scene(_Data):
    def __init__(self, name):
        super().__init__(name)
        self.objects = ObjectCollection()
        self.collection = _Collection(self.objects)
        self.frame_start = 1
        self.frame_end = 250
        self.frame_current = 1
        self.render = _RenderSettings()
        self.cycles = _Simple("cycles", samples=64, device="CPU", use_denoising=True)
        self.eevee = _Simple("eevee", taa_render_samples=16, use_raytracing=False, samples=16)
        self.unit_settings = _Simple("unit", scale_length=1.0, system="METRIC", length_unit="METERS")
        self.world = _Simple("world", use_nodes=False, node_tree=None)
        self.rigidbody_world = None
        self.gravity = Vector((0.0, 0.0, -9.81))
        self.use_gravity = True


class _Collection:
    def __init__(self, object_collection):
        self.objects = object_collection

    def link(self, obj):
        self.objects.link(obj)

    def unlink(self, obj):
        self.objects.unlink(obj)


class _Simple:
    def __init__(self, name, **kw):
        self.name = name
        for k, v in kw.items():
            setattr(self, k, v)


class _RenderSettings(_Simple):
    def __init__(self):
        super().__init__(
            "render",
            filepath="/tmp/render.png",
            resolution_x=1920,
            resolution_y=1080,
            resolution_percentage=100,
            engine="BLENDER_EEVEE_NEXT",
            film_transparent=False,
            use_file_extension=True,
        )
        self.image_settings = _Simple("image_settings", file_format="PNG")



class ViewLayer:
    def __init__(self):
        self.objects = ObjectCollection()
        self.name = "ViewLayer"
        self.update = lambda *a, **k: None


class WindowManager:
    def __init__(self):
        self.windows = []


class Context:
    def __init__(self):
        self.scene = Scene("Scene")
        self.view_layer = ViewLayer()
        self.window_manager = WindowManager()
        self.window = None
        self.area = None
        self.region = None
        self.mode = "OBJECT"
        self.collection = self.scene.collection
        self._selected = []

    @property
    def active_object(self):
        return self.view_layer.objects.active

    @active_object.setter
    def active_object(self, obj):
        self.view_layer.objects.active = obj

    @property
    def object(self):
        return self.view_layer.objects.active

    @property
    def selected_objects(self):
        return [o for o in self.view_layer.objects if o.select_get()]

    @property
    def selected_editable_objects(self):
        return self.selected_objects

    @contextmanager
    def temp_override(self, **kwargs):
        prev = {}
        for k, v in kwargs.items():
            if hasattr(self, k):
                prev[k] = getattr(self, k)
                setattr(self, k, v)
        try:
            yield self
        finally:
            for k, v in prev.items():
                setattr(self, k, v)

    def evaluated_depsgraph_get(self):
        return _Simple("depsgraph")


class _OpsRecorder:
    """Permissive bpy.ops stand-in: any chain returns {'FINISHED'}."""

    def __init__(self, parent=None, prefix=""):
        self._parent = parent
        self._prefix = prefix

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        child = _OpsRecorder(self, f"{self._prefix}{name}.")
        setattr(self, name, child)
        return child

    def __call__(self, *args, **kwargs):
        return {"FINISHED"}




# material node surface
class Socket:
    def __init__(self, name):
        self.name = name
        self.default_value = None
        self.links = []
        self.node = None
        self.type = "VALUE"

    def __repr__(self):
        return f"<Socket {self.name} = {self.default_value}>"


class _Sockets:
    def __init__(self, names):
        self._items = [Socket(n) for n in names]

    def __getitem__(self, name):
        for s in self._items:
            if s.name == name:
                return s
        raise KeyError(name)

    def get(self, name, default=None):
        for s in self._items:
            if s.name == name:
                return s
        return default

    def new(self, socket_type, name):
        sock = Socket(name)
        sock.type = socket_type
        self._items.append(sock)
        return sock

    def __contains__(self, name):
        return any(s.name == name for s in self._items)

    def __iter__(self):
        return iter(self._items)
    def __len__(self):
        return len(self._items)


class Node:
    def __init__(self, name, ntype):
        self.name = name
        self.type = ntype
        self.label = name
        self.location = (0.0, 0.0)
        self.width = 200.0
        self.inputs = _Sockets([])
        self.outputs = _Sockets([])
        self.image = None
        self.color = (0.6, 0.6, 0.6, 1.0)
        self.use_custom_color = False
        self.blend_type = "MIX"
        self.data_type = "FLOAT"
        self.mode = "MULTIPLY"


class Link:
    def __init__(self, from_socket, to_socket):
        self.from_socket = from_socket
        self.to_socket = to_socket
        self.is_valid = True

    def __repr__(self):
        return f"<Link {self.from_socket.name} -> {self.to_socket.name}>"


class NodeTree(_Data):
    def __init__(self, name, ntype):
        super().__init__(name)
        self.type = ntype
        self.nodes = _Nodes()
        self.links = _Links()
        self.inputs = _Sockets([])
        self.outputs = _Sockets([])


class _Nodes:
    def __init__(self):
        self._items = []

    def new(self, ntype, name=None):
        n = Node(name or _NODE_DEFAULT_NAME.get(ntype, ntype), ntype)
        n.name = _unique_name([x for x in self._items], n.name)
        n.inputs = _Sockets(_NODE_INPUTS.get(ntype, []))
        n.outputs = _Sockets(_NODE_OUTPUTS.get(ntype, []))
        for s in list(n.inputs) + list(n.outputs):
            s.node = n
        self._items.append(n)
        return n

    def remove(self, node):
        if node in self._items:
            self._items.remove(node)

    def get(self, name, default=None):
        for n in self._items:
            if n.name == name:
                return n
        return default

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __contains__(self, name):
        return any(n.name == name for n in self._items)


class _Links:
    def __init__(self):
        self._items = []

    def new(self, from_socket, to_socket):
        link = Link(from_socket, to_socket)
        self._items.append(link)
        from_socket.links.append(link)
        to_socket.links.append(link)
        return link

    def remove(self, link):
        if link in self._items:
            self._items.remove(link)
            if link in link.from_socket.links:
                link.from_socket.links.remove(link)
            if link in link.to_socket.links:
                link.to_socket.links.remove(link)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class _Material(_Data):
    def __init__(self, name, data=None):
        super().__init__(name)
        self.use_nodes = False
        self.node_tree = None
        self.blend_method = "OPAQUE"
        self.diffuse_color = (0.8, 0.8, 0.8, 1.0)
        self.metallic = 0.0
        self.roughness = 0.5
        self.use_nodes_auto = False

    @property
    def use_nodes(self):
        return self._use_nodes

    @use_nodes.setter
    def use_nodes(self, v):
        self._use_nodes = bool(v)
        if v and self.node_tree is None:
            tree = NodeTree(self.name + "_node_tree", "ShaderNodeTree")
            bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
            out = tree.nodes.new("ShaderNodeOutputMaterial")
            self.node_tree = tree
            self._principled = bsdf
            self._output = out


_NODE_DEFAULT_NAME = {
    "ShaderNodeBsdfPrincipled": "Principled BSDF",
    "ShaderNodeOutputMaterial": "Material Output",
    "ShaderNodeBsdfDiffuse": "Diffuse BSDF",
    "ShaderNodeBsdfGlossy": "Glossy BSDF",
    "ShaderNodeBsdfTransparent": "Transparent BSDF",
    "ShaderNodeEmission": "Emission",
    "ShaderNodeTexImage": "Image Texture",
    "ShaderNodeTexNoise": "Noise Texture",
    "ShaderNodeTexWave": "Wave Texture",
    "ShaderNodeTexChecker": "Checker Texture",
    "ShaderNodeTexCoord": "Texture Coordinate",
    "ShaderNodeMapping": "Mapping",
    "ShaderNodeMixShader": "Mix Shader",
    "ShaderNodeMixRGB": "Mix",
    "ShaderNodeRGB": "RGB",
    "ShaderNodeValue": "Value",
    "ShaderNodeMath": "Math",
    "ShaderNodeVectorMath": "Vector Math",
    "ShaderNodeBump": "Bump",
    "ShaderNodeNormal": "Normal",
    "ShaderNodeUVMap": "UV Map",
    "ShaderNodeGroup": "Group",
    "ShaderNodeSeparateXYZ": "Separate XYZ",
    "ShaderNodeCombineXYZ": "Combine XYZ",
    "ShaderNodeTexGradient": "Gradient Texture",
    "ShaderNodeBsdfGlass": "Glass BSDF",
    "ShaderNodeBsdfPrincipledHair": "Principled Hair BSDF",
}

_NODE_INPUTS = {
    "GeometryNodeDistributePointsOnFaces": ["Mesh", "Selection", "Density", "Seed", "Distribute Method", "Use Poisson Disk"],
    "GeometryNodeInstanceOnPoints": ["Points", "Selection", "Instance"],
    "GeometryNodeTransform": ["Geometry", "Translation", "Rotation", "Scale"],
    "GeometryNodeObjectInfo": ["Object"],
    "NodeGroupInput": [],
    "NodeGroupOutput": ["Geometry"],
    "ShaderNodeBsdfPrincipled": [
        "Base Color", "Subsurface", "Subsurface Radius", "Subsurface Color",
        "Metallic", "Specular", "Specular Tint", "Roughness", "Anisotropic",
        "Anisotropic Rotation", "Sheen", "Sheen Tint", "Clearcoat",
        "Clearcoat Roughness", "IOR", "Transmission", "Transmission Roughness",
        "Emission Color", "Emission Strength", "Alpha", "Normal",
        "Clearcoat Normal", "Tangent",
    ],
    "ShaderNodeOutputMaterial": ["Surface", "Volume", "Displacement", "Thickness"],
    "ShaderNodeBsdfDiffuse": ["Color", "Roughness", "Normal"],
    "ShaderNodeBsdfGlossy": ["Color", "Roughness", "Anisotropy", "Normal"],
    "ShaderNodeBsdfTransparent": ["Color", "Weight"],
    "ShaderNodeEmission": ["Color", "Strength", "Weight"],
    "ShaderNodeTexImage": ["Vector"],
    "ShaderNodeTexNoise": ["Vector", "W", "Scale", "Detail", "Roughness", "Distortion"],
    "ShaderNodeTexWave": ["Vector", "Scale", "Distortion", "Detail", "Detail Scale", "Phase", "Bands Direction", "Rings Direction"],
    "ShaderNodeTexChecker": ["Vector", "Color1", "Color2", "Scale"],
    "ShaderNodeTexCoord": [],
    "ShaderNodeMapping": ["Vector", "Location", "Rotation", "Scale"],
    "ShaderNodeMixShader": ["Fac", "Shader", "Shader_001"],
    "ShaderNodeMixRGB": ["Fac", "Color1", "Color2"],
    "ShaderNodeRGB": [],
    "ShaderNodeValue": [],
    "ShaderNodeMath": ["Value", "Value_001"],
    "ShaderNodeVectorMath": ["Vector", "Vector_001"],
    "ShaderNodeBump": ["Strength", "Distance", "Height", "Normal"],
    "ShaderNodeNormal": ["Normal"],
    "ShaderNodeUVMap": [],
    "ShaderNodeSeparateXYZ": ["Vector"],
    "ShaderNodeCombineXYZ": ["X", "Y", "Z"],
    "ShaderNodeTexGradient": ["Vector"],
    "ShaderNodeBsdfGlass": ["Color", "Roughness", "IOR", "Normal"],
    "ShaderNodeGroup": [],
}

_NODE_OUTPUTS = {
    "GeometryNodeDistributePointsOnFaces": ["Points"],
    "GeometryNodeInstanceOnPoints": ["Instances"],
    "GeometryNodeTransform": ["Geometry"],
    "GeometryNodeObjectInfo": ["Geometry", "Transform", "Location", "Rotation", "Scale"],
    "NodeGroupInput": ["Geometry"],
    "NodeGroupOutput": [],
    "ShaderNodeBsdfPrincipled": ["BSDF"],
    "ShaderNodeOutputMaterial": [],
    "ShaderNodeBsdfDiffuse": ["BSDF"],
    "ShaderNodeBsdfGlossy": ["BSDF"],
    "ShaderNodeBsdfTransparent": ["BSDF"],
    "ShaderNodeEmission": ["Emission"],
    "ShaderNodeTexImage": ["Color", "Alpha", "Vector"],
    "ShaderNodeTexNoise": ["Fac", "Color"],
    "ShaderNodeTexWave": ["Fac", "Color"],
    "ShaderNodeTexChecker": ["Fac", "Color"],
    "ShaderNodeTexCoord": ["Generated", "Normal", "UV", "Object", "Camera", "Window", "Reflection"],
    "ShaderNodeMapping": ["Vector"],
    "ShaderNodeMixShader": ["Shader"],
    "ShaderNodeMixRGB": ["Color"],
    "ShaderNodeRGB": ["Color"],
    "ShaderNodeValue": ["Value"],
    "ShaderNodeMath": ["Value"],
    "ShaderNodeVectorMath": ["Vector"],
    "ShaderNodeBump": ["Normal"],
    "ShaderNodeNormal": ["Normal", "Dot"],
    "ShaderNodeUVMap": ["UV"],
    "ShaderNodeSeparateXYZ": ["X", "Y", "Z"],
    "ShaderNodeCombineXYZ": ["Vector"],
    "ShaderNodeTexGradient": ["Color"],
    "ShaderNodeBsdfGlass": ["BSDF"],
}


# ─────────────────────────────────────────────────────────────────────────────
# bmesh
# ─────────────────────────────────────────────────────────────────────────────
class BMeshVert:
    def __init__(self, co, index=0):
        self.co = Vector(co)
        self.index = index
        self.hide = False
        self.select = False
        self.link_edges = []
        self.link_faces = []

    @property
    def normal(self):
        return Vector((0.0, 0.0, 1.0))


class BMeshEdge:
    def __init__(self, verts, index=0):
        self.verts = verts
        self.index = index
        self.select = False
        self.link_faces = []

    @property
    def is_manifold(self):
        return len(self.link_faces) == 2


class BMeshFace:
    def __init__(self, verts, index=0):
        self.verts = verts
        self.index = index
        self.select = False
        self.material_index = 0
        self._loops = None

    @property
    def normal(self):
        if len(self.verts) >= 3:
            return _tri_normal(self.verts[0].co, self.verts[1].co, self.verts[2].co)
        return Vector((0.0, 0.0, 1.0))

    @property
    def loops(self):
        if self._loops is None:
            self._loops = [BMeshLoop(v, self, i) for i, v in enumerate(self.verts)]
        return self._loops

    @property
    def calc_center_median(self):
        if not self.verts:
            return Vector()
        return sum((v.co for v in self.verts), Vector()) / len(self.verts)


class BMeshLoop:
    def __init__(self, vert, face, index=0):
        self.vert = vert
        self.face = face
        self.index = index
        self._uv = {}

    def __getitem__(self, uv_layer):
        if uv_layer not in self._uv:
            self._uv[uv_layer] = _UV(uv_layer)
        return self._uv[uv_layer]


class BMeshUVLayer:
    def __init__(self, name):
        self.name = name


class BMeshVertSeq:
    def __init__(self, bm):
        self.bm = bm

    def ensure_lookup_table(self):
        pass

    def new(self, co=(0.0, 0.0, 0.0)):
        v = BMeshVert(co, len(self.bm._verts))
        self.bm._verts.append(v)
        return v

    def __iter__(self):
        return iter(self.bm._verts)

    def __len__(self):
        return len(self.bm._verts)

    def __getitem__(self, i):
        return self.bm._verts[i]

    def __contains__(self, v):
        return v in self.bm._verts


class BMeshEdgeSeq:
    def __init__(self, bm):
        self.bm = bm

    def ensure_lookup_table(self):
        pass

    def new(self, verts):
        e = BMeshEdge(verts, len(self.bm._edges))
        self.bm._edges.append(e)
        return e

    def __iter__(self):
        return iter(self.bm._edges)

    def __len__(self):
        return len(self.bm._edges)


class BMeshFaceSeq:
    def __init__(self, bm):
        self.bm = bm

    def ensure_lookup_table(self):
        pass

    def new(self, verts):
        f = BMeshFace(verts, len(self.bm._faces))
        self.bm._faces.append(f)
        for v in verts:
            v.link_faces.append(f)
        return f

    def __iter__(self):
        return iter(self.bm._faces)

    def __len__(self):
        return len(self.bm._faces)


class BMeshUVSeq:
    def __init__(self):
        self._items = []

    def new(self, name="UVMap", **kwargs):
        if kwargs:
            raise TypeError("BMLayerCollection.new() takes no keyword arguments")
        layer = BMeshUVLayer(name)
        self._items.append(layer)
        return layer

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class BMesh:
    def __init__(self):
        self._verts = []
        self._edges = []
        self._faces = []
        self.verts = BMeshVertSeq(self)
        self.edges = BMeshEdgeSeq(self)
        self.faces = BMeshFaceSeq(self)
        self.loops = _Simple("loops", layers=_BMeshLayerSeq())
        self.select_history = []
        self.is_valid = True

    def from_mesh(self, mesh):
        for v in mesh.vertices:
            nv = BMeshVert(v.co)
            nv.index = len(self._verts)
            self._verts.append(nv)
        for e in mesh.edges:
            self._edges.append(BMeshEdge([self._verts[i] for i in e.vertices], len(self._edges)))
        for p in mesh.polygons:
            self._faces.append(BMeshFace([self._verts[i] for i in p.vertices], len(self._faces)))

    def to_mesh(self, mesh):
        mesh.vertices = [Vertex(v.co) for v in self._verts]
        mesh.edges = [Edge([v.index for v in e.verts]) for e in self._edges]
        mesh.polygons = [Polygon([v.index for v in f.verts]) for f in self._faces]

    def free(self):
        self.is_valid = False
        self._verts.clear()
        self._edges.clear()
        self._faces.clear()

    def normal_update(self):
        pass

    def copy(self):
        bm = BMesh()
        for v in self._verts:
            bm.verts.new(v.co)
        return bm

    def calc_loop_triangles(self):
        return []


class _BMeshLayerSeq:
    def __init__(self):
        self.uv = BMeshUVSeq()
        self.color = _ListWithNew(VertexColorLayer)


class _BMeshOps:
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)

        def _run(*args, **kwargs):
            return {"geom": list(kwargs.get("geom", []))}

        return _run


# ─────────────────────────────────────────────────────────────────────────────
# assemble the bpy module
# ─────────────────────────────────────────────────────────────────────────────
def _build():
    bpy = types.ModuleType("bpy")
    bpy.app = _Simple(
        "app",
        version=(5, 1, 0),
        version_string="5.1.0",
        background=False,
        debug_value=0,
        version_char="a",
    )
    bpy.context = Context()
    bpy.data = BlendData()
    bpy.ops = _OpsRecorder()
    bpy.types = _Simple("types")
    bpy.utils = _Simple("utils")
    types_mod = types.ModuleType("bpy.types")
    sys.modules["bpy.types"] = types_mod

    def _use_factory_nodes(tree, material):
        return material

    bpy.types.Node = Node
    bpy.types.Material = _Material
    bpy.types.Object = Object
    bpy.types.Mesh = Mesh
    bpy.types.Armature = Armature
    bpy.types.Scene = Scene
    class Operator:
        bl_idname = ""
        bl_label = ""
        bl_description = ""
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            return {"FINISHED"}

        def report(self, level, message):
            pass

    class Panel:
        bl_label = ""
        bl_idname = ""
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = ""

        def draw(self, context):
            pass

    bpy.types.Operator = Operator
    bpy.types.Panel = Panel
    bpy.types.PropertyGroup = type("PropertyGroup", (), {})
    types_mod = sys.modules["bpy.types"]
    types_mod.Operator = Operator
    types_mod.Panel = Panel
    types_mod.PropertyGroup = bpy.types.PropertyGroup
    types_mod.Node = Node
    types_mod.Material = _Material
    types_mod.Object = Object
    types_mod.Mesh = Mesh
    types_mod.Armature = Armature
    types_mod.Scene = Scene
    bpy.props = _Simple(
        "props",
        StringProperty=lambda **k: "str",
        BoolProperty=lambda **k: False,
        IntProperty=lambda **k: 0,
        FloatProperty=lambda **k: 0.0,
        EnumProperty=lambda **k: "",
    )
    props_mod = types.ModuleType("bpy.props")
    for k, v in vars(bpy.props).items():
        if not k.startswith("_"):
            setattr(props_mod, k, v)
    sys.modules["bpy.props"] = props_mod
    return bpy


def install():
    """Inject the stub into sys.modules. Call BEFORE importing addon modules."""
    if getattr(sys.modules.get("bpy"), "__bpy_stub__", False) is not True:
        stub = _build()
        stub.__bpy_stub__ = True
        sys.modules["bpy"] = stub

        # Objek bawaan ala factory startup: Cube, Camera, Light.
        scene = stub.context.scene
        cube = stub.data.objects.new("Cube", stub.data.meshes.new("Cube"))
        scene.collection.objects.link(cube)
        cam = stub.data.objects.new("Camera", stub.data.cameras.new("Camera"))
        scene.collection.objects.link(cam)
        light = stub.data.objects.new("Light", stub.data.lights.new("Light", "POINT"))
        scene.collection.objects.link(light)

    import importlib
    bmesh_mod = types.ModuleType("bmesh")
    bmesh_mod.new = BMesh
    bmesh_mod.from_edit_mesh = lambda mesh, face_map=None: BMesh()
    bmesh_mod.ops = _BMeshOps()
    bmesh_mod.types = _Simple(
        "types",
        BMesh=BMesh,
        BMeshVert=BMeshVert,
        BMeshEdge=BMeshEdge,
        BMeshFace=BMeshFace,
        BMeshLoop=BMeshLoop,
    )
    sys.modules["bmesh"] = bmesh_mod

    mathutils_mod = types.ModuleType("mathutils")
    mathutils_mod.Vector = Vector
    mathutils_mod.Matrix = Matrix
    mathutils_mod.Euler = Euler
    mathutils_mod.Quaternion = Quaternion
    bvhtree = types.ModuleType("mathutils.bvhtree")
    bvhtree.BVHTree = _Simple("BVHTree", FromObject=staticmethod(_bvhtree_from_object))
    mathutils_mod.bvhtree = bvhtree
    sys.modules["mathutils"] = mathutils_mod
    sys.modules["mathutils.bvhtree"] = bvhtree

    import importlib

    for name in list(sys.modules):
        if name.startswith("addon") or name == "mathutils" or name == "bmesh":
            if name != "bmesh" and name != "mathutils":
                try:
                    importlib.reload(sys.modules[name])
                except Exception:
                    pass
    return sys.modules["bpy"]


if __name__ == "__main__":
    install()
    bpy = sys.modules["bpy"]
    obj = bpy.data.objects.new("Cube", bpy.data.meshes.new("CubeMesh"))
    bpy.context.scene.collection.objects.link(obj)
    assert obj.name == "Cube"
    obj2 = bpy.data.objects.new("Cube", None)
    assert obj2.name == "Cube.001"
    mat = bpy.data.materials.new("M")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    assert bsdf is not None
    bsdf.inputs["Base Color"].default_value = (1, 0, 0, 1)
    arm = bpy.data.armatures.new("Arm")
    eb = arm.edit_bones.new("Bone")
    eb.head = Vector((0, 0, 0))
    eb.tail = Vector((0, 0, 1))
    assert arm.bones.get("Bone") is not None
    v = Vector((1, 2, 3))
    assert v.length == math.sqrt(14)
    print("bpy_stub self-check OK")
