import bpy
import os
import re
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import BoolProperty, StringProperty, PointerProperty


class ExportSettings(PropertyGroup):
    include_animations: BoolProperty(name="Include Animations", default=True)
    include_textures: BoolProperty(name="Include Textures", default=True)
    export_path: StringProperty(name="Export Path", default="//", subtype='DIR_PATH')
    export_each: BoolProperty(name="Export Each Object Individually", default=False)
    fbx_filename: StringProperty(name="FBX File Name", default="")
    show_validation_details: BoolProperty(name="Show Object Validation Details", default=False)


def validate_objects(objects, settings):
    validation_summary = {
        "all_valid": True,
        "errors": 0,
        "warnings": 0,
        "details": []
    }

    for obj in objects:
        if obj.hide_get():
            continue  # Skip hidden objects

        legal = []
        errors = []
        warnings = []

        if not re.match(r"^[a-zA-Z0-9_]+$", obj.name):
            errors.append("Invalid object name")
        else:
            legal.append("Valid name")

        scale_issues = [i for i, s in enumerate(obj.scale) if abs(s - 1.0) >= 0.001]
        if scale_issues:
            errors.append(f"Scale not applied on axis: {', '.join('XYZ'[i] for i in scale_issues)}")
        else:
            legal.append("Valid scale (1.0 on all axes)")

        if obj.type == 'MESH':
            if obj.name != obj.data.name:
                errors.append("Object name doesn't match mesh name")
            else:
                legal.append("Mesh and Object names matched")

            if not obj.material_slots:
                warnings.append("No material assigned")
            else:
                legal.append("Material(s) assigned")

            textures_ok = True
            for mat_slot in obj.material_slots:
                mat = mat_slot.material
                if mat and mat.use_nodes:
                    for node in mat.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            image = node.image
                            if not image:
                                textures_ok = False
                            elif not image.packed_file and not os.path.exists(bpy.path.abspath(image.filepath)):
                                textures_ok = False
            if not textures_ok:
                errors.append("Missing or broken textures")
            else:
                legal.append("Textures present or packed")

        if errors:
            validation_summary["errors"] += len(errors)
            validation_summary["all_valid"] = False
        if warnings:
            validation_summary["warnings"] += len(warnings)

        validation_summary["details"].append({
            "name": obj.name,
            "legal": legal,
            "errors": errors,
            "warnings": warnings
        })

    return validation_summary


class OBJECT_OT_export_fbx(Operator):
    bl_idname = "export_scene.fbx_to_unity"
    bl_label = "Export FBX"
    bl_description = "Export selected model(s) as FBX for Unity"

    def execute(self, context):
        settings = context.scene.export_settings
        objects = [obj for obj in context.selected_objects if not obj.hide_get()]

        if not objects:
            self.report({'ERROR'}, "No visible objects selected.")
            return {'CANCELLED'}

        export_dir = bpy.path.abspath(settings.export_path)

        if settings.export_each:
            for obj in objects:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj

                export_name = obj.name + ".fbx"
                export_path = os.path.join(export_dir, export_name)

                result = bpy.ops.export_scene.fbx(
                    filepath=export_path,
                    use_selection=True,
                    apply_unit_scale=True,
                    apply_scale_options='FBX_SCALE_ALL',
                    bake_space_transform=True,
                    object_types={'MESH', 'ARMATURE'},
                    add_leaf_bones=False,
                    bake_anim=settings.include_animations,
                    path_mode='COPY' if settings.include_textures else 'AUTO',
                    embed_textures=settings.include_textures,
                )

                if result != {'FINISHED'}:
                    self.report({'ERROR'}, f"Failed to export {obj.name}")
                    return {'CANCELLED'}

        else:
            export_name = settings.fbx_filename.strip()
            if not export_name:
                self.report({'ERROR'}, "FBX filename is empty.")
                return {'CANCELLED'}

            if not export_name.lower().endswith(".fbx"):
                export_name += ".fbx"

            export_path = os.path.join(export_dir, export_name)

            result = bpy.ops.export_scene.fbx(
                filepath=export_path,
                use_selection=True,
                apply_unit_scale=True,
                apply_scale_options='FBX_SCALE_ALL',
                bake_space_transform=True,
                object_types={'MESH', 'ARMATURE'},
                add_leaf_bones=False,
                bake_anim=settings.include_animations,
                path_mode='COPY' if settings.include_textures else 'AUTO',
                embed_textures=settings.include_textures,
            )

            if result != {'FINISHED'}:
                self.report({'ERROR'}, "Failed to export file.")
                return {'CANCELLED'}

        self.report({'INFO'}, "Export completed.")
        return {'FINISHED'}


class VIEW3D_PT_export_panel(Panel):
    bl_label = "Export FBX for Unity"
    bl_idname = "VIEW3D_PT_export_unity"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.export_settings
        selected = [obj for obj in context.selected_objects if not obj.hide_get()]

        layout.prop(settings, "export_path")
        layout.prop(settings, "include_animations")
        layout.prop(settings, "include_textures")
        layout.prop(settings, "export_each")
        if not settings.export_each:
            layout.prop(settings, "fbx_filename")

        layout.separator()

        box = layout.box()
        box.label(text="Validation Summary:")

        if not selected:
            box.label(text="No visible objects selected", icon='INFO')
            return

        validation = validate_objects(selected, settings)
        valid = validation["all_valid"]
        err = validation["errors"]
        warn = validation["warnings"]

        icon = 'CHECKMARK' if valid else 'ERROR'
        status_msg = "All checks passed." if valid else f"{err} error(s), {warn} warning(s) found."
        box.label(text=status_msg, icon=icon)

        if not valid:
            box.prop(settings, "show_validation_details", toggle=True)

        if settings.show_validation_details:
            for item in validation["details"]:
                if not item["errors"] and not item["warnings"]:
                    continue
                sub = box.box()
                sub.label(text=item["name"], icon='OBJECT_DATAMODE')
                for e in item["errors"]:
                    sub.label(text=e, icon='X')
                for w in item["warnings"]:
                    sub.label(text=w, icon='ERROR')

        layout.separator()
        row = layout.row()
        row.enabled = valid
        export_name = settings.fbx_filename.strip()
        row.operator("export_scene.fbx_to_unity", icon='EXPORT')
        if not settings.export_each and not export_name:
            row.enabled = False
            layout.label(text="Enter File Name", icon='ERROR')
        if not valid:
            layout.label(text="Fix validation issues before export.", icon='ERROR')


def register():
    bpy.utils.register_class(ExportSettings)
    bpy.utils.register_class(OBJECT_OT_export_fbx)
    bpy.utils.register_class(VIEW3D_PT_export_panel)
    bpy.types.Scene.export_settings = PointerProperty(type=ExportSettings)


def unregister():
    bpy.utils.unregister_class(ExportSettings)
    bpy.utils.unregister_class(OBJECT_OT_export_fbx)
    bpy.utils.unregister_class(VIEW3D_PT_export_panel)
    del bpy.types.Scene.export_settings


if __name__ == "__main__":
    register()
