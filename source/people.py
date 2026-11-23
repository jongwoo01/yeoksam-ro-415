"""Build two jointed, clothed street avatars in metres, facing local -Y."""
import math
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
for style in ('man','woman'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    woman=style=='woman'
    colors={'knit':'9d5143' if woman else '344e65','rib':'884537' if woman else '293f54',
            'shirt':'f2eee1','slacks':'3a3836' if woman else '454a50','leather':'473c38',
            'sole':'27292b','skin':'d49e80','hair':'332723','eye':'30282a','lip':'a5635b'}
    materials={}
    for name,color in colors.items():
        m=bpy.data.materials.new(name);m.use_nodes=True
        b=m.node_tree.nodes.get('Principled BSDF')
        b.inputs['Base Color'].default_value=tuple(((int(color[i:i+2],16)/255+.055)/1.055)**2.4 for i in (0,2,4))+(1,)
        b.inputs['Roughness'].default_value=.48 if name in ('leather','eye') else .83
        if name in ('knit','rib'):b.inputs['Sheen Weight'].default_value=.28
        materials[name]=m

    def pivot(name,parent=None,at=(0,0,0)):
        obj=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(obj);obj.parent=parent;obj.location=at
        return obj
    def shape(name,parent,mat,pts,faces):
        data=bpy.data.meshes.new(name);data.from_pydata(pts,[],faces);data.update()
        obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);obj.parent=parent
        data.materials.append(materials[mat])
        for poly in data.polygons:poly.use_smooth=True
        return obj
    def rings(name,parent,mat,sections,n=32):
        # (height, half width, half depth, centre X, centre Y), ordered bottom to top.
        pts=[(x+w*math.cos(j*math.tau/n),y+d*math.sin(j*math.tau/n),z)
             for z,w,d,x,y in sections for j in range(n)]
        faces=[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(len(sections)-1) for j in range(n)]
        faces.extend([tuple(reversed(range(n))),tuple(range(len(pts)-n,len(pts)))])
        obj=shape(name,parent,mat,pts,faces)
        for cap in list(obj.data.polygons)[-2:]:cap.use_smooth=False
        return obj
    def oval(name,parent,mat,at,r):
        x,y,z=at;w,d,h=r
        return rings(name,parent,mat,[(z+h*math.sin(a),max(.001,w*math.cos(a)),max(.001,d*math.cos(a)),x,y)
                    for a in [-1.57,-1.25,-.95,-.62,-.31,0,.31,.62,.95,1.25,1.57]],20)
    def centered(rows):return [(z,w,d,0,0) for z,w,d in rows]
    body=pivot('body')
    if woman:body.scale=(.94,.95,.96)
    rings('hip',body,'slacks',centered([(.77,.145,.087),(.83,.166,.106),(.94,.15,.099)]))
    shoulders=.192 if woman else .213
    rings('pullover',body,'knit',centered([(.888,.153,.105),(.92,.162,.110),(.96,.179,.116),(1.10,.169,.112),(1.23,shoulders,.120),(1.33,shoulders,.103),(1.38,.156,.079),(1.396,.087,.071)]))
    rings('waistband',body,'rib',centered([(.888,.154,.106),(.898,.157,.109),(.933,.165,.112)]))
    rings('neck',body,'skin',centered([(1.37,.062,.052),(1.51,.058,.051)]))
    rings('shirt collar stand',body,'shirt',centered([(1.381,.096,.077),(1.405,.088,.071),(1.444,.068,.060)]))
    for side in (-1,1):
        pts=[(side*x,y,z) for x,y,z in [(.003,-.066,1.43),(.066,-.050,1.439),(.102,-.062,1.399),(.053,-.109,1.344)]]
        shape('folded collar',body,'shirt',pts,[(0,1,2,3),(3,2,1,0)])
    head=pivot('head',body,(0,0,1.575))
    rings('face',head,'skin',[(z,w,d,0,y) for z,w,d,y in [(-.125,.043,.049,-.019),(-.111,.067,.070,-.012),(-.068,.088,.088,-.004),(-.008,.104,.100,0),(.061,.106,.098,.005),(.111,.091,.081,.008),(.14,.038,.045,.008)]])
    for side in (-1,1):
        oval('ear',head,'skin',(side*.103,.004,-.009),(.018,.024,.035))
        oval('eye',head,'eye',(side*.042,-.094,.001),(.012,.005,.005))
        oval('brow',head,'hair',(side*.043,-.092,.020),(.022,.005,.004))
    oval('nose',head,'skin',(0,-.102,-.022),(.015,.015,.024))
    oval('mouth',head,'lip',(0,-.091,-.058),(.022,.005,.004))
    pts=[];faces=[];n=40
    for k in range(12):
        for j in range(n):
            a=j*math.tau/n;front=max(0,-math.sin(a))
            edge=(2.35 if not woman else 2.71)-front*(1.02 if not woman else 1.44)+.11*math.cos(a)*front
            t=.015+(edge-.015)*k/11
            pts.append((.113*math.sin(t)*math.cos(a),.009+.113*math.sin(t)*math.sin(a),.024+.143*math.cos(t)))
    for k in range(11):
        for j in range(n):faces.append((k*n+j,(k+1)*n+j,(k+1)*n+(j+1)%n,k*n+(j+1)%n))
    shape('parted hair',head,'hair',pts,faces)
    if woman:
        for side in (-1,1):
            rings('face framing lock',head,'hair',[(z,w,d,side*x,y) for z,w,d,x,y in [
                (-.124,.006,.006,.086,-.035),(-.085,.013,.017,.100,-.034),
                (-.022,.015,.024,.101,-.032),(.055,.018,.029,.093,-.028),(.10,.014,.02,.079,-.025)]])
        oval('low ponytail',head,'hair',(0,.109,-.116),(.050,.046,.118))
        oval('hair tie',head,'rib',(0,.116,-.046),(.042,.041,.016))
    for s,side in [(-1,'L'),(1,'R')]:
        thigh=pivot('leg'+side,body,(s*.086,0,.823))
        rings('trouser thigh',thigh,'slacks',centered([(-.39,.063,.067),(-.29,.073,.078),(-.10,.086,.092),(.048,.081,.087)]))
        shin=pivot('knee'+side,thigh,(0,0,-.366))
        rings('trouser calf',shin,'slacks',centered([(-.361,.056,.061),(-.32,.061,.065),(-.14,.066,.071),(.016,.063,.067)]))
        ankle=pivot('ankle'+side,shin,(0,0,-.35))
        for mat,rows in [('sole',[(-.454,.061,.120,-.044),(-.445,.065,.129,-.044),(-.428,.065,.129,-.044)]),
                         ('leather',[(-.432,.064,.127,-.044),(-.407,.064,.124,-.046),(-.381,.060,.106,-.030),(-.352,.053,.061,.002)])]:
            rings('shoe '+mat,ankle,mat,[(z+.35,w,d,0,y) for z,w,d,y in rows])
        arm=pivot('arm'+side,body,(s*(shoulders-.014),0,1.306))
        rings('sweater sleeve',arm,'knit',[(-.254,.048,.052,s*.040,0),(-.20,.056,.060,s*.037,0),(-.08,.066,.071,s*.025,0),(.035,.060,.062,0,0),(.054,.039,.044,0,0)])
        fore=pivot('elbow'+side,arm,(s*.040,0,-.230))
        rings('forearm sleeve',fore,'knit',centered([(-.213,.041,.042),(-.15,.048,.050),(-.05,.053,.055),(.017,.047,.050)]))
        rings('ribbed cuff',fore,'rib',centered([(-.227,.039,.041),(-.20,.043,.045)]))
        rings('shirt cuff',fore,'shirt',centered([(-.243,.038,.040),(-.222,.038,.040)]))
        oval('hand',fore,'skin',(0,-.006,-.285),(.032,.030,.057))
        oval('thumb',fore,'skin',(-s*.021,-.026,-.27),(.014,.013,.027))
    chest=pivot('chest',body,(0,0,.91))
    for obj in list(body.children):
        if obj not in (chest,) and obj.name not in ('legL','legR','hip'):
            obj.parent=chest
            obj.location.z-=.91
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source'/f'knit-{style}.blend'))
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'public'/f'knit-{style}.glb'),export_format='GLB')
