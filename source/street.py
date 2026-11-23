"""Build the exterior street study. Blender X/Y form the ground plane; units are metres."""
import bpy, math, random, json
from mathutils import Vector
from pathlib import Path
from collections import defaultdict
random.seed(415)
root = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(root/'source'))
from retail import add_shops
from parking import add_parking
from street_life import add_cars
from shopfront_finish import add_street_details
from window_recesses import fit_windows
bpy.ops.wm.read_factory_settings(use_empty=True)
buffers = defaultdict(lambda: ([], []))
materials = {}
bounds = []
def material(name, rgb, rough=.75, metal=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb,1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb,1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    materials[name] = mat
for args in [
 ('asphalt',(.105,.108,.113)),('paver',(.46,.445,.405)),('curb',(.58,.57,.53)),('mortar',(.24,.24,.22)),('paint',(.81,.79,.69)),('ochre',(.78,.49,.12)),
 ('stone',(.56,.54,.49)),('plaster',(.71,.69,.61)),('brick',(.36,.185,.135)),('charcoal',(.09,.10,.10)),('glass',(.28,.43,.46),.16,.72),('smoke',(.18,.26,.28),.24,.55),('silver',(.53,.57,.56),.34,.52),('navy',(.032,.076,.145)),('wood',(.28,.155,.074)),('bark',(.18,.145,.095)),('earth',(.15,.125,.087)),('leaf1',(.075,.18,.035)),('leaf2',(.16,.29,.058)),('leaf3',(.26,.37,.083)),('leaf4',(.095,.22,.075))]:
    material(*args)
def mesh(mat,verts,faces):
    v,f=buffers[mat]; start=len(v); v.extend(verts); f.extend(tuple(start+i for i in face) for face in faces)
def box(mat,x,y,z,w,d,h):
    pts=[(x+i*w/2,y+j*d/2,z+k*h/2) for k in (-1,1) for j in (-1,1) for i in (-1,1)]
    mesh(mat,pts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)])
def pole(mat,a,b,r,s,n=7):
    a,b=Vector(a),Vector(b); axis=(b-a).normalized()
    u=axis.cross(Vector((0,1,0)) if abs(axis.y)<.95 else Vector((1,0,0))).normalized(); v=axis.cross(u)
    pts=[tuple(p+(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n))*rad) for p,rad in [(a,r),(b,s)] for i in range(n)]
    mesh(mat,pts,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]+[tuple(range(n,2*n))])
def collide(x,y,w,d,top=None):
    footprint=[x-w/2,x+w/2,-y-d/2,-y+d/2]
    bounds.append(footprint if top is None else footprint+[top])
