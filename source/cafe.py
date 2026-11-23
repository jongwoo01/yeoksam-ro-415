"""Street-facing cafe study. Furniture and lighting are an original interior design."""
import bpy, math
from mathutils import Vector
from pathlib import Path

def furnish():
    collection=bpy.data.collections.new('카페 · 가구와 입면')
    bpy.context.scene.collection.children.link(collection)
    def finish(obj,name,material):
        obj.name=name
        for source in list(obj.users_collection): source.objects.unlink(obj)
        collection.objects.link(obj)
        obj.data.materials.append(material)
        return obj
    def surface(name,color,rough=.5,metal=0,emission=0):
        m=bpy.data.materials.new(name);m.use_nodes=True
        b=m.node_tree.nodes.get('Principled BSDF')
        b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
        if emission:
            b.inputs['Emission Color'].default_value=(*color,1);b.inputs['Emission Strength'].default_value=emission
        return m
    oak=surface('Honey oak',(.43,.211,.082));bronze=surface('Anodized bronze',(.14,.079,.041),.28,.72)
    cream=surface('Limestone',(.72,.62,.46));velvet=surface('Moss upholstery',(.14,.215,.132),.94)
    chalk=surface('Chalk ceramic',(.79,.73,.61),.26);black=surface('Espresso',(.048,.03,.021))
    lamp=surface('Opal light',(.99,.65,.32),.25,0,2.8); brass=surface('Brushed brass',(.61,.375,.141),.29,.75)
    pane=surface('Cafe glazing',(.7,.82,.81),.08,.3)
    bs=pane.node_tree.nodes.get('Principled BSDF');bs.inputs['Alpha'].default_value=.12
    def slab(name,xyz,size,mat,bevel=.02):
        bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
        o=finish(bpy.context.object,name,mat);o.dimensions=size
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        if bevel:
            m=o.modifiers.new('가공한 모서리','BEVEL');m.width=bevel;m.segments=3
            o.modifiers.new('면 법선','WEIGHTED_NORMAL')
        return o
    def turn(name,x,y,profile,mat):
        n=32;v=[];f=[]
        for z,r in profile:
            v.extend((x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),z) for i in range(n))
        for j in range(len(profile)-1):
            for i in range(n):
                a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
        f.extend([tuple(reversed(range(n))),tuple(range(len(v)-n,len(v)))])
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.update()
        o=bpy.data.objects.new(name,mesh);finish(o,name,mat)
        for poly in mesh.polygons[:-2]:poly.use_smooth=True
    def lettering(words,x,y,z,size,mat):
        curve=bpy.data.curves.new(words,'FONT');curve.body=words;curve.align_x='CENTER';curve.align_y='CENTER'
        curve.size=size;curve.space_character=1.12;curve.extrude=.017;curve.bevel_depth=.003
        o=bpy.data.objects.new(words,curve);o.location=(x,y,z);o.rotation_euler.x=math.pi/2;finish(o,words,mat)
        bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
    slab('석재 바닥',(0,13.4,.16),(17.5,6.5,.14),surface('interior floor',(.17,.145,.115),.83))
    slab('천장',(0,13.7,3.25),(17.6,6.3,.18),cream)
    slab('뒤쪽 벽',(0,16.6,1.7),(17.5,.2,3.2),cream)
    for x in [-8.62,8.62]:slab('측벽',(x,13.7,1.68),(.18,6.1,3.1),pane if x>0 else cream)
    for x in [-7.8,-3.9,0,3.9,7.8]:
        slab('창틀',(x,10.67,1.69),(.064,.16,3.0),bronze,.009)
    for x in [-5.85,-1.95,1.95,5.85]:
        slab('쇼윈도',(x,10.7,1.69),(3.82,.018,2.9),pane,0)
    for z in [.235,2.61,3.13]:slab('창틀 가로대',(0,10.67,z),(15.65,.15,.05),bronze,.008)
    return collection

def studio(root):
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
    s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100
    world=bpy.data.worlds.new('오후의 하늘');s.world=world;world.use_nodes=True
    nodes=world.node_tree.nodes;env=nodes.new('ShaderNodeTexEnvironment')
    path=Path(bpy.app.binary_path).resolve().parents[1]/'Resources'/f'{bpy.app.version[0]}.{bpy.app.version[1]}'/'datafiles'/'studiolights/world/courtyard.exr'
    env.image=bpy.data.images.load(str(path));env.image.pack()
    bg=nodes.get('Background');bg.inputs['Strength'].default_value=.58
    world.node_tree.links.new(env.outputs[0],bg.inputs[0])
    bpy.ops.object.light_add(type='SUN',rotation=(.55,-.65,-.40))
    sun=bpy.context.object;sun.name='늦은 오후 햇살';sun.data.energy=2.2;sun.data.angle=.045;sun.data.color=(1,.85,.65)
    for x in [-6,-2,2,6]:
        bpy.ops.object.light_add(type='AREA',location=(x,13.5,3.10));o=bpy.context.object
        o.name='실내 간접광';o.data.energy=140;o.data.shape='DISK';o.data.size=2;o.data.color=(1,.76,.49)
    bpy.ops.object.camera_add(location=(-4.2,-6.8,2.5))
    cam=bpy.context.object;cam.name='카페 전면 · 보행자 시점'
    cam.rotation_euler=(Vector((1.6,11.1,4.2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=29;s.camera=cam
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
    s.render.filepath=str(root/'source/카페-블렌더.png')
