"""Original illustration for the freestanding drinks board; no campaign copy."""
import bpy,random,math
from mathutils import Vector
from pathlib import Path
rng=random.Random(11);bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,c,rough,trans=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1)
    b.inputs['Roughness'].default_value=rough;b.inputs['Transmission Weight'].default_value=trans;b.inputs['IOR'].default_value=1.34
    return m
glass=mat('clear PET',(.97,.98,.99),.13,.94);ice=mat('ice',(.96,.99,1),.18,.77)
peach=mat('peach tea',(.96,.253,.086),.25,.23);milk=mat('strawberry cream',(.95,.41,.42),.32)
red=mat('berry pieces',(.67,.034,.052),.37);orange=mat('orange rind',(1,.41,.055),.38)
def vessel(x,y,profile,m):
    n=72;v=[(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),z) for z,r in profile for i in range(n)]
    f=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)]
    data=bpy.data.meshes.new(m.name);data.from_pydata(v,[],f);data.update()
    o=bpy.data.objects.new(m.name,data);bpy.context.collection.objects.link(o);data.materials.append(m)
    for poly in data.polygons:poly.use_smooth=True
for x,y,fill in [(-.43,.12,peach),(.42,-.12,milk)]:
    vessel(x,y,[(.01,.006),(.01,.276),(.038,.29),(1.19,.411),(1.216,.421),(1.23,.41),(1.22,.399),(.045,.279),(.043,.006)],glass)
    vessel(x,y,[(.04,.005),(.04,.274),(1.125,.391),(1.139,.378),(1.139,.002)],fill)
    for j in range(10):
        a=j*2.39;r=rng.uniform(.03,.27)
        bpy.ops.mesh.primitive_cube_add(size=rng.uniform(.13,.21),location=(x+r*math.cos(a),y+r*math.sin(a),rng.uniform(1.1,1.205)))
        o=bpy.context.object;o.data.materials.append(ice);o.rotation_euler=(rng.random(),rng.random(),rng.random())
        mod=o.modifiers.new('soft ice edges','BEVEL');mod.width=.027;mod.segments=3
    for j in range(12):
        a=j*2.4;r=rng.uniform(.06,.31)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=rng.uniform(.036,.067),location=(x+r*math.cos(a),y+r*math.sin(a),1.13+rng.uniform(.01,.08)))
        bpy.context.object.data.materials.append(orange if x<0 else red)
s=bpy.context.scene;s.world=bpy.data.worlds.new('softbox');s.world.color=(.33,.33,.36)
for loc,energy,size in [((-3,-4,5),430,4),((2,2,4),530,3),((3,-2,3),180,2)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.size=size;o.rotation_euler=(Vector((0,0,.6))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.49,-5.3,2.28));o=bpy.context.object
o.rotation_euler=(Vector((0,0,.64))-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=1.96;s.camera=o
s.render.engine='CYCLES';s.cycles.samples=18;s.cycles.use_denoising=True;s.render.film_transparent=True
s.render.resolution_x=620;s.render.resolution_y=550;s.render.resolution_percentage=100;s.render.image_settings.color_mode='RGBA'
s.render.filepath=str(Path(__file__).parent/'finishes/drinks.png');bpy.ops.render.render(write_still=True)
