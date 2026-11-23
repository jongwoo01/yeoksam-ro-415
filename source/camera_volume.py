"""Bake camera clearance from actual city surfaces in the chase camera's range."""
import math
from mathutils.bvhtree import BVHTree

def bake_camera_volume(objects, path):
    vertices, faces = [], []
    for obj in objects:
        if obj.type != 'MESH':
            continue
        start = len(vertices)
        vertices.extend(tuple(obj.matrix_world @ v.co) for v in obj.data.vertices)
        for face in obj.data.polygons:
            ids = [start+i for i in face.vertices]
            if max(vertices[i][2] for i in ids) > .45:
                faces.append(ids)
    tree = BVHTree.FromPolygons(vertices, faces)
    # Half-metre voxels, X [-52,52), Blender Y [-34,70), height [0,16).
    size, layers = 208, 32
    bits = bytearray(size*size*layers//8)
    for j in range(size):
        y = -34+(j+.5)*.5
        for i in range(size):
            x = -52+(i+.5)*.5
            if math.hypot(x,y-17.5)>51:
                continue
            for k in range(layers):
                if tree.find_nearest((x,y,(k+.5)*.5),.54)[0] is not None:
                    bit = (j*size+i)*layers+k
                    bits[bit//8] |= 1 << (bit%8)
    path.write_bytes(bits)
