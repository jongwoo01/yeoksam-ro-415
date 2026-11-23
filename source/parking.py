"""Visible rear elevation and forecourt, interpreted from public street view 34."""
import random
def add_parking(material,box,mesh):
    rng=random.Random(34)
    palette=[(.32,.32,.30),(.36,.355,.33),(.30,.30,.29),(.345,.33,.30)]
    for i,shade in enumerate(palette):material('court slab '+str(i),shade,.89)
    # Flush running-bond pavers. Their texture varies by stone rather than by row.
    box('mortar',-.3,28.03,-.016,19.62,8.04,.05)
    for j in range(25):
        x=-10.11
        while x<9.50:
            width=min(.40 if j%2 and x==-10.11 else .80,9.51-x)
            if width<.012:break
            box('court slab '+str(rng.randrange(4)),x+width/2,24.02+(j+.5)*.32,.012,width-.009,.312,.012)
            x+=width
    for i in range(7):
        x=7.52-i*2.54
        box('paint',x,26.73,.024,.072,4.92,.012)
    box('paint',-.10,29.16,.024,15.32,.074,.012)
    # Thin joints in the stone cladding and dark-framed horizontal openings.
    for row in range(16):
        for col in range(14):
            width=18/14
            box('chalkwall',-9+(col+.5)*width,24.033,.65+row*1.20,width-.016,.09,1.184)
    for j in range(5):
        for x in [-6.2,-.9,5.6]:
            z=3.46+j*3.14
            box('charcoal',x,24.101,z,2.45,.10,1.02)
            box('tint',x,24.163,z,2.32,.034,.88)
            box('silver',x,24.19,z,.045,.035,.91)
    box('granite',.1,24.27,.29,16.7,.49,.54)
    for i in range(660):
        x=rng.uniform(-8.16,8.36);y=rng.uniform(24.12,24.46);z=rng.uniform(.56,.91);w=rng.uniform(.08,.16)
        mesh('canopy',[(x-w,y,z-.09),(x+w,y,z-.09),(x+w,y+.06,z+.10),(x-w,y+.06,z+.10)],[(0,1,2,3)])
    # Only the mass visible across the parking court is modelled.
    box('chalkwall',-7.55,31.25,1.35,3.60,1.65,2.70)
    box('stone',-7.55,31.23,2.70,3.74,1.79,.13)

    # The building opposite the rear wall carries ivy across its pale facade.
    # Keep the uneven climbing outline and exposed upper windows seen in frame 34.
    box('stone',.30,34.00,7.25,20.20,3.9,14.5)
    for level in range(4):
        for i in range(7):
            x=-8.17+2.68*i;z=3.04+level*3.18
            box('charcoal',x,32.025,z,1.83,.10,1.26)
            box('tint',x,31.958,z,1.68,.035,1.10)
            box('silver',x,31.926,z-.29,1.71,.04,.046)
    import math
    for _ in range(3100):
        x=rng.uniform(-9.71,10.28)
        base=2.18+.21*math.sin(x*1.66)
        crest=base+1.05+9*math.exp(-((x+6.1)/4.0)**2)+.55*math.sin(2.76*x)
        z=rng.uniform(base-.22,crest+.18)
        y=31.84+rng.uniform(-.085,.04);r=rng.uniform(.10,.25)
        mesh('canopy',[(x-r,y,z-r),(x+r,y-.018,z-r),(x+r,y+.04,z+r),(x-r,y+.038,z+r)],[(0,1,2,3)])

    # Long drainage channel across the entrance and alternating rough stone inserts (41, 43).
    box('charcoal',9.33,28.68,.070,.26,7.14,.040)
    for j in range(84):box('silver',9.33,25.16+j*.083,.101,.24,.012,.012)
    for row,col in [(3,1),(4,7),(6,4),(8,10),(9,2)]:
        box('granite',-9+(col+.5)*18/14,24.105,.65+row*1.20,.64,.07,.49)
    for k in range(3):
        x=-7.9+k*2.1;box('granite',x,30.97,.19,.69,.49,.37)
