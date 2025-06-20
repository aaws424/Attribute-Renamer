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
        # Allow operation if we're in geometry nodes editor OR have selected mesh objects
        return ((context.space_data.type == 'NODE_EDITOR' and 
                context.space_data.tree_type == 'GeometryNodeTree') or
                any(obj.type == 'MESH' for obj in context.selected_objects))
    
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
            node_was_renamed = False
            
            # Check different node types that might reference attributes
            if hasattr(node, 'inputs'):
                for input_socket in node.inputs:
                    if hasattr(input_socket, 'default_value') and isinstance(input_socket.default_value, str):
                        if input_socket.default_value == old_name:
                            input_socket.default_value = new_name
                            renamed_count += 1
                            node_was_renamed = True
            
            # Check for specific node types with attribute name properties
            if node.type == 'NAMED_ATTRIBUTE':
                if hasattr(node, 'attribute_name') and node.attribute_name == old_name:
                    node.attribute_name = new_name
                    renamed_count += 1
                    node_was_renamed = True
            
            elif node.type == 'STORE_NAMED_ATTRIBUTE':
                if hasattr(node, 'attribute_name') and node.attribute_name == old_name:
                    node.attribute_name = new_name
                    renamed_count += 1
                    node_was_renamed = True
            
            elif node.type == 'REMOVE_ATTRIBUTE':
                if hasattr(node, 'attribute_name') and node.attribute_name == old_name:
                    node.attribute_name = new_name
                    renamed_count += 1
                    node_was_renamed = True
            
            # Check for attribute name in node inputs (for nodes that use string inputs for attribute names)
            if hasattr(node, 'inputs'):
                for input_socket in node.inputs:
                    if input_socket.name in ['Name', 'Attribute']:
                        if hasattr(input_socket, 'default_value') and input_socket.default_value == old_name:
                            input_socket.default_value = new_name
                            renamed_count += 1
                            node_was_renamed = True
            
            # Change node color to red if it was renamed
            if node_was_renamed:
                node.use_custom_color = True
                node.color = (0.8, 0.2, 0.2)  # Red color
            
            # Handle nested node groups
            if node.type == 'GROUP' and hasattr(node, 'node_tree') and node.node_tree:
                # Recursively process the nested node group
                nested_count = self.rename_attributes_in_tree(node.node_tree, old_name, new_name, processed_trees)
                renamed_count += nested_count
                
                # If the nested group had renames, color this group node too
                if nested_count > 0:
                    node.use_custom_color = True
                    node.color = (0.6, 0.3, 0.1)  # Orange color for group nodes with nested changes
        
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
        
        total_renamed = 0
        processed_node_trees = set()
        objects_processed = 0
        
        # Get selected objects
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}
        
        # Process each selected object
        for obj in selected_objects:
            obj_renamed = 0
            
            # Check all modifiers on the object
            for modifier in obj.modifiers:
                if modifier.type == 'NODES' and modifier.node_group:
                    node_tree = modifier.node_group
                    
                    # Skip if we already processed this node tree
                    if node_tree not in processed_node_trees:
                        renamed_count = self.rename_attributes_in_tree(node_tree, old_name, new_name)
                        if renamed_count > 0:
                            obj_renamed += renamed_count
                            processed_node_trees.add(node_tree)
            
            if obj_renamed > 0:
                objects_processed += 1
                total_renamed += obj_renamed
        
        # Also check the currently active node tree in the editor (if any)
        if (context.space_data.type == 'NODE_EDITOR' and 
            context.space_data.tree_type == 'GeometryNodeTree' and
            context.space_data.edit_tree):
            
            active_tree = context.space_data.edit_tree
            if active_tree not in processed_node_trees:
                renamed_count = self.rename_attributes_in_tree(active_tree, old_name, new_name)
                if renamed_count > 0:
                    total_renamed += renamed_count
                    processed_node_trees.add(active_tree)
        
        if total_renamed > 0:
            self.report({'INFO'}, f"Renamed {total_renamed} attribute reference(s) from '{old_name}' to '{new_name}' across {objects_processed} object(s) and {len(processed_node_trees)} node tree(s)")
        else:
            self.report({'WARNING'}, f"No references to attribute '{old_name}' found in selected objects")
        
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