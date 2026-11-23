"""Observed retail elevations in the street study; model dimensions are approximate."""
import math, random
from pathlib import Path
import bpy

def add_shops(material,box,pole,mesh,collide,materials):
    for name,color,rough,metal in [
        ('chalkwall',(.81,.80,.75),.83,0),('deepblue',(.015,.055,.18),.43,.18),('fascia',(.014,.05,.115),.53,.23),
        ('tile',(.72,.7,.62),.77,0),('granite',(.56,.55,.51),.9,0),('violet',(.43,.15,.45),.48,.1),
        ('awning',(.41,.045,.055),.86,0),('pink',(.7,.37,.52),.6,0),('yellow',(.98,.68,.032),.43,0),
        ('orange',(.94,.35,.075),.46,0),('cream',(.92,.89,.78),.45,.08),('greenletters',(.19,.45,.21),.58,0),
        ('tint',(.084,.14,.139),.18,.42),('shrub',(.10,.20,.038),.98,0)]:
        material(name,color,rough,metal)
    # Font geometry is converted once and batched by material before export.
    font=bpy.data.fonts.load('/System/Library/Fonts/AppleSDGothicNeo.ttc')
    latin=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
    def text(label,x,y,z,w,h,mat,turn=0):
        c=bpy.data.curves.new(label,'FONT');c.body=label;c.font=font if any(ord(a)>127 for a in label) else latin
        c.align_x='CENTER';c.align_y='CENTER';c.extrude=.009;c.bevel_depth=.003;c.offset=.008;c.resolution_u=4;c.bevel_resolution=1
        o=bpy.data.objects.new(label,c);bpy.context.collection.objects.link(o)
        bpy.context.view_layer.update()
        sx=w/max(o.dimensions.x,.001);sy=h/max(o.dimensions.y,.001)
        o.scale=(sx,sy,.8);o.location=(x,y,z);o.rotation_euler=(math.pi/2,0,turn)
        bpy.context.view_layer.update()
        ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        mesh(mat,[tuple(o.matrix_world@v.co) for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);ev.to_mesh_clear()
        bpy.data.objects.remove(o,do_unlink=True);bpy.data.curves.remove(c)
    # The upper glass ribbon sits between stone-clad end bays.
    for sign in [-1,1]:
        box('chalkwall',sign*7.49,10.83,12.04,2.94,.22,15.07)
        for floor in range(5):
            z=5.94+floor*3.0
            box('glass',sign*7.51,10.68,z,1.03,.12,1.43)
            box('silver',sign*7.51,10.60,z-.69,1.10,.14,.045)
        for j in range(19):
            box('silver',sign*7.49,10.707,4.82+j*.78,2.96,.036,.016)
    for i in range(-5,6):
        box('silver',i*1.09,10.695,12.1,.041,.09,15.15)
    for j in range(11):
        box('silver',0,10.69,5.1+j*1.36,11.88,.10,.064)
    # Alternating broad pale piers and recessed windows, rather than a glass wall.
    for x,w in [(-8.4,1.0),(-5.2,2.0),(-1.63,1.15),(2.02,1.2),(5.74,1.85),(8.57,.75)]:
        box('chalkwall',x,10.67,1.78,w,.51,3.0)
    box('fascia',0,10.45,3.78,18.25,.62,1.52)
    box('fascia',9.01,16.86,3.78,.28,13.0,1.52)
    for z in [3.07,4.50]:box('deepblue',0,10.12,z,18.30,.10,.07)
    text('EDIYA COFFEE',0,10.105,3.78,8.55,.72,'cream')
    text('이디야커피',-3.8,10.098,3.28,.71,.105,'cream')
    for x in range(-8,9,2):
        pole('silver',(x,10.35,4.58),(x,10.00,4.69),.024,.024)
        box('silver',x,9.99,4.64,.18,.13,.10)
    for x in [-.89,.07,1.03]:box('deepblue',x,10.33,1.59,.085,.12,2.84)
    for z,h in [(.45,.52),(2.98,.09)]:
        box('deepblue',.07,10.33,z,2.01,.12,h)
    for x in [-.03,.16]:box('silver',x,10.23,1.32,.035,.06,.34)
    text('더킹고등수학전문학원',9.19,16.9,3.82,4.75,.42,'greenletters',math.pi/2)
    for k,word in enumerate(['더킹','고등','수학']):
        x=-1.28+k*1.14;box('chalkwall',x,10.72,5.13,1.12,.07,.58);text(word,x,10.67,5.13,.85,.35,'charcoal')
    pole('deepblue',(9.17,11.25,3.92),(9.38,11.25,3.92),.46,.46,48)
    pole('cream',(9.38,11.25,3.92),(9.4,11.25,3.92),.404,.404,48)
    text('EDIYA',9.416,11.25,3.97,.57,.16,'deepblue',math.pi/2)
    text('COFFEE',9.416,11.25,3.75,.55,.105,'deepblue',math.pi/2)
    # Street-view 11–13: the lane sees two different elevations.
    # The academy side has round columns and a continuous turquoise window ribbon.
    for y in [11.68,16.48,21.2]:
        pole('stone',(8.97,y,4.53),(8.97,y,7.25),.34,.34,32)
        for z in [5.40,6.32]:pole('silver',(8.97,y,z),(8.97,y,z+.018),.342,.342,32)
    for row in range(5):
        z=5.83+3.03*row
        for j in range(10):
            y=11.68+1.20*j
            box('tint',9.047,y,z,.12,1.15,2.67)
            box('silver',9.122,y,z+.39,.09,1.19,.048)
            box('silver',9.12,y-.589,z,.08,.044,2.78)
        box('stone',9.10,17.18,z+1.41,.36,12.95,.18)
    for j,word in enumerate(['더킹','고등','수학','전문','학원']):
        y=13.02+j*1.18
        box('chalkwall',9.14,y,5.08,.09,1.10,.54)
        text(word,9.196,y,5.08,.77,.32,'charcoal',math.pi/2)
    for y in [11.49,15.52,19.50,22.78]:
        box('chalkwall',8.94,y,1.69,.34,1.04,2.80)
    # Opposite corner: tiled piers, square punched openings and dark inset frames.
    for row in range(4):
        for j in range(6):
            y=12.17+j*1.87;z=5.43+3.04*row
            box('charcoal',13.84,y,z,.11,1.24,1.56)
            box('smoke',13.768,y,z+.012,.052,1.09,1.38)
            box('silver',13.722,y,z-.14,.053,1.11,.047)
            box('stone',13.77,y,z-.80,.25,1.32,.070)
    rng=random.Random(137)
    def planter(x,y,w,d):
        box('granite',x,y,.48,w,d,.68);box('stone',x,y,.82,w+.045,d+.045,.09)
        box('earth',x,y,.874,w-.12,d-.12,.04);collide(x,y,w,d)
        for _ in range(int(w*d*95)):
            px=x+rng.uniform(-w*.48,w*.48);py=y+rng.uniform(-d*.48,d*.48)
            z=.88+rng.uniform(.08,.36);r=rng.uniform(.045,.105)
            for a in [rng.uniform(0,math.pi),rng.uniform(math.pi,2*math.pi)]:
                vx=math.cos(a)*r*1.7;vy=math.sin(a)*r*1.7
                mesh('canopy',[(px-vx,py-vy,z-r),(px+vx,py+vy,z-r),(px+vx,py+vy,z+r),(px-vx,py-vy,z+r)],[(0,1,2,3)])
    planter(-5.15,10.10,7.5,.66);planter(5.56,10.10,7.12,.66);planter(9.0,16.75,.7,12.65)
    # Form the visible depth behind each pane with reveals and low-reflectance backing.
    for x in [-7.15,-3.46,3.8,7.26]:
        for jamb in [-1.13,1.13]:box('chalkwall',x+jamb,11.19,1.74,.075,.86,2.88)
        box('stone',x,11.02,.37,2.28,.73,.13)
        for edge in [-1.10,1.10]:box('silver',x+edge,11.05,1.76,.035,.075,2.9)
    for x in [-.49,.54]:box('silver',x,10.48,2.72,.84,.04,.041)
    # Freestanding display seen beside the blue door; use an original drink illustration.
    box('charcoal',1.34,10.08,1.03,.74,.12,1.68)
    box('deepblue',1.34,10.006,1.05,.675,.04,1.57)
    # Narrow corner bay adjoining the violet fascia.
    box('charcoal',-9.78,11.1,5.1,1.24,.27,9.6)
    for h in range(6):
        box('glass',-9.78,10.92,1+h*1.53,1.02,.08,1.40)
        box('silver',-9.78,10.84,.30+h*1.53,1.13,.12,.055)
    # Left shop. Preserve the legible letters; the preceding mark is indistinct.
    box('charcoal',-15.8,11.18,2.05,11.4,.8,3.65)
    box('violet',-16.1,10.72,3.12,6.7,.14,.97)
    text('ELFBAR',-16.05,10.625,3.13,3.35,.48,'cream')
    box('chalkwall',-16.1,10.73,1.48,5.85,.11,2.07)
    box('awning',-17.62,10.65,1.64,1.50,.07,.50);text('임대문의',-17.62,10.606,1.64,1.15,.26,'cream')
    box('violet',-10.55,10.83,3.55,.83,.21,2.24)
    for j,t in enumerate(['코인','노래','연습장','B1']):text(t,-10.55,10.71,4.25-j*.46,.66,.34,'cream')
    # Public lettering on two faces of the snack shop.
    box('charcoal',19.0,10.77,3.29,10.46,.32,1.02)
    box('charcoal',13.77,16.72,3.29,.31,12.0,1.02)
    for side in [False,True]:
        for label,offset,width,mat in [('소풍',-1.9,1.65,'yellow'),('김밥',-.16,1.52,'cream'),('분식',1.53,1.54,'orange')]:
            if side:text(label,13.59,16.72-offset,3.27,width,.54,mat,-math.pi/2)
            else:text(label,19+offset,10.585,3.27,width,.54,mat)
    box('cream',22.38,10.57,3.25,1.0,.08,.47);text('한티점',22.38,10.515,3.25,.76,.26,'charcoal')
    for x in [15.25,17.74,20.23,22.72]:
        box('charcoal',x-1.20,11.05,1.65,.06,.62,2.27);box('pink',x,10.70,.68,2.46,.045,.44)
    for y in [12.2,14.75,17.3,19.85]:
        box('charcoal',14.02,y-1.24,1.64,.62,.06,2.24);box('pink',13.70,y,.68,.045,2.48,.44)
    for x in [15.25,17.74,20.23,22.72]:
        for z in [.93,2.53]:box('silver',x,10.69,z,2.46,.06,.045)
        text('소풍',x,10.704,1.76,.58,.20,'cream')
    for y in [12.2,14.75,17.3,19.85]:
        box('silver',13.67,y,.94,.05,2.46,.045)
    for k,t in enumerate(['올바른','영어']):
        x=18.25+k*2.12;box('chalkwall',x,10.84,5.6,1.53,.06,.63);text(t,x,10.79,5.6,1.15,.43,'charcoal')
    for x in [14.1,23.85]:box('pink',x,10.60,1.65,.37,.13,2.42)
    mesh('awning',[(14,10.6,2.94),(23.9,10.6,2.94),(23.9,9.96,2.65),(14,9.96,2.65)],[(0,1,2,3)])
    box('awning',18.95,9.95,2.60,9.92,.06,.13)
