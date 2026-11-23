"""Reconstructed window films and printed menus along the restaurant's alley frontage."""
import bpy
from pathlib import Path


def add_snack_graphics(lane_x):
    root = Path(__file__).parent / 'finishes'
    # All surfaces face the lane. Increasing street Y reads from right to left.
    surfaces = {
        'snack-window-frosted.jpg': [(13.61, y, .68, 2.38, .56) for y in (12.2,14.75,17.3,19.85)],
        'snack-window-dark.jpg': [(13.74, y, 1.84, 2.39, 1.34) for y in (17.3,19.85)],
        'food-strip.jpg': [(13.55, y, 1.56, .38, 2.08) for y in (14.03,18.64)],
    }
    for file, panels in surfaces.items():
        material = bpy.data.materials.new(file.split('.')[0])
        material.use_nodes = True
        nodes = material.node_tree.nodes
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(root / file), check_existing=True)
        tex.image.pack()
        shader = nodes.get('Principled BSDF')
        material.node_tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
        shader.inputs['Roughness'].default_value = .53
        vertices, faces = [], []
        for x,y,z,w,h in panels:
            x = lane_x(x,y)
            n = len(vertices)
            vertices.extend([(x,y+w/2,z-h/2),(x,y-w/2,z-h/2),(x,y-w/2,z+h/2),(x,y+w/2,z+h/2)])
            faces.append((n,n+1,n+2,n+3))
        data = bpy.data.meshes.new(material.name)
        data.from_pydata(vertices, [], faces)
        data.update()
        uv = data.uv_layers.new()
        for loop in data.loops:
            uv.data[loop.index].uv = [(0,0),(1,0),(1,1),(0,1)][loop.vertex_index % 4]
        obj = bpy.data.objects.new(material.name, data)
        bpy.context.collection.objects.link(obj)
        data.materials.append(material)
