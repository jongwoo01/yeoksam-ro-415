"""West service passage and rear forecourts visible in street-view frames 56–60."""
import math

def add_west_court(box,pole,mesh,collide):
    # Grey office side and short black canopy looking back towards the main road, frame 58.
    for y in [13.21,16.50,19.79,22.31]:
        for level in range(7):
            z=5.43+3.05*level
            box('silver',-22.19,y,z,.14,1.82,1.54)
            box('tint',-22.28,y,z,.056,1.68,1.41)
            box('silver',-22.325,y,z-.30,.035,1.7,.040)
        box('charcoal',-22.19,y,1.65,.17,2.53,2.58)
        box('glass',-22.30,y,1.68,.05,2.30,2.37)
    box('charcoal',-22.48,18.91,2.93,.89,8.45,.16)
    for y in [13.2+i*.96 for i in range(7)]:
        pole('charcoal',(-22.78,y,.17),(-22.78,y,1.04),.025,.025)
    for z in [.51,.99]:pole('charcoal',(-22.78,13.2,z),(-22.78,18.96,z),.022,.022)
    # Cream facade across passage: parking vestibule recessed behind piers.
    box('chalkwall',-33.52,24.68,1.72,13.00,.21,3.44)
    box('chalkwall',-39.90,17.90,1.72,.18,13.66,3.44)
    box('charcoal',-33.44,11.13,1.67,12.82,.17,3.34)
    for x in [-38.44,-35.61,-32.78,-29.95]:
        box('glass',x,10.998,1.61,2.66,.066,2.69)
    for y in [12.41,14.57,16.73,22.30,24.18]:
        box('charcoal',-26.99,y,1.68,.19,1.96,3.32)
        box('tint',-26.87,y,1.60,.05,1.79,2.94)
        box('chalkwall',-26.81,y-.99,1.74,.31,.22,3.46)
    box('charcoal',-29.2,19.44,1.63,.13,2.98,3.17)
    for y in [17.92,20.94]:box('chalkwall',-28.04,y,1.7,2.51,.22,3.40)
    box('stone',-28.03,19.42,.13,2.55,2.96,.20)
    box('chalkwall',-27.09,19.43,3.09,.54,3.10,.68)
    for y in [12.76,16.63,21.10,24.36]:
        box('stone',-26.84,y,7.40,.39,.48,8.18)
        for j in range(7):
            box('charcoal',-26.77,y+.18+j*.35,4.41,.037,.026,.65)
    for z in [4.13,4.76]:box('charcoal',-26.76,18.54,z,.058,12.43,.063)
    # Photo 57: stone pavers, trench drains, striped lifting arm and rear door.
    box('paver',-15.82,28.29,.032,12.66,8.42,.065)
    for y in [25.12,29.32]:
        box('charcoal',-16.25,y,.081,10.78,.21,.03)
        for j in range(59):box('silver',-21.60+j*.182,y,.106,.020,.22,.018)
    for x in [-19.96,-16.88,-13.8,-10.72]:
        box('ochre',x,28.60,.091,.079,5.01,.028)
    box('charcoal',-21.73,25.60,.68,.30,.35,1.29)
    box('chalkwall',-21.73,25.60,1.24,.34,.37,.27)
    box('cream',-21.70,27.05,1.16,.083,2.93,.12)
    for j in range(5):box('awning',-21.70,25.91+j*.55,1.16,.091,.24,.124)
    collide(-21.70,27.05,.10,2.94,1.23)
    box('charcoal',-11.78,24.22,1.46,2.34,.18,2.75)
    box('tint',-11.78,24.35,1.44,2.18,.052,2.51)
    box('silver',-11.78,24.41,1.49,.047,.042,2.52)
    # Low barrier and covered stalls at the closed end (56 and 60).
    box('chalkwall',-23.03,28.80,.44,.19,8.42,.88)
    collide(-23.03,28.80,.19,8.42,.88)
    box('granite',-29.35,33.08,.52,13.32,.24,1.04)
    collide(-29.35,33.08,13.32,.24,1.04)
    for x in [-37.0,-34.36,-31.72]:
        box('ochre',x,29.54,.025,.071,5.94,.018)
        for y in [27.0,32.12]:pole('charcoal',(x,y,.04),(x,y,2.50),.056,.056)
    # Rolled roof over the parking stalls.
    for j in range(13):
        v0=j/13;v1=(j+1)/13
        def edge(v):return (26.51+6.22*v,2.50+.47*math.sin(math.pi*v))
        y0,z0=edge(v0);y1,z1=edge(v1)
        mesh('graphite',[(-38.1,y0,z0),(-31,y0,z0),(-31,y1,z1),(-38.1,y1,z1)],[(0,1,2,3),(3,2,1,0)])
    # Residential backdrop beyond the planted end wall, 56.
    for x in [-37.0,-33.75,-30.50,-27.25,-24.00,-20.75,-17.50]:
        for level in range(7):
            z=3.4+level*2.74
            box('chalkwall',x,40.97,z,3.24,.38,2.73)
            box('glass',x,40.73,z,2.72,.10,2.25)
            for off in [-.87,0,.87]:box('silver',x+off,40.65,z,.053,.06,2.23)
            box('silver',x,40.54,z-.61,2.73,.10,.047)
            box('stone',x,40.52,z-1.18,2.90,.46,.12)
            if x in [-33.75,-24]:
                box('cream',x+1.0,40.27,z-.71,.62,.43,.46)
    box('chalkwall',-27.20,45.49,11.45,24.00,8.66,22.90)
    collide(-27.20,45.49,24.00,8.66)
    box('stone',-27.20,45.49,22.98,24.29,8.94,.20)
    for x in [-35.1,-30.2,-24.3,-19.4]:
        box('granite',x,35.80,.48,4.85,1.91,.83)
        for i in range(7):
            xx=x-1.92+i*.63
            pole('shrub',(xx,35.8,.83),(xx,35.8,1.27),.49,.40,9)
    for x in [-21.8,-16.8]:pole('charcoal',(x,24.48,.1),(x,24.48,3.61),.055,.046)
    # The court-facing office bay projects past the stone return, with a louvred service entrance.
    for level in range(6):
        z=4.68+3.05*level
        box('granite',-18.5,24.32,z,3.32,.55,2.84)
        box('tint',-18.5,24.63,z,2.97,.09,2.49)
        for x in [-19.25,-17.75]:box('silver',x,24.70,z,.053,.065,2.52)
        box('silver',-18.5,24.70,z-.51,2.99,.056,.052)
        box('stone',-18.5,24.46,z-1.33,3.44,.70,.15)
    box('charcoal',-19.43,24.18,1.53,2.67,.14,2.85)
    box('granite',-19.43,24.48,2.97,2.85,.80,.16)
    box('silver',-19.89,24.285,1.33,1.27,.068,2.47)
    for j in range(10):box('charcoal',-19.89,24.332,.98+j*.084,1.08,.023,.034)
    box('cream',-16.19,24.39,.72,.68,.49,.99)
    for j in range(8):box('silver',-16.19,24.65,.49+j*.070,.57,.026,.025)
    for x in [-15.27,-14.94]:
        pole('silver',(x,24.16,.25),(x,24.16,9.7),.051,.051,10)
    box('granite',-14.49,24.21,.26,1.24,.62,.32)
    pole('charcoal',(-21.68,25.05,.08),(-21.68,25.05,3.19),.056,.042)
    pole('charcoal',(-21.68,25.05,3.19),(-21.45,25.05,3.32),.045,.045)
    box('cream',-21.30,25.05,3.28,.34,.19,.095)
    # Low yellow lane markers and narrow balcony stacks show in frame 56.
    for y in [24.9,27.1,29.3]:
        pole('ochre',(-24.77,y,.06),(-24.77,y,.12),.14,.105,16)
    for x in [-35.38,-29.05,-22.64]:
        for level in range(7):
            z=2.38+level*2.74
            box('chalkwall',x,40.25,z-.09,1.03,.84,.22)
            for dx in [-.47,0,.47]:pole('silver',(x+dx,39.87,z),(x+dx,39.87,z+.78),.022,.022,6)
            for h in [.30,.75]:box('silver',x,39.87,z+h,1.02,.045,.039)
