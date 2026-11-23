"""Bake short-range ambient visibility into static architectural vertices."""
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def bake(collection):
    ignore={'canopy','shrub','leaf1','leaf4','glass','tint','smoke'}
    objects=[o for o in collection if o.type=='MESH' and o.name not in ignore]
    points=[];faces=[]
    for obj in objects:
        base=len(points);points.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(base+i for i in f.vertices) for f in obj.data.polygons)
    tree=BVHTree.FromPolygons(points,faces)
    probes=[]
    for i in range(12):
        z=(i+.5)/12; r=math.sqrt(1-z*z);a=i*2.39996
        probes.append(Vector((r*math.cos(a),r*math.sin(a),z)))
    names={'chalkwall','fascia','tile','granite','silver','curb','stone','charcoal','plaster','deepblue','cream','paver','bark'}
    for obj in objects:
        if obj.name not in names and not obj.name.startswith('court slab '):continue
        mesh=obj.data;attr=mesh.color_attributes.new(name='Ambient occlusion',type='BYTE_COLOR',domain='POINT')
        mesh.color_attributes.active_color=attr
        for v in mesh.vertices:
            n=v.normal.normalized();q=n.to_track_quat('Z','Y')
            p=obj.matrix_world@v.co+n*.025;obstruction=0
            for direction in probes:
                _,_,_,dist=tree.ray_cast(p,q@direction,2.4)
                if dist is not None:obstruction+=1-dist/2.4
            value=max(.38,1-.82*obstruction/len(probes))
            attr.data[v.index].color=(value,value,value,1)
