import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import PropertyGroup

class ChatMsg(PropertyGroup):
    role: StringProperty()
    text: StringProperty()
    is_new: BoolProperty(default=False)

class ModelItem(PropertyGroup):
    model_id: StringProperty()
    model_name: StringProperty()
    provider: StringProperty()
