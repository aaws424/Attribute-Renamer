bl_info = {
    "name": "Attribute Renamer",
    "author": "AAWS424",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Geometry Nodes Editor > N-Panel",
    "description": "Rename attributes in geometry nodes",
    "category": "Node",
}

import bpy
from . import ui
from . import operators

def register():
    operators.register()
    ui.register()

def unregister():
    ui.unregister()
    operators.unregister()

if __name__ == "__main__":
    register()