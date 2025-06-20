import bpy
from bpy.types import Panel

class GEONODES_PT_attribute_renamer(Panel):
    """Panel for renaming attributes in geometry nodes"""
    bl_label = "Attribute Renamer"
    bl_idname = "GEONODES_PT_attribute_renamer"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Tool"
    
    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'NODE_EDITOR' and 
                context.space_data.tree_type == 'GeometryNodeTree')
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Header
        layout.label(text="Rename Attributes", icon='GREASEPENCIL')
        
        # Text fields
        col = layout.column(align=True)
        col.prop(scene, "attr_renamer_old_name", text="From")
        col.prop(scene, "attr_renamer_new_name", text="To")
        
        # Spacing
        layout.separator()
        
        # Rename button
        row = layout.row()
        row.scale_y = 1.5
        op = row.operator("geonodes.rename_attribute", text="Rename Attribute", icon='FILE_REFRESH')
        
        # Enable/disable button based on input
        if not scene.attr_renamer_old_name or not scene.attr_renamer_new_name:
            row.enabled = False
        
        # Info text
        layout.separator()
        box = layout.box()
        box.label(text="Renames attribute references in:", icon='INFO')
        box.label(text="• All selected mesh objects")
        box.label(text="• All geometry node modifiers")
        box.label(text="• All nested node groups recursively")
        box.label(text="• Currently active node tree (if any)")
        
        # Usage instruction
        layout.separator()
        info_box = layout.box()
        info_box.label(text="Usage:", icon='QUESTION')
        info_box.label(text="Select objects with Geometry Nodes")
        info_box.label(text="modifiers, then click Rename")

classes = [
    GEONODES_PT_attribute_renamer,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)