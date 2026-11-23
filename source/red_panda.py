"""Small red panda in a rain jacket, with a satchel and jointed limbs."""
import bpy, math
from pathlib import Path
bpy.ops.wm.read_factory_settings(use_empty=True)
root=Path(__file__).resolve().parents[1]
def group(name,loc,parent=None):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=parent;o.location=loc;return o
palette={'fur':'bc5638','cream':'f6dfba','dark':'382925','jacket':'e8a53b','lining':'e4bd61','bag':'376660','trim':'274846','boot':'493d37','nose':'201d1e','white':'fff7dd'}
mats={}
for k,h in palette.items():
    m=bpy.data.materials.new(k);m.diffuse_color=tuple(((int(h[i:i+2],16)/255+.055)/1.055)**2.4 for i in (0,2,4))+(1,);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=m.diffuse_color
    bs.inputs['Roughness'].default_value=.87
    mats[k]=m
def oval(name,p,loc,scale,mat,angle=0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12)
    o=bpy.context.object;o.name=name;o.parent=p;o.location=loc;o.scale=scale;o.rotation_euler.y=angle;o.data.materials.append(mats[mat])
    for f in o.data.polygons:f.use_smooth=True
    return o
body=group('body',(0,0,0))
oval('raincoat',body,(0,0,.75),(.32,.265,.39),'jacket')
oval('hood',body,(0,.065,1.00),(.34,.27,.17),'lining')
head=group('head',(0,-.01,1.27),body)
oval('head_fur',head,(0,0,0),(.42,.315,.344),'fur')
for s in [-1,1]:
    oval('ear',head,(s*.285,.024,.264),(.128,.105,.194),'cream',s*.35)
    oval('inner_ear',head,(s*.286,-.045,.275),(.086,.051,.133),'dark',s*.35)
    oval('cheek',head,(s*.238,-.235,-.065),(.156,.065,.075),'cream',-s*.51)
    oval('brow',head,(s*.151,-.252,.121),(.081,.04,.047),'cream',s*.22)
    oval('eye',head,(s*.148,-.289,.038),(.045,.028,.055),'nose')
    oval('glint',head,(s*.148-.010,-.311,.054),(.012,.01,.014),'white')
oval('muzzle',head,(0,-.285,-.072),(.152,.088,.083),'cream')
oval('nose',head,(0,-.357,-.031),(.048,.026,.028),'nose')
for s,side in [(-1,'L'),(1,'R')]:
    hip=group('leg'+side,(s*.144,0,.48),body)
    oval('trousers',hip,(0,0,-.137),(.125,.15,.203),'dark')
    oval('ankle_boot',hip,(0,-.035,-.33),(.133,.19,.12),'boot')
    arm=group('arm'+side,(s*.29,0,.936),body)
    oval('sleeve',arm,(s*.043,0,-.112),(.111,.128,.177),'jacket',s*.12)
    oval('paw',arm,(s*.059,-.012,-.265),(.082,.095,.10),'dark')
oval('canvas pack',body,(0,.25,.78),(.228,.107,.248),'bag')
oval('flap',body,(0,.339,.868),(.214,.035,.126),'trim')
oval('clasp',body,(0,.374,.826),(.029,.011,.036),'lining')
for s in [-1,1]:oval('strap',body,(s*.183,.086,.95),(.045,.16,.108),'bag')
tail=group('tail',(0,.14,.56),body)
for i in range(8):
    t=i/7;r=.116*(1-.35*t)
    oval('tail_ring',tail,(.075+.16*t,.095+i*.069,-.034-.13*math.sin(t*math.pi)),(r,r*1.16,r),('cream' if i%2 else 'fur'))
# Batch pieces sharing a joint and material, retaining the named animation pivots.
for parent in [o for o in bpy.context.scene.objects if o.type=='EMPTY']:
    for material in mats.values():
        parts=[o for o in parent.children if o.type=='MESH' and o.data.materials[0]==material]
        if len(parts)<2:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in parts:o.select_set(True)
        bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source/레서판다.blend'))
bpy.ops.export_scene.gltf(filepath=str(root/'public/red-panda.glb'),export_format='GLB')
