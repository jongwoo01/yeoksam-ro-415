"""Build street-facing display volumes. Background light is illustrative."""
import bpy,math,random
from pathlib import Path

def fit_windows(material,box,pole,mesh,materials):
    material('window reveal',(.28,.245,.20),.87)
    material('interior ceiling',(.35,.31,.26),.95)
    material('warm diffuser',(.92,.74,.48),.38)
    emitter=materials['warm diffuser'].node_tree.nodes.get('Principled BSDF')
    emitter.inputs['Emission Color'].default_value=(1,.72,.38,1);emitter.inputs['Emission Strength'].default_value=2.2
    material('plant stem',(.058,.082,.028),.82)
    material('palm blade',(.056,.17,.054),.74)
    material('glazed ceramic',(.23,.215,.175),.37)
    for x in [-7.1,-3.45,3.82,7.26]:
        box('window reveal',x,12.05,.40,2.19,2.25,.14)
        for j in range(2):
            pole('charcoal',(x+j*.52-.28,12.12,3.13),(x+j*.52-.28,12.12,3.0),.023,.024)
            pole('warm diffuser',(x+j*.52-.28,12.12,2.99),(x+j*.52-.28,12.12,3.01),.068,.071,18)
    rng=random.Random(102)
    # Leaf silhouettes sit at two separate depths; behind them the light changes with parallax.
    for x,y in [(-.72,12.14),(2.9,13.02)]:
        pole('glazed ceramic',(x,y,.23),(x,y,.69),.21,.27,24)
        for i in range(37):
            az=i*2.4;reach=rng.uniform(.25,.60);start=(x,y,.63)
            end=(x+reach*.37*math.cos(az),y+reach*.37*math.sin(az),rng.uniform(1.05,1.8))
            pole('plant stem',start,end,.013,.008)
            tip=(x+reach*math.cos(az),y+reach*math.sin(az),end[2]+rng.uniform(.02,.31))
            mx=(end[0]+tip[0])*.5;my=(end[1]+tip[1])*.5;mz=(end[2]+tip[2])*.5+.08
            mesh('palm blade',[end,(mx-.068*math.sin(az),my+.068*math.cos(az),mz),tip,(mx+.068*math.sin(az),my-.068*math.cos(az),mz)],[(0,1,2,3)])
    # Recessed restaurant shell is shadowed by its real corner canopy and window returns.
    box('window reveal',19,13,.26,10.3,5.1,.18)
    box('interior ceiling',19,13,2.87,10.4,5.0,.15)
    for x in [15.25,17.74,20.23,22.72]:
        box('silver',x,11.03,.99,2.43,.57,.09)
        box('charcoal',x-1.20,12.14,2.35,.07,2.4,.09)
        box('warm diffuser',x,12.68,2.76,.52,.12,.036)
    def printed_face(label,file,x,y,z,w,h):
        mat=bpy.data.materials.new(label);mat.use_nodes=True
        nodes=mat.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage')
        tex.image=bpy.data.images.load(str(Path(__file__).parent/'finishes'/file),check_existing=True);tex.image.pack()
        bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.69
        mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        points=[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)]
        data=bpy.data.meshes.new(label);data.from_pydata(points,[],[(0,1,2,3)]);data.update();uv=data.uv_layers.new()
        for j,val in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[j].uv=val
        o=bpy.data.objects.new(label,data);bpy.context.collection.objects.link(o);data.materials.append(mat)
    printed_face('음료 안내판','drink-board.jpg',1.34,9.978,1.05,.66,1.53)
    for x in [14.10,23.85]:printed_face('분식 그림 메뉴','food-strip.jpg',x,10.522,1.65,.34,2.32)
    # Two curved backdrops carry only a softly exposed room-light treatment.
    img=bpy.data.images.load(str(Path(__file__).parent/'finishes/interior-light.jpg'));img.pack()
    for label,cx,cy,width,depth,roof,offset in [('coffee',0,11.45,17.2,4.7,3.15,.02),('snack',19,11.36,10.25,3.65,2.85,.55)]:
        m=bpy.data.materials.new(label+' interior daylight');m.use_nodes=True
        ns=m.node_tree.nodes;bs=ns.get('Principled BSDF');texture=ns.new('ShaderNodeTexImage');texture.image=img
        m.node_tree.links.new(texture.outputs['Color'],bs.inputs['Base Color'])
        m.node_tree.links.new(texture.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.37
        points=[];faces=[];coords=[]
        for k in range(41):
            f=k/40;a=math.pi*f
            x=cx-width*.5*math.cos(a);y=cy+depth*math.sin(a)
            points.extend([(x,y,.22),(x,y,roof)])
            coords.extend([(offset+f*.47,.255),(offset+f*.47,.68)])
            if k:faces.append((k*2-2,k*2,k*2+1,k*2-1))
        data=bpy.data.meshes.new(label);data.from_pydata(points,[],faces);data.update()
        layer=data.uv_layers.new(name='UVMap')
        for loop in data.loops:layer.data[loop.index].uv=coords[loop.vertex_index]
        o=bpy.data.objects.new(label+' · 창 너머 조명',data);bpy.context.collection.objects.link(o);data.materials.append(m)
