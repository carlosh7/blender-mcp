bl_info = {
    "name": "Example Add-on Preferences",
    "author": "Your Name Here",
    "version": (1, 0),
    "blender": (2, 65, 0),
    "location": "SpaceBar Search -> Add-on Preferences Example",
    "description": "Example Add-on",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object",
}


import bpy
from bpy.props import BoolProperty, IntProperty, StringProperty
from bpy.types import AddonPreferences, Operator


class ExampleAddonPreferences(AddonPreferences):
    # This must match the add-on name, use `__package__`
    # when defining this for add-on extensions or a sub-module of a Python package.
    bl_idname = __name__

    filepath: StringProperty(
        name="Example File Path",
        subtype="FILE_PATH",
    )
    number: IntProperty(
        name="Example Number",
        default=4,
    )
    boolean: BoolProperty(
        name="Example Boolean",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a preferences view for our add-on")
        layout.prop(self, "filepath")
        layout.prop(self, "number")
        layout.prop(self, "boolean")


class OBJECT_OT_addon_prefs_example(Operator):
    """Display example preferences"""

    bl_idname = "object.addon_prefs_example"
    bl_label = "Add-on Preferences Example"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        info = f"Path: {addon_prefs.filepath:s}, Number: {addon_prefs.number:d}, Boolean {addon_prefs.boolean!r}"
        self.report({"INFO"}, info)
        print(info)

        return {"FINISHED"}


# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_addon_prefs_example)
    bpy.utils.register_class(ExampleAddonPreferences)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_addon_prefs_example)
    bpy.utils.unregister_class(ExampleAddonPreferences)
