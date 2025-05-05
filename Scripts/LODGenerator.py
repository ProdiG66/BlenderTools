import bpy

class LODGeneratorProperties(bpy.types.PropertyGroup):
    lod_count: bpy.props.IntProperty(
        name="LOD Count",
        description="Number of LOD levels to generate",
        default=3,
        min=1,
        max=10
    )
    decimate_type: bpy.props.EnumProperty(
        name="Decimate Type",
        description="Type of decimation to apply",
        items=[
            ('COLLAPSE', "Collapse", "Use Collapse type (ratio-based)"),
            ('UNSUBDIV', "Un-Subdivide", "Use Un-Subdivide type (iteration-based)")
        ],
        default='COLLAPSE'
    )
    decimate_step: bpy.props.FloatProperty(
        name="Decimate Step",
        description="Reduction per LOD (only for Collapse)",
        default=0.3,
        min=0.05,
        max=1.0
    )

class OBJECT_OT_generate_lods(bpy.types.Operator):
    bl_idname = "object.generate_lods"
    bl_label = "Generate LODs"
    bl_description = "Generate LODs using Decimate modifier"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.lod_gen_props
        selected_objects = context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        for obj in selected_objects:
            if obj.type != 'MESH':
                self.report({'INFO'}, f"Skipping non-mesh object: {obj.name}")
                continue

            # Detect base name
            base_name = obj.name
            if base_name.endswith("_LOD0"):
                base_name = base_name[:-6]  # Strip _LOD0

            # Rename original object to *_LOD0 if not already
            obj.name = f"{base_name}_LOD0"
            obj.data.name = obj.name

            for i in range(1, props.lod_count + 1):
                lod_obj = obj.copy()
                lod_obj.data = obj.data.copy()
                lod_obj.name = f"{base_name}_LOD{i}"
                lod_obj.data.name = lod_obj.name
                bpy.context.collection.objects.link(lod_obj)

                decimate = lod_obj.modifiers.new(name=f"LOD{i}_Decimate", type='DECIMATE')
                decimate.decimate_type = props.decimate_type

                if props.decimate_type == 'COLLAPSE':
                    ratio = max(0.01, 1.0 - props.decimate_step * i)
                    decimate.ratio = ratio
                    decimate.use_collapse_triangulate = True
                elif props.decimate_type == 'UNSUBDIV':
                    decimate.iterations = i * 2  # 2, 4, 6...

        self.report({'INFO'}, "LODs generated")
        return {'FINISHED'}

class VIEW3D_PT_lod_generator(bpy.types.Panel):
    bl_label = "LOD Generator"
    bl_idname = "VIEW3D_PT_lod_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.lod_gen_props
        selected = context.selected_objects

        has_mesh = any(obj.type == 'MESH' for obj in selected)

        layout.prop(props, "lod_count")
        layout.prop(props, "decimate_type")

        if props.decimate_type == 'COLLAPSE':
            layout.prop(props, "decimate_step")

        layout.enabled = has_mesh
        if has_mesh:
            layout.operator("object.generate_lods", icon='MOD_DECIM')
        else:
            layout.label(text="Select at least one mesh object", icon='ERROR')

def register():
    bpy.utils.register_class(LODGeneratorProperties)
    bpy.utils.register_class(OBJECT_OT_generate_lods)
    bpy.utils.register_class(VIEW3D_PT_lod_generator)
    bpy.types.Scene.lod_gen_props = bpy.props.PointerProperty(type=LODGeneratorProperties)

def unregister():
    bpy.utils.unregister_class(LODGeneratorProperties)
    bpy.utils.unregister_class(OBJECT_OT_generate_lods)
    bpy.utils.unregister_class(VIEW3D_PT_lod_generator)
    del bpy.types.Scene.lod_gen_props

if __name__ == "__main__":
    register()
