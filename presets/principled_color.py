import bpy
propchart = bpy.context.window_manager.propchart

propchart.value = 'data.materials[0].node_tree.nodes["Principled BSDF"].inputs[0].default_value'
