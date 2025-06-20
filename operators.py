import bpy
from bpy.types import Operator
from bpy.props import StringProperty

class GEONODES_OT_rename_attribute(Operator):
    """Rename attribute in the active geometry nodes tree"""
    bl_idname = "geonodes.rename_attribute"
    bl_label = "Rename Attribute"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'NODE_EDITOR' and 
                context.space_data.tree_type == 'GeometryNodeTree' and
                context.space_data.edit_tree is not None)
    
    def rename_attributes_in_tree(self, node_tree, old_name, new_name, processed_trees=None):
        """Recursively rename attributes in a node tree and all nested node groups"""
        if processed_trees is None:
            processed_trees = set()
        
        # Prevent infinite recursion by tracking processed trees
        if node_tree in processed_trees:
            return 0
        processed_trees.add(node_tree)
        
        renamed_count = 0
        
        # Search through all nodes in the current tree
        for node in node_tree.nodes:
            # Check different node types that might reference attributes
            if hasattr(node, 'inputs'):
                for input_socket in node.inputs:
                    if hasattr(input_socket, 'default_value') and isinstance(input_socket.default_value, str):
                        if input_socket.default_value == old_name:
                            input_socket.default_value = new_name
                            renamed_count += 1
            
            # Check for specific node types with attribute name properties
            if node.type == 'NAMED_ATTRIBUTE':
                if hasattr(node, 'attribute_name') and node.attribute_name == old_name:
                    node.attribute_name = new_name
                    renamed_count += 1
            
            elif node.type == 'STORE_NAMED_ATTRIBUTE':
                if hasattr(node, 'attribute_name') and node.attribute_name == old_name:
                    node.attribute_name = new_name
                    renamed_count += 1
            
            elif node.type == 'REMOVE_ATTRIBUTE':
                if hasattr(node, 'attribute_name') and node.attribute_name == old_name:
                    node.attribute_name = new_name
                    renamed_count += 1
            
            # Check for attribute name in node inputs (for nodes that use string inputs for attribute names)
            if hasattr(node, 'inputs'):
                for input_socket in node.inputs:
                    if input_socket.name in ['Name', 'Attribute']:
                        if hasattr(input_socket, 'default_value') and input_socket.default_value == old_name:
                            input_socket.default_value = new_name
                            renamed_count += 1
            
            # Handle nested node groups
            if node.type == 'GROUP' and hasattr(node, 'node_tree') and node.node_tree:
                # Recursively process the nested node group
                nested_count = self.rename_attributes_in_tree(node.node_tree, old_name, new_name, processed_trees)
                renamed_count += nested_count
        
        return renamed_count

    def execute(self, context):
        scene = context.scene
        old_name = scene.attr_renamer_old_name
        new_name = scene.attr_renamer_new_name
        
        if not old_name:
            self.report({'ERROR'}, "Old attribute name cannot be empty")
            return {'CANCELLED'}
        
        if not new_name:
            self.report({'ERROR'}, "New attribute name cannot be empty")
            return {'CANCELLED'}
        
        if old_name == new_name:
            self.report({'WARNING'}, "Old and new names are the same")
            return {'CANCELLED'}
        
        # Get the active geometry nodes tree
        node_tree = context.space_data.edit_tree
        
        if not node_tree:
            self.report({'ERROR'}, "No active geometry nodes tree")
            return {'CANCELLED'}
        
        # Rename attributes recursively through all nested node groups
        renamed_count = self.rename_attributes_in_tree(node_tree, old_name, new_name)
        
        if renamed_count > 0:
            self.report({'INFO'}, f"Renamed {renamed_count} attribute reference(s) from '{old_name}' to '{new_name}' (including nested node groups)")
        else:
            self.report({'WARNING'}, f"No references to attribute '{old_name}' found")
        
        return {'FINISHED'}

classes = [
    GEONODES_OT_rename_attribute,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register properties
    bpy.types.Scene.attr_renamer_old_name = StringProperty(
        name="Old Name",
        description="Current attribute name to rename",
        default=""
    )
    
    bpy.types.Scene.attr_renamer_new_name = StringProperty(
        name="New Name", 
        description="New attribute name",
        default=""
    )

def unregister():
    # Unregister properties
    del bpy.types.Scene.attr_renamer_old_name
    del bpy.types.Scene.attr_renamer_new_name
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)