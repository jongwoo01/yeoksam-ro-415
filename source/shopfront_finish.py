"""Street-level details visible from the pavement; combine geometry by material."""
import math,random
def add_street_details(material,box,pole,mesh,collide):
    rng=random.Random(322)
    # Parked small-wheeled bicycle next to the purple shop front.
    cx,cy=-13.3,10.02
    def p(x,y,z):return (cx+x,cy+y,z)
    def rod(a,b,r,mat):pole(mat,p(*a),p(*b),r,r,10)
    for x in [-.54,.54]:
        for j in range(32):
            a=j*math.tau/32;b=(j+1)*math.tau/32
            rod((x+.266*math.cos(a),0,.434+.266*math.sin(a)),(x+.266*math.cos(b),0,.434+.266*math.sin(b)),.037,'rubber')
            rod((x+.235*math.cos(a),0,.434+.235*math.sin(a)),(x+.235*math.cos(b),0,.434+.235*math.sin(b)),.011,'alloy')
            if j%2==0:rod((x,.018,.434),(x+.234*math.cos(a),0,.434+.234*math.sin(a)),.004,'silver')
    for a,b in [((-.54,0,.43),(-.13,0,.86)),((-.54,0,.43),(-.08,0,.45)),((-.08,0,.45),(-.13,0,.86)),((-.13,0,.82),(.34,0,.87)),((-.08,0,.45),(.34,0,.87)),((.54,0,.43),(.34,0,.93)),((.34,0,.93),(.30,0,1.13))]:
        rod(a,b,.029,'graphite')
    rod((.30,-.19,1.13),(.30,.19,1.13),.021,'rubber')
    box('rubber',cx-.15,cy,.926,.25,.16,.065);collide(cx,cy,1.68,.43)
    # Recessed seams, irregular stone faces and overhanging coping.
    for x0,x1 in [(-8.88,-1.40),(2.00,9.11)]:
        n=round((x1-x0)/.68)
        for i in range(n):
            x=x0+(i+.5)*(x1-x0)/n;w=(x1-x0)/n-.018;front=9.754
            y=front-rng.uniform(.018,.063)
            pts=[(x-w/2,front,.20),(x+w/2,front,.20),(x+w/2,front,.785),(x-w/2,front,.785),
                 (x-w*.39,y,.28),(x+w*.39,y-.022,.29),(x+w*.4,y,.71),(x-w*.40,y-.015,.70),(x+w*rng.uniform(-.15,.18),y-.032,.5)]
            mesh('granite',pts,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,8),(5,6,8),(6,7,8),(7,4,8)])
        box('chalkwall',(x0+x1)*.5,9.772,.821,x1-x0,.145,.061)
    # Frame and mullion details on the papered shop. Keep its observed vacancy sign.
    for x in [-19.06,-17.11,-15.16,-13.20]:
        box('silver',x,10.644,1.48,.047,.074,2.06)
    for z in [.478,2.49]:box('charcoal',-16.10,10.63,z,5.92,.10,.052)
    for x in [-19.49,-16.4,-13.03]:
        pole('silver',(x,10.67,3.66),(x,10.31,3.76),.016,.016)
        box('charcoal',x,10.30,3.73,.14,.11,.07)
    # Catenary profile of the overhead street cables, along the model's public frontage.
    for lane in range(3):
        for span in range(-2,3):
            start=span*25-9;end=start+25
            for i in range(12):
                def cable(t):
                    return (start+(end-start)*t,7.04+lane*.12,6.62+lane*.09-.46*4*t*(1-t))
                pole('rubber',cable(i/12),cable((i+1)/12),.014,.014,5)