box('asphalt',0,0,-.25,165,144,.5)
# Each paved strip also defines the character's support surface, in Blender XY.
walkways=[]
def paving(y0,y1,l0,r0,l1,r1):
    walkways.append([y0,y1,l0,r0,l1,r1])
    outline=[(l0,y0),(r0,y0),(r1,y1),(l1,y1)]
    mesh('paver',[(x,y,z) for z in [0,.146] for x,y in outline],
         [(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
def border(a,b,mat,width,top):
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    nx,ny=-dy/length*width/2,dx/length*width/2
    pts=[(a[0]+nx,a[1]+ny),(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny)]
    mesh(mat,[(x,y,z) for z in [0,top] for x,y in pts],[(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
paving(-11.1,-6.5,-76.5,76.5,-76.5,76.5)
for sign,edge in [(-1,9.52),(1,13.35)]:
    radius=1.1;cx=edge+sign*radius;cy=6.5+radius
    arc=[(cx-sign*radius*math.sin(i*math.pi/24),cy-radius*math.cos(i*math.pi/24)) for i in range(13)]
    edgepts=arc+[(edge,11.1),(edge,23.4)]
    for (x0,y0),(x1,y1) in zip(edgepts,edgepts[1:]):
        other=(-76.5 if sign<0 else 76.5) if y0<11.1 else (9.0 if sign<0 else 13.88)
        paving(y0,y1,min(other,x0),max(other,x0),min(other,x1),max(other,x1))
        border((x0,y0),(x1,y1),'curb',.12,.15)
    stripe=[(cx-sign*(radius+.21)*math.sin(i*math.pi/24),cy-(radius+.21)*math.cos(i*math.pi/24)) for i in range(13)]
    stripe.append((edge-sign*.21,23.4))
    for a,b in zip(stripe,stripe[1:]):border(a,b,'ochre',.082,.009)
for side in [-1,1]:
    for left,right in ([(-76.5,8.42),(14.45,76.5)] if side==1 else [(-76.5,76.5)]):
        count=math.ceil(right-left)
        for j in range(count):
            x=left+(j+.5)*(right-left)/count
            box('curb',x,side*6.50,.074,(right-left)/count-.008,.12,.148)
        box('ochre',(left+right)/2,side*6.29,.004,right-left,.082,.008)
# Zebra markings visible beside the shop corner in shots 04 and 06.
for j in range(3):
    box('paint',10.28+j*1.17,8.32,.007,.45,1.84,.012)
for j in range(11):
    box('paint',16.85,-5.85+j*1.17,.007,2.42,.45,.012)
for x in range(-75,76,7):
    for y in [-3.15,3.15]:box('paint',x,y,.006,3.4,.11,.012)
# Facades have recessed glazing, reveals, sills and individually varied blinds.
def building(x,y,w,d,floors,style,hero=False,retail=False):
    side=1 if y>0 else -1
    front=y-side*d/2
    def face(mat,u,depth,z,width,thick,height):
        box(mat,x+u,front-side*depth,z,width,thick,height)
    height=4+floors*3.05
    collide(x,y,w,d)
    if hero or retail:box(style,x,y,(height+3.3)/2,w,d,height-3.3)
    else:box(style,x,y,height/2,w,d,height)
    if not (hero or retail):face('charcoal',0,.11,2,w-.28,.21,3.76)
    cols=max(3,round(w/(2.6 if hero else 3.2))); pitch=(w-.5)/cols
    for col in range(cols):
        u=(col+.5-cols/2)*pitch
        if not (hero or retail):face('smoke',u,.25,1.88,pitch-.14,.10,3.37)
        if not (hero or retail):face('silver',u,.32,2.8,pitch-.08,.06,.045)
        if not (hero or retail):face('silver',u-pitch/2,.35,1.93,.07,.12,3.7)
        for floor in range(floors):
            z=5.52+floor*3.05
            ww=pitch-.09 if hero else pitch-.42
            hh=2.82 if hero else 2.05
            face(random.choice(['glass','glass','smoke']),u,.09,z,ww,.15,hh)
            face('silver',u,.19,z,ww,.085,.045)
            face('silver',u,.19,z,.047,.085,hh)
            face('stone',u,.20,z-hh/2,ww+.09,.34,.095)
            if random.random()<.26:
                face('silver',u,.183,z+hh*.34,ww*.92,.025,.22)
    if not (hero or retail):face(style,0,.43,3.65,w-.18,.61,.90)
    face('stone',0,.29,height,w+.24,.65,.32)
    if hero:
        for u in [-w/2+.30,w/2-.30]:face('stone',u,.46,1.66,.57,.8,3.28)
    if not (hero or retail):
        # Facade families keep continuous shop bands, inset bays, and projecting bays distinct.
        family=(round(x/3)+floors)%3
        if family==0:
            for bay in range(cols):
                u=(bay+.5-cols/2)*pitch
                face(style,u-pitch*.46,.23,height*.5,pitch*.085,.43,height)
            for floor in range(1,floors+1):
                face('silver',0,.26,4+floor*3.05,w,.44,.12)
        elif family==1:
            for floor in range(floors):
                for j in range(4):
                    face('charcoal',0,.22,4+3.05*floor+.12+j*.15,w-.19,.15,.048)
            box(style,x+w*.09,y+(side*d*.09),height+1.08,w*.76,d*.66,2.16)
        else:
            for u in [-w*.36,w*.34]:
                face('charcoal',u,.49,2.38,w*.19,.93,.15)
            face('stone',0,.33,height-.36,w+.12,.70,.22)
        # Side elevations get inset-looking, subdivided windows and lintels as well.
        for edge in [-1,1]:
            for j in range(3):
                yy=y+(j-1)*d*.26
                for floor in range(floors):
                    zz=5.48+3.05*floor
                    xx=x+edge*(w*.5+.045)
                    box('smoke',xx,yy,zz,.10,1.67,1.64)
                    box('silver',xx+edge*.06,yy,zz,.043,.043,1.63)
                    box(style,xx+edge*.075,yy,zz-.84,.23,1.89,.10)
    if floors>2:box('charcoal',x+w*.17,y,height+.9,w*.21,d*.27,1.8)
add_shops(material,box,pole,mesh,collide,materials)
fit_windows(material,box,pole,mesh,materials)
add_parking(material,box,mesh)
collide(.1,24.27,16.7,.49,.56)
collide(-7.55,31.25,3.60,1.65)
collide(.30,34.0,20.20,3.9)
add_cars(material,mesh,collide)
add_street_details(material,box,pole,mesh,collide)
building(0,17.5,18,13,5,'stone',True)
building(-15.76,17.65,12.75,12.9,4,'charcoal',retail=True)
building(19.02,17.27,10.30,12.38,4,'tile',retail=True)
for side in [-1,1]:
    for x in [-62,-46,-29,-16,0,17,32,49,66]:
        if side==1 and x in (-16,0,17):continue
        w=random.choice([10.6,11.5,12.4])
        building(x,side*(17.6+random.uniform(0,1.8)),w,12,random.randint(2,6),random.choice(['plaster','brick','stone','charcoal']))
    for x in range(-75,76,15):
        background_x=20.8 if side==1 and x==15 else x
        building(background_x,side*40,13,12,random.randint(3,9),random.choice(['stone','plaster','brick']))
def crown(x,y,z,scale):
    # Sparse cutout sprays at several angles preserve the gaps between branches.
    for _ in range(57):
        angle=random.random()*math.tau; t=random.uniform(-1,1); rr=random.random()**(1/3)
        radial=scale*rr*math.sqrt(1-t*t)
        p=Vector((x+radial*math.cos(angle),y+radial*math.sin(angle),z+scale*t*rr*.87))
        az=angle+random.uniform(-.85,.85); half=random.uniform(.40,.56)
        u=Vector((math.cos(az)*half,math.sin(az)*half,random.uniform(-.12,.12)))
        v=Vector((-math.sin(az)*.34,math.cos(az)*.34,random.uniform(.25,.53)))
        mesh('canopy',[tuple(p-u-v),tuple(p+u-v),tuple(p+u+v),tuple(p-u+v)],[(0,1,2,3)])
material('weathered iron',(.105,.097,.078),.91,.29)
material('dry leaf',(.34,.205,.071),.92)
material('pale grit',(.29,.265,.215),.96)
def tree_well(x,y):
    dirt=random.Random(round(x*107+y*379))
    box('earth',x,y,.146,1.28,1.35,.012)
    for side in [-1,1]:
        box('weathered iron',x+side*.635,y,.166,.032,1.35,.035)
        box('weathered iron',x,y+side*.667,.166,1.28,.032,.035)
    # Narrow grate strips around the open soil and flared, tapering roots.
    for i in range(-8,9):
        xx=x+i*.070
        span=.46 if abs(i)<5 else .62
        for side in [-1,1]:
            length=.66-span
            box('weathered iron',xx,y+side*(.66-length/2),.171,.034,length,.023)
    for k in range(6):
        a=k*.98+dirt.uniform(-.24,.24)
        pole('bark',(x+.06*math.cos(a),y+.06*math.sin(a),.27),
             (x+.42*math.cos(a),y+.42*math.sin(a),.155),.096,.017,7)
    for k in range(61):
        xx=x+dirt.uniform(-.60,.60);yy=y+dirt.uniform(-.63,.63)
        r=dirt.uniform(.012,.029)
        mesh('pale grit',[(xx-r,yy,.154),(xx,yy-r,.154),(xx+r,yy,.156),(xx,yy+r,.155),(xx,yy,.155+r*.48)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)])
    for k in range(19):
        xx=x+dirt.uniform(-1.45,1.45);yy=y+dirt.uniform(-.7,.7)
        a=dirt.uniform(0,math.tau);dx=.049*math.cos(a);dy=.049*math.sin(a)
        mesh('dry leaf',[(xx-dx,yy-dy,.175),(xx-dy*.57,yy+dx*.57,.176),(xx+dx,yy+dy,.18),(xx+dy*.5,yy-dx*.5,.176)],[(0,1,2,3)])
def tree(x,y):
    tree_well(x,y);collide(x,y,.38,.38)
    trunk=(x+.08,y,3.25)
    pole('bark',(x,y,.16),trunk,.18,.105,10)
    for i in range(9):
        a=i*2.4; rad=random.uniform(.7,1.6); top=random.uniform(4.4,6.4)
        mid=(x+rad*.60*math.cos(a),y+rad*.60*math.sin(a),top-.85)
        end=(x+rad*math.cos(a),y+rad*math.sin(a),top)
        pole('bark',(x+.06,y,2.25+i*.10),mid,.085,.048);pole('bark',mid,end,.05,.015)
        crown(*end,random.uniform(1.12,1.50))
material('canopy',(.8,.82,.77),.83)
for side in [-1,1]:
    for x in range(-57,65,12):
        tree(x+(2 if side>0 else -1)+random.uniform(-.85,.85),side*(7.47+random.uniform(-.16,.16)))
    for x in [-39,-9,24,54]:
        y=side*7
        pole('charcoal',(x,y,.16),(x,y,6.9),.092,.054);collide(x,y,.18,.18)
        pole('silver',(x,y,6.85),(x,y-side*1.6,7.14),.055,.038)
        box('charcoal',x,y-side*1.61,7.12,.38,.64,.105)
# Road furniture and paint are modelled in small material batches.
for x in range(-67,68,3):
    if abs(x-12)<5:continue
    pole('charcoal',(x,0,.02),(x,0,.74),.055,.055)
    for z in [.24,.55]:
        pole('ochre',(x,0,z),(x,0,z+.095),.057,.057)
        if abs(x+3-12)>=5:pole('charcoal',(x,0,z),(x+3,0,z),.023,.023)
    collide(x,0,.11,.11,.74)
    if abs(x+3-12)>=5:collide(x+1.5,0,3,.046,.573)
for y in [-.13,.13]:box('ochre',0,y,.023,143,.075,.014)
# Extend only the visual horizon outside the playable circle.
for end in [-1,1]:
    box('asphalt',end*129,0,-.252,95,75,.5)
    for edge in [-1,1]:
        box('paver',end*122,edge*8.8,.07,94,4.6,.14)
        for i in range(5):
            x=end*(81+i*17);height=12+(i*7+(3 if edge<0 else 0))%19
            y=edge*(18+i%2*2.2);width=13+i%3
            box('plaster' if i%2 else 'stone',x,y,height/2,width,13,height)
            for z in range(3,height,3):
                box('smoke',x,y-edge*6.57,z,width-.8,.11,1.44)
                for k in [-2,-1,0,1,2]:box('silver',x+k*2.2,y-edge*6.66,z,.053,.062,1.44)
    for j in range(4):
        h=15+6*j;box('stone',end*(160+3*j),-22+j*15,h/2,16,14,h)
# Load generated image finishes into the source scene and embed them in glTF.
finish_names={'tile':'tile.jpg','granite':'granite.jpg','bark':'bark-photo.jpg','violet':'violet.jpg','canopy':'leaf-photo.png','paver':'sidewalk.jpg'}
for key,file in finish_names.items():
    m=materials[key];bs=m.node_tree.nodes.get('Principled BSDF')
    tx=m.node_tree.nodes.new('ShaderNodeTexImage')
    tx.image=bpy.data.images.load(str(root/'source/finishes'/file));tx.image.pack()
    m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
    if key=='canopy':
        m.node_tree.links.new(tx.outputs['Alpha'],bs.inputs['Alpha']);m.use_backface_culling=False
pbr={'asphalt':('asphalt_04',4.2),'brick':('brick_wall_006',3.1),'stone':('brushed_concrete_03',3.5),'plaster':('brushed_concrete_03',4.5),'curb':('brushed_concrete_03',1.7)}
for name,(stem,scale) in pbr.items():
    m=materials[name];nodes=m.node_tree.nodes;bs=nodes.get('Principled BSDF')
    for kind in ['diff','nor_gl']:
        pic=bpy.data.images.load(str(root/'public/materials'/f'{stem}_{kind}.jpg'),check_existing=True);pic.pack()
        tex=nodes.new('ShaderNodeTexImage');tex.image=pic
        if kind=='diff':m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        else:
            pic.colorspace_settings.name='Non-Color'
            normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.58
            m.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
for mat,(verts,faces) in buffers.items():
    data=bpy.data.meshes.new(mat);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(mat,data);bpy.context.collection.objects.link(obj);data.materials.append(materials[mat])
    if mat=='windscreen':
        bs=materials[mat].node_tree.nodes.get('Principled BSDF')
        bs.inputs['Alpha'].default_value=.52
        materials[mat].use_backface_culling=True
    if mat in finish_names or mat in pbr:
        uv=data.uv_layers.new(name='UVMap')
        sizes={'tile':1.85,'granite':2.9,'bark':1.1,'paver':2.5,'violet':6.7,'canopy':1}
        sizes.update({k:v[1] for k,v in pbr.items()})
        for poly in data.polygons:
            nx,ny,nz=map(abs,poly.normal)
            for j,loop in enumerate(poly.loop_indices):
                x,y,z=verts[data.loops[loop].vertex_index]
                if mat=='canopy':coord=[(0,0),(1,0),(1,1),(0,1)][j]
                elif mat=='violet':coord=((x+19.45)/6.7,z)
                else:coord=((y if nx>ny and nx>nz else x)/sizes[mat],(y if nz>max(nx,ny) else z)/sizes[mat])
                uv.data[loop].uv=coord
    if mat in {'pearl','graphite','windscreen','rubber','alloy'}:
        data.set_sharp_from_angle(angle=math.radians(44))
        for poly in data.polygons:poly.use_smooth=True
    if mat.startswith('leaf'):materials[mat].use_backface_culling=False
bpy.context.scene.unit_settings.system='METRIC'
import sys
sys.path.insert(0,str(root/'source'))
from cafe import furnish,studio
furnish()
from occlusion import bake
bake(bpy.context.scene.objects)
studio(root)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source/street.blend'))
bpy.ops.export_scene.gltf(filepath=str(root/'public/street.glb'),export_format='GLB',export_texcoords=True,export_vertex_color='ACTIVE',export_apply=True,export_lights=False,export_cameras=False)
(root/'public/obstacles.json').write_text(json.dumps(bounds))
(root/'public/walkways.json').write_text(json.dumps(walkways))

bpy.ops.render.render(write_still=True)
