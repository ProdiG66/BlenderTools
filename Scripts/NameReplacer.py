import bpy

REPLACE_MODES = [
    ("prefix_prefix", "Prefix → Prefix", ""),
    ("prefix_suffix", "Prefix → Suffix", ""),
    ("suffix_prefix", "Suffix → Prefix", ""),
    ("suffix_suffix", "Suffix → Suffix", "")
]

TARGETS = [
    ("OBJECT", "Objects", ""),
    ("BONE", "Bones", ""),
    ("MATERIAL", "Materials", ""),
    ("TEXTURE", "Textures", "")
]

class StringReplaceToolProperties(bpy.types.PropertyGroup):
    old_str: bpy.props.StringProperty(name="Old String", default="")
    new_str: bpy.props.StringProperty(name="New String", default="")
    replace_mode: bpy.props.EnumProperty(name="Mode", items=REPLACE_MODES)
    target_type: bpy.props.EnumProperty(name="Target", items=TARGETS)

def replace_name(name, old, new, mode):
    if mode == "prefix_prefix" and name.startswith(old):
        return new + name[len(old):]
    elif mode == "suffix_suffix" and name.endswith(old):
        return name[:-len(old)] + new
    elif mode == "prefix_suffix" and name.startswith(old):
        return name[len(old):] + new
    elif mode == "suffix_prefix" and name.endswith(old):
        return new + name[:-len(old)]
    return name

class OBJECT_OT_ExecuteStringReplace(bpy.types.Operator):
    bl_idname = "object.execute_string_replace"
    bl_label = "Replace String"

    def execute(self, context):
        props = context.scene.string_replace_tool
        old = props.old_str
        new = props.new_str
        mode = props.replace_mode
        target = props.target_type

        if not old:
            self.report({'WARNING'}, "Old string is empty.")
            return {'CANCELLED'}

        if target == "OBJECT":
            for obj in bpy.context.selected_objects:
                obj.name = replace_name(obj.name, old, new, mode)

        elif target == "BONE":
            armature = context.active_object
            if not armature or armature.type != 'ARMATURE':
                self.report({'WARNING'}, "Select an armature.")
                return {'CANCELLED'}
            bpy.ops.object.mode_set(mode='EDIT')
            for bone in armature.data.edit_bones:
                bone.name = replace_name(bone.name, old, new, mode)
            bpy.ops.object.mode_set(mode='OBJECT')

        elif target == "MATERIAL":
            for mat in bpy.data.materials:
                mat.name = replace_name(mat.name, old, new, mode)

        elif target == "TEXTURE":
            for tex in bpy.data.textures:
                tex.name = replace_name(tex.name, old, new, mode)

        return {'FINISHED'}
    
class OBJECT_PT_StringReplaceToolPanel(bpy.types.Panel):
    bl_label = "Name Replacer"
    bl_idname = "OBJECT_PT_string_replace_tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        props = context.scene.string_replace_tool
        layout = self.layout
        layout.prop(props, "old_str")
        layout.prop(props, "new_str")
        layout.prop(props, "replace_mode")
        layout.prop(props, "target_type")
        layout.operator("object.execute_string_replace", icon='FONT_DATA')

classes = (
    StringReplaceToolProperties,
    OBJECT_OT_ExecuteStringReplace,
    OBJECT_PT_StringReplaceToolPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.string_replace_tool = bpy.props.PointerProperty(type=StringReplaceToolProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.string_replace_tool

if __name__ == "__main__":
    register()
