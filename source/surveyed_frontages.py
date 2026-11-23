"""Publicly visible elevations from the November survey, frames 35–51. Units are metres."""
import math

def add_frontages(box,pole,text,collide):
    # Western neighbour, frame 51: two unequal glazing bays in a tall stone frame.
    for x,width in [(-17.73,7.66),(-11.38,1.98)]:
        box('charcoal',x,11.04,14.67,width+.16,.20,21.28)
        for level in range(7):
            z=5.5+level*3.05
            box('glass',x,10.90,z,width,.12,2.92)
            for offset in [-1.06,-.19,.96]:
                box('silver',x,10.80,z+offset,width+.06,.12,.063)
            for j in range(1,round(width/1.6)):
                xx=x-width/2+width*j/round(width/1.6)
                box('silver',xx,10.81,z,.042,.08,2.94)
    box('stone',-13.30,10.96,14.78,1.04,.33,21.0)
    box('stone',-15.80,11.01,25.67,12.6,.52,.58)
    box('navy',-19.13,10.68,24.79,3.67,.09,.66)
    # Basement stair and recessed glass door beside the purple fascia, frames 16, 48–49.
    box('charcoal',-11.99,10.67,1.62,2.96,.18,2.81)
    for i in range(3):
        box('granite',-12,10.45-i*.16,.19+(2-i)*.085,2.22,.20,.15)
    for i in [-1,1]:
        box('glass',-12+i*.48,10.55,1.55,.86,.06,2.11)
        box('silver',-12+i*.49,10.48,1.05,.032,.07,.42)
    box('wood',-19.90,10.58,3.11,2.50,.19,.98)
    text('스시노스시',-19.90,10.46,3.12,2.03,.35,'charcoal')
    # Enclose the ground-storey shell behind the inhabited frontage.
    for x in [-22.04,-9.47]:
        box('stone',x,17.68,1.72,.17,12.86,3.44)
    box('stone',-15.76,24.02,1.72,12.74,.18,3.44)
    # Rear bays are screened from public road view: continue the known storey and pier rhythm.
    for level in range(7):
        z=5.5+level*3.05
        for x in [-20.29,-17.42,-14.55,-11.68]:
            box('charcoal',x,24.15,z,2.04,.12,1.49)
            box('tint',x,24.23,z,1.86,.06,1.32)
            box('silver',x,24.28,z,.045,.045,1.32)
        box('stone',-15.76,24.17,z-1.03,12.77,.22,.13)

    # Seongjin's recessed lane entrance and triangular steel canopy (35, 37, 43).
    for y in [20.68,23.67]:
        box('granite',9.04,y,1.67,.49,.49,3.18)
    box('charcoal',8.99,22.18,1.69,.17,2.54,2.89)
    for y in [21.62,22.74]:
        box('tint',9.109,y,1.52,.050,1.04,2.28)
        box('silver',9.16,y,1.37,.06,.035,.34)
    box('granite',9.13,22.18,3.04,.34,3.16,.76)
    text('성 진 빌 딩',9.315,22.18,3.05,2.43,.36,'charcoal',math.pi/2)
    box('deepblue',9.28,23.58,1.84,.045,.32,.42)
    text('415',9.31,23.58,1.84,.26,.18,'cream',math.pi/2)
    for y in [20.30+i*.55 for i in range(8)]:
        pole('silver',(9.0,y,3.50),(9.84,y,3.50),.034,.034)
        pole('silver',(9.0,y,3.98),(9.84,y,3.50),.033,.033)
        pole('silver',(9.84,y,3.50),(9.0,y+.54,3.98),.028,.028)
    for x,z in [(9,3.98),(9.84,3.50)]:pole('silver',(x,20.30,z),(x,24.16,z),.038,.038)
    # The planter turns the corner after a break for the entrance.
    box('granite',9.04,24.10,.46,.68,1.02,.64)
    for y in [20.39,23.95]:
        box('granite',9.23,y,.18,.71,.38,.13)

    # Restaurant along the lane and PC entrance to its rear (36, 39–40).
    for j in range(5):
        y=13.98+j*1.84
        box('violet',13.698,y,5.47,.055,1.02,1.08)
        text('미술학원',13.657,y,5.45,.85,.21,'cream',-math.pi/2)
    for j in range(3):
        box('wood',13.50+j*.13,19.54,.18+j*.075,.17,2.63,.14)
    box('charcoal',13.57,22.40,2.94,.38,2.02,.88)
    text('PC',13.365,22.40,2.95,1.44,.62,'awning',-math.pi/2)
    box('charcoal',13.57,23.21,5.02,.32,.68,3.16)
    for j,label in enumerate(['P','C','B1']):
        text(label,13.39,23.21,5.91-j*.76,.49,.53,'cream' if j==2 else 'awning',-math.pi/2)
    for a,b in [((13.48,22.16,11.9),(13.48,22.16,4.3)),((13.48,22.16,4.3),(13.48,21.57,3.35)),((13.48,21.57,3.35),(13.48,20.92,3.35))]:
        pole('silver',a,b,.12,.12,16)
    # Photograph 40: small horizontal rear windows, exposed rainwater pipes, exterior condensers.
    for level in range(4):
        for x in [15.14,17.47,19.94,22.63]:
            z=4.95+level*3.02
            box('charcoal',x,23.49,z,1.14,.11,.55)
            box('tint',x,23.56,z,1.03,.04,.42)
            box('silver',x,23.60,z,.032,.04,.43)
    for x in [16.19,21.44]:pole('silver',(x,23.56,.26),(x,23.56,15.62),.044,.044)
    for j in range(4):
        x=14.63+(j%2)*.88;z=2.62+(j//2)*.68
        box('chalkwall',x,23.71,z,.82,.42,.60)
        pole('charcoal',(x,23.925,z),(x,23.94,z),.205,.205,24)
        for k in range(6):box('silver',x,23.95,z-.14+k*.055,.39,.019,.013)
    # Photo 39: motor court between the tiled wall and the next building.
    box('stone',19.84,27.40,.015,11.90,7.55,.06)
    for x in [15.18,18.02,20.86,23.70]:box('paint',x,27.61,.054,.055,6.93,.018)
    box('paint',19.43,30.97,.054,8.60,.063,.018)
    for j in range(20):box('charcoal',13.86,24.3+j*.32,.061,.43,.033,.016)
    for x,y in [(13.84,23.79),(14.52,25.22)]:
        box('rubber',x,y,.095,.35,.35,.08)
        pole('orange',(x,y,.10),(x,y,.65),.15,.044,20)
        pole('cream',(x,y,.38),(x,y,.46),.094,.078,20)

    # Opposite Seongjin, storefronts observed in 45, 46 and 50.
    for x,y,label,colour in [(7.5,-11.39,'MEGA MGC COFFEE','stone'),(-6.7,-11.45,'디피매쓰 수학학원','deepblue')]:
        for j in range(4):
            xx=x-3.30+j*2.20
            box('charcoal',xx-1.055,y-.24,1.70,.11,.16,2.92)
            box('snack glazing',xx,y-.13,1.65,2.02,.07,2.57)
            box('silver',xx-.99,y-.06,1.61,.052,.055,2.64)
        box(colour,x,y,3.36,9.02,.31,.82)
        text(label,x,y+.19,3.38,6.47,.40,'cream',math.pi)
    box('yellow',7.5,-11.16,2.88,9.05,.34,.14)
    for z in [4.63+i*2.84 for i in range(5)]:
        box('glass',3.23,-11.43,z,1.07,.34,2.72)
        box('silver',3.23,-11.23,z+1.32,1.09,.09,.074)

    # Opposite the parking entrance, photo 42. Shopfronts face the narrow lane.
    for x,y,label in [(13.93,35.85,'라무진'),(13.93,42.46,'브레인팩토리')]:
        box('charcoal',x+.04,y,3.19,.31,5.70,.87)
        text(label,x-.15,y,3.19,3.80,.45,'cream',-math.pi/2)
        for j in range(3):
            yy=y-1.92+j*1.91
            box('charcoal',x+.15,yy,1.56,.16,1.89,2.64)
            box('glass',x+.045,yy,1.59,.070,1.71,2.31)
        box('stone',x-.17,y,.21,.61,5.68,.18)
    box('orange',8.94,35.16,4.52,.12,2.38,1.22)
    text('NEO CAT',9.02,35.16,4.54,1.88,.38,'charcoal',math.pi/2)
    # Crossing at the parking apron stays passable beside the retracted gate.
    for j in range(6):
        y=24.49+j*.22
        for dz in [0,.42]:
            pole('silver',(9.27,y,.17+dz),(9.27,y+.24,.85+dz),.022,.022)
            pole('silver',(9.27,y+.24,.17+dz),(9.27,y,.85+dz),.022,.022)
        pole('silver',(9.27,y,.11),(9.27,y,1.13),.021,.021)
    collide(9.27,25.09,.18,1.46,1.12)
    for i in range(3):
        box('rubber',6.26-i*2.54,24.93,.16,1.42,.24,.24)
        for dx in [-.41,.41]:box('ochre',6.26-i*2.54+dx,24.93,.29,.17,.22,.032)
    pole('silver',(8.82,24.31,.2),(8.82,24.31,2.75),.038,.038)
    pole('cream',(8.82,24.31,2.76),(8.82,24.31,2.99),.13,.10,20)

    # Later blocks on Yeoksam-ro 63-gil, 52–55.
    for side,x,y,label,board,ink in [
        (1,8.91,45.64,'육미식탁','cream','wood'),
        (-1,13.84,45.05,'묵 호 댁','cream','navy'),
        (-1,13.95,58.86,'전라도 맛','yellow','awning'),
        (1,8.65,58.10,'밀봉국수','wood','cream')]:
        turn=side*math.pi/2
        box(board,x,y,3.12,.29,5.21,.78)
        text(label,x+side*.16,y,3.13,4.24,.47,ink,turn)
        for k in [-1,0,1]:
            yy=y+k*1.65
            box('charcoal',x-side*.03,yy,1.56,.14,1.62,2.70)
            box('glass',x+side*.06,yy,1.56,.040,1.49,2.51)
            box('silver',x+side*.093,yy-.74,1.65,.045,.038,2.60)
        box('granite',x+side*.16,y,.19,.62,5.16,.15)
    for k in range(5):
        yy=43.44+k*.85
        box('awning',8.94,yy,4.87,.11,.79,1.24)
        text('홍콩반점'[k] if k<4 else '0410',9.01,yy,4.88,.55,.35,'cream',math.pi/2)
    for yy in [36.1,40.1,44.1]:
        box('glass',13.83,yy,6.3,.15,3.88,2.12)
        for h in [5.27,6.33,7.38]:box('silver',13.72,yy,h,.06,3.94,.052)
    # Rooftop parapets, projecting shutters and recessed door on the alley-facing west block.
    for z in [4.7,7.8,10.85]:
        for yy in [56.93,59.34,61.75]:
            box('charcoal',8.65,yy,z,.13,1.91,1.30)
            box('tint',8.74,yy,z,.04,1.76,1.16)
            box('silver',8.78,yy,z+.04,.05,.036,1.14)
    # Crossing gantry and overhead utility runs, visible in 04, 40 and 46.
    pole('charcoal',(7.42,7.05,.17),(7.42,7.05,6.36),.12,.075,14)
    pole('charcoal',(7.42,7.05,6.25),(14.32,7.05,6.25),.083,.055,12)
    box('charcoal',12.10,7.05,5.96,2.32,.25,.51)
    for yy in [28.2,46.8,65.1]:
        pole('granite',(13.56,yy,.05),(13.56,yy,9.4),.14,.10,14)
        pole('silver',(13.13,yy,8.89),(14.,yy,8.89),.047,.047)
    for start,end in [(10.9,28.2),(28.2,46.8),(46.8,65.1)]:
        for i in range(3):
            prev=None
            for k in range(9):
                t=k/8;pt=(13.45+i*.21,start+(end-start)*t,8.93-.45*math.sin(math.pi*t))
                if prev:pole('rubber',prev,pt,.018,.018,5)
                prev=pt

    # Low telecom bundles cross above the street between the two corner blocks (35, 61).
    for y0,y1,x0,x1,z0,z1 in [(27.95,18.45,13.58,9.06,8.44,7.87),
                                (-16.9,-21.4,12.88,18.64,6.53,6.92),
                                (-22.6,9.85,18.64,13.58,7.62,8.30)]:
        for j in range(3):
            last=(x0,y0+j*.13,z0)
            for k in range(1,13):
                t=k/12
                pt=(x0+(x1-x0)*t,y0+(y1-y0)*t+j*.13,z0+(z1-z0)*t-.45*math.sin(math.pi*t))
                pole('rubber',last,pt,.026 if j==0 else .016,.026 if j==0 else .016,5)
                last=pt

    # Separate lower openings on the cafe's alley face keep its opaque piers and
    # printed display continuous behind the long planter (photos 37 and 43).
    box('navy',8.83,15.74,1.75,.13,8.98,2.88)
    for y in [12.10,15.18,18.26]:
        box('tint',8.95,y,1.83,.08,2.18,2.49)
        box('silver',9.005,y-.99,1.79,.044,.048,2.54)
    text('EDIYA COFFEE',9.035,16.61,2.27,3.14,.38,'cream',math.pi/2)
    box('chalkwall',8.90,19.69,1.64,.30,.69,2.94)
    # Openings, lintels and awning below the ivy facing the parked cars (41).
    for x,shade in [(-7.41,'ochre'),(-3.80,'deepblue'),(.36,'awning'),(4.57,'tint')]:
        box('charcoal',x,31.94,1.53,2.92,.13,2.71)
        box(shade,x,31.84,1.79,2.65,.085,1.65)
        box('granite',x,31.78,.44,2.93,.22,.66)
        box('silver',x,31.75,1.95,.049,.07,1.87)
        box('stone',x,31.74,2.94,3.03,.45,.12)
    box('yellow',4.20,31.52,1.28,4.10,.032,.49)
    text('성진빌딩 관리실',4.20,31.486,1.29,2.77,.22,'charcoal')
    # The parking court to the east terminates at a pale party wall, with cars in front (39).
    box('chalkwall',27.31,28.34,4.8,.28,9.09,9.60)
    collide(27.31,28.34,.28,9.09)
    for i in range(7):box('silver',27.14,24.30+i*1.27,4.82,.022,.017,9.44)
    box('granite',27.13,28.36,.34,.07,9.0,.66)
    box('stone',20.71,31.22,.32,12.8,.25,.58)
    # Set the shop thresholds back from the glazed road frontage (45).
    for x in [3.32,11.69]:
        box('silver',x,-11.08,1.65,.11,.42,2.92)
    for k in range(8):
        box('silver',4.12+k*.43,-10.91,.61,.029,.029,.77)
    pole('silver',(4.06,-10.91,.99),(7.21,-10.91,.99),.036,.036)
    box('yellow',7.49,-11.04,2.85,9.00,.70,.12)
    for x in [5.15,7.49,9.83]:
        box('cream',x,-11.20,1.72,1.85,.12,.33)
    # Cafe signs are mounted *ahead* of the typical massing's projecting lintel.
    box('charcoal',7.50,-10.89,3.52,9.04,.19,.94)
    text('MEGA MGC COFFEE',7.50,-10.767,3.52,6.12,.46,'cream',math.pi)
    box('deepblue',-6.70,-10.89,3.26,8.97,.21,.68)
    text('디피매쓰 수학학원',-6.70,-10.759,3.26,5.36,.31,'cream',math.pi)
    box('cream',24.21,-11.08,3.21,10.43,.19,.78)
    text('제주우다',24.21,-10.946,3.23,3.88,.40,'navy',math.pi)

    # The south arm is a real driveable lane, not a pavement between generic blocks (61–64).
    text('30',15.63,-12.70,.019,1.09,2.22,'paint',flat=True)
    for x,y,length,label,board,ink,turn in [
        (12.91,-15.1,6.81,'MEGA MGC COFFEE','silver','cream',math.pi/2),
        (12.91,-20.7,3.36,'돌파수학','deepblue','cream',math.pi/2),
        (18.59,-14.7,5.89,'제주우다','cream','navy',-math.pi/2),
        (18.59,-19.55,3.60,'신마라명가','tint','cream',-math.pi/2),
        (18.59,-23.05,2.91,'초록 당구장','yellow','greenletters',-math.pi/2)]:
        outward=1 if x<15 else -1
        box(board,x,y,3.11,.33,length,.82)
        text(label,x+outward*.18,y,3.12,length*.78,.42,ink,turn)
        bays=max(2,round(length/1.57))
        for j in range(bays):
            yy=y+(j+.5-bays/2)*(length/bays)
            box('charcoal',x-outward*.11,yy-length/bays*.48,1.52,.12,.08,2.64)
            box('snack glazing',x-outward*.023,yy,1.54,.06,length/bays-.14,2.42)
        box('wood',x+outward*.13,y,.18,.56,length,.18)
    for j in range(13):
        yy=-21.12+j*.25
        box('cream' if j%2 else 'greenletters',18.35,yy,2.65,.73,.254,.12)
    box('cream',18.28,-14.66,.39,.49,5.36,.67)
    for j in range(8):
        yy=-16.8+j*.62
        for k in range(5):
            a=k*math.tau/5
            pole('shrub',(18.28,yy,.66),(18.28+.17*math.cos(a),yy+.18*math.sin(a),1.10),.075,.032,7)
    for yy in [-12.14,-13.52,-14.90,-16.28,-17.66]:
        pole('silver',(13.12,yy,.16),(13.12,yy,.91),.034,.034)
    for zz in [.51,.89]:pole('silver',(13.12,-12.14,zz),(13.12,-17.66,zz),.032,.032)
    # Southern private lot beyond the coffee shop has a gate and a white low-rise wall.
    box('asphalt',7.47,-28.22,.008,10.46,5.9,.027)
    for yy in [-26.9,-29.5]:box('paint',7.53,yy,.034,7.78,.065,.014)
    box('charcoal',12.77,-25.94,.77,.34,.34,1.54)
    box('cream',12.77,-27.28,1.07,.075,2.69,.095)
    for j in range(5):box('awning',12.77,-26.19-j*.50,1.08,.083,.19,.086)
    collide(12.77,-27.28,.10,2.7,1.13)

    # The pavement view into the coffee corner shows a counter, stools and pendant lamps.
    box('wood',7.85,-12.29,.97,6.92,.52,.14)
    box('cream',7.85,-12.58,.63,6.83,.16,.78)
    for x in [5.17,6.52,7.87,9.22,10.57]:
        pole('charcoal',(x,-12.,.19),(x,-12.,.65),.035,.035)
        pole('wood',(x,-12.,.64),(x,-12.,.71),.19,.19,18)
        pole('charcoal',(x,-12.12,2.76),(x,-12.12,3.17),.012,.012)
        pole('warm diffuser',(x,-12.12,2.68),(x,-12.12,2.77),.105,.075,16)
    for yy in [-13.62,-15.08,-16.54]:
        box('wood',12.16,yy,.87,.79,.68,.095)
        pole('charcoal',(12.16,yy,.2),(12.16,yy,.86),.045,.045)
    for j in range(4):
        box('chalkwall',-9.2+j*1.39,-12.51,1.12,.83,.51,.78)
    # Rear café service windows and doors are visible down the cross-lane.
    for xx in [4.41,7.36,10.13]:
        box('charcoal',xx,-24.59,1.75,1.46,.11,1.13)
        box('tint',xx,-24.66,1.76,1.32,.052,1.0)
    # Street-level food shop, below the wrapping sign. Keep glazing clear of its backing.
    for yy in [13.62,16.25,18.71]:
        box('wood',14.36,yy,.91,.67,1.12,.09)
        pole('charcoal',(14.36,yy,.28),(14.36,yy,.88),.045,.045)
        for dy in [-.39,.39]:box('wood',14.68,yy+dy,.54,.33,.32,.075)
