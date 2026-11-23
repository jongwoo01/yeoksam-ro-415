"""Parked vehicles. Distances are metres in local longitudinal/lateral axes."""
import math
from bisect import bisect_right


def add_cars(material, mesh, collide):
    for name, color, roughness, metal in [
        ('pearl', (.72,.75,.76), .24,.46), ('graphite', (.10,.13,.15), .23,.61),
        ('rubber', (.022,.024,.026), .84,0), ('alloy', (.55,.60,.62), .27,.8),
        ('windscreen', (.060,.104,.125), .14,.48), ('window trim', (.017,.021,.024), .34,.16),
        ('seat fabric', (.040,.046,.047), .86,0), ('tail light', (.52,.018,.016), .22,.24), ('headlight', (.80,.86,.86), .17,.52)
    ]:
        material(name,color,roughness,metal)

    def profile(table, x):
        """Cubic Hermite interpolation through measured-design section landmarks."""
        i=max(0,min(len(table)-2,bisect_right(table,(x,math.inf))-1))
        x0,a=table[i]; x1,b=table[i+1]
        t=max(0,min(1,(x-x0)/(x1-x0)))
        xl,l=table[max(0,i-1)]; xr,r=table[min(len(table)-1,i+2)]
        m=(b-l)/(x1-xl)*(x1-x0); n=(r-a)/(xr-x0)*(x1-x0)
        return a+(b-a)*t*t*(3-2*t)+m*t*(1-t)**2-n*t*t*(1-t)

    def car(cx,cy,angle,paint,suv=False):
        co,si=math.cos(angle),math.sin(angle)
        def part(mat,pts,faces):
            vertices=[]
            for x,y,z in pts:
                # Bumper corners sweep toward the wheels. Apply the same contour
                # to every lens, intake and seam mounted on the bumper.
                blend=max(0,min(1,(abs(x)-1.81)/.54))
                x-=math.copysign(blend*blend*(.27*abs(y)**2+.11*max(0,.48-z)),x)
                vertices.append((cx+x*co-y*si,cy+x*si+y*co,z))
            mesh(mat,vertices,faces)

        def surface(mat,rows,flip=False):
            cols=len(rows[0])
            faces=[]
            for row in range(len(rows)-1):
                for col in range(cols-1):
                    a=row*cols+col
                    face=(a,a+cols,a+cols+1,a+1)
                    faces.append(face[::-1] if flip else face)
            part(mat,[p for row in rows for p in row],faces)

        width=[(-2.355,.67),(-2.22,.83),(-1.65,.89),(-1.1,.91),(0,.904),(1.40,.91),(2.04,.86),(2.355,.69)]
        shoulder=[(-2.355,.76),(-2.12,.89),(-1.48,.948),(-.7,.962),(.45,.921),(1.32,.86),(1.98,.78),(2.355,.66)]
        if suv:
            roof=[(-1.94,.94),(-1.60,1.40),(-1.27,1.54),(-.65,1.59),(.25,1.58),(.66,1.46),(1.27,.91)]
        else:
            roof=[(-1.67,.96),(-1.20,1.17),(-.72,1.37),(-.31,1.435),(.17,1.437),(.49,1.39),(.83,1.20),(1.20,.926)]
        def arch(x):
            dx=min(abs(x-axle) for axle in (-1.36,1.36))
            if dx>.387:return .245
            return .325+math.sqrt(max(0,.387**2-dx**2))
        xs=sorted(set([round(-2.355+i*4.71/82,6) for i in range(83)]+
                      [round(ax+.387*math.cos(i*math.pi/24),6) for ax in (-1.36,1.36) for i in range(25)]))
        def sidepoint(x,f,side):
            low=arch(x); high=profile(shoulder,x)
            breadth=profile(width,x)*(.968+.034*math.sin(f*math.pi)-.028*f**4)
            return (x,side*breadth,low+(high-low)*f)

        for side in (-1,1):
            surface(paint,[[sidepoint(x,f,side) for f in (0,.12,.34,.65,.88,1)] for x in xs],side==1)
            for ax in (-1.36,1.36):
                rows=[]
                for i in range(33):
                    a=math.pi*i/32; x=ax+.387*math.cos(a); z=.325+.387*math.sin(a)
                    y=abs(sidepoint(x,0,side)[1])
                    rows.append([(x,side*(y-.11),z),(x,side*y,z),(x+.024*math.cos(a),side*(y+.004),z+.024*math.sin(a))])
                surface('rubber' if suv else paint,rows,side<0)
            # Recess lines and handles follow the presswork instead of floating in a plane.
            for seam in (-.96,-.16,.94):
                rows=[]
                for i in range(13):
                    f=.13+.84*i/12; x=seam+.07*(1-f)
                    if arch(x)>.30:continue
                    rows.append([(a,b+side*.004,c) for a,b,c in (sidepoint(x,f,side),sidepoint(x+.012,f,side))])
                if len(rows)>1:surface('window trim',rows,side<0)
            for x in (-.82,.05):
                rows=[]
                for dx in (-.077,-.060,.058,.077):
                    a,b,c=sidepoint(x+dx,.83,side);h=.010 if abs(dx)>.07 else .019
                    rows.append([(a,b+side*.012,c-h),(a,b+side*.025,c),(a,b+side*.012,c+h)])
                surface(paint,rows,side==1)

        def deck(x,t):
            w=profile(width,x)*.94
            return (x,w*t,profile(shoulder,x)+.057*(1-t*t))
        for lo,hi,mat in [(-2.355,roof[0][0],paint),(roof[0][0],roof[-1][0],'seat fabric'),(roof[-1][0],2.355,paint)]:
            segment=[lo]+[x for x in xs if lo<x<hi]+[hi]
            surface(mat,[[deck(x,t) for t in (-1,-.84,-.44,0,.44,.84,1)] for x in segment])
        for side in (-1,1):
            rows=[]
            for i in range(20):
                q=i/19;x=roof[-1][0]+.02+(2.25-roof[-1][0])*q
                t=side*(.78-.12*q)
                rows.append([(xx,yy,zz+.003) for xx,yy,zz in (deck(x,t-.004),deck(x,t+.004))])
            surface('window trim',rows)
        def cushion(x,y,z,length,width,height):
            rows=[]
            for h,scale in [(-1,.68),(-.72,.96),(.58,1),(.90,.84),(1,.03)]:
                ring=[]
                for k in range(21):
                    a=k*math.tau/20
                    def rounded(v):return math.copysign(abs(v)**.60,v)
                    ring.append((x+length*scale*rounded(math.cos(a))-.045*h,
                                 y+width*scale*rounded(math.sin(a)),z+height*h))
                rows.append(ring)
            surface('seat fabric',rows,True)
        for x in [-.82,.09]:
            for y in [-.375,.375]:
                cushion(x,y,.978,.115,.226,.218)
                cushion(x-.067,y,1.235,.078,.131,.085)
        surface('window trim',[[(x,-.72,h),(x,-.42,h+.025),(x,.42,h+.025),(x,.72,h)]
                               for x,h in [(.56,.963),(.67,1.045),(.92,.99),(1.12,.954)]])

        for sign in (-1,1):
            x=sign*2.355;w=profile(width,x);h=profile(shoulder,x)
            surface(paint,[[(x-sign*back,w*t,z*(1-.06*t*t)) for t in (-1,-.86,-.45,0,.45,.86,1)]
                           for z,back in [(.25,.11),(.34,.01),(.56,0),(h+.048,.005)]],sign>0)

        # One continuous greenhouse with a sloping windshield, roof rails and separate panes.
        begin,end=roof[0][0],roof[-1][0]
        def glasspoint(x,t):
            top=profile(roof,x);base=profile(shoulder,x)+.035
            rise=max(.014,top-base);half=.828-.145*min(1,rise/.48)
            if abs(t)<=.76:
                return (x,t/.76*half,top-.027*(t/.76)**2)
            f=(abs(t)-.76)/.24
            return (x,math.copysign(half+(.854-half)*f,t),top-.027-(rise-.027)*f)
        roof_start=-1.30 if suv else -.58
        roof_end=.55 if suv else .40
        cuts=sorted(set([begin+(end-begin)*i/42 for i in range(43)]+[roof_start,roof_end,-.26,-.16]))
        strips=[-1,-.98,-.83,-.76,-.68,-.36,0,.36,.68,.76,.83,.98,1]
        panels={}
        for i,(lo,hi) in enumerate(zip(cuts,cuts[1:])):
            x=(lo+hi)/2
            for j,(a,b) in enumerate(zip(strips,strips[1:])):
                t=abs((a+b)/2)
                mat='windscreen'
                if (t<.76 and roof_start<=x<=roof_end) or .76<t<.83:mat=paint
                if t>.98 or (t>.83 and -.26<x<-.16):mat='window trim'
                points,faces,indices=panels.setdefault(mat,([],[],{}))
                face=[]
                for key in ((i,j),(i+1,j),(i+1,j+1),(i,j+1)):
                    if key not in indices:
                        indices[key]=len(points)
                        points.append(glasspoint(cuts[key[0]],strips[key[1]]))
                    face.append(indices[key])
                faces.append(face)
        for mat,(points,faces,_) in panels.items():part(mat,points,faces)
        # Cast a continuous underbody shadow and darken the inside of each wheel well.
        surface('rubber', [[(x,-.70,.24),(x,.70,.24)] for x in (-2.22,2.22)],True)
        for side in (-1,1):
            for ax in (-1.36,1.36):
                rows=[]
                for i in range(29):
                    a=math.pi*i/28
                    x=ax+.38*math.cos(a);z=.325+.38*math.sin(a)
                    rows.append([(x,side*.698,z),(x,side*.85,z)])
                surface('rubber',rows,side<0)
        # Rounded mirror housings, each with a dark underside.
        for side in (-1,1):
            rows=[]
            for x,w,h in ((.52,.015,.016),(.55,.084,.057),(.64,.103,.068),(.735,.080,.051),(.76,.018,.014)):
                rows.append([(x,side*(.89+w*math.cos(i*math.tau/16)),1.012+h*math.sin(i*math.tau/16)) for i in range(17)])
            surface(paint,rows,side>0)
            surface('window trim', [[(.65,side*y,.962),(.70,side*y,.978)] for y in (.80,.91)],side<0)
        for ax in (-1.36,1.36):
            for side in (-1,1):
                def wheelring(radius,depth):
                    return [(ax+radius*math.cos(i*math.tau/36),side*depth,.328+radius*math.sin(i*math.tau/36)) for i in range(37)]
                surface('rubber',[wheelring(rad,y) for rad,y in ((.216,.864),(.256,.869),(.305,.863),(.328,.84),(.328,.704),(.308,.682),(.212,.679))],side>0)
                surface('alloy',[wheelring(.225,.869),wheelring(.201,.873),wheelring(.19,.84)],side<0)
                surface('graphite',[wheelring(.202,.832),wheelring(.012,.832)],side<0)
                for k in range(5):
                    for split in (-1,1):
                        a=k*math.tau/5
                        outline=[(.04,-.26),(.12,split*.12-.12),(.212,split*.27-.055),(.212,split*.27+.07),(.105,split*.12+.12),(.04,.26)]
                        pts=[(ax+r*math.cos(a+t),side*.875,.328+r*math.sin(a+t)) for r,t in outline]
                        part('alloy',pts,[tuple(range(len(pts))),tuple(reversed(range(len(pts))))])
                surface('alloy',[wheelring(.052,.879),wheelring(.001,.879)],side<0)
        # Contrasting lenses and grille on the bumper skin, with no identifying plate.
        for front in (-1,1):
            h=profile(shoulder,front*2.355)
            def band(mat,z,w,thickness):
                rows=[]
                for i in range(21):
                    t=(i-10)/10
                    x=front*(2.359-.003*t*t)
                    rows.append([(x,w*t,z-.019*t*t),(x,w*t,z-.019*t*t+thickness)])
                surface(mat,rows,front<0)
            if front>0:
                # Install lenses in dark housings and set a stepped intake below.
                def fascia(mat,contour,depth):
                    edges=list(zip(contour,contour[1:]+contour[:1]))
                    ys=sorted(y for y,z in contour)
                    samples=sorted(set(ys+[ys[0]+(ys[-1]-ys[0])*i/24 for i in range(1,24)]))
                    rows=[]
                    for y in samples:
                        heights=[z for yy,z in contour if yy==y]
                        for (ya,za),(yb,zb) in edges:
                            if min(ya,yb)<y<max(ya,yb):
                                heights.append(za+(zb-za)*(y-ya)/(yb-ya))
                        rows.append([(2.355+depth,y,min(heights)),(2.355+depth,y,max(heights))])
                    surface(mat,rows)
                fascia('window trim',[(-.64,.535),(-.47,.564),(.47,.564),(.64,.535),(.46,.323),(-.46,.323)],.013)
                for n in range(3):
                    z=.361+n*.057;w=.47+.048*n
                    fascia('graphite',[(-w,z),(w,z),(w+.008,z+.012),(-w-.008,z+.012)],.019)
                for side in (-1,1):
                    def pod(mat,points,d):
                        fascia(mat,[(side*y,z) for y,z in points],d)
                    pod('window trim',[(.11,.634),(.46,.651),(.68,.634),(.66,.548),(.39,.565),(.15,.597)],.019)
                    pod('headlight',[(.15,.625),(.46,.640),(.668,.624),(.655,.607),(.45,.625),(.17,.610)],.024)
                    for y in [.48,.565]:
                        pod('alloy',[(y,.577),(y+.058,.579),(y+.057,.598),(y,.596)],.025)
                fascia('window trim',[(-.13,.625),(.13,.625),(.14,.614),(-.14,.614)],.017)
                fascia('cream',[(-.21,.397),(.21,.397),(.21,.479),(-.21,.479)],.032)
            else:
                band('window trim',h-.12,.66,.075)
                band('tail light',h-.082,.66,.032)
                band('cream',.416,.234,.095)
            for side in (-1,1):
                rows=[]
                for d in [0,.06,.15,.25,.33]:
                    x=front*(2.355-d);y=profile(width,x)*.982;z=profile(shoulder,x)-.067
                    rows.append([(x,side*(y+.004),z-.045*(1-d/.36)),(x,side*(y+.009),z+.012)])
                surface('headlight' if front>0 else 'tail light',rows,front*side<0)
        # Three nested supports match the bonnet, glass and cabin above the wheels.
        def support(start, end, breadth, height):
            mid = (start+end)/2
            length = end-start
            collide(cx+mid*co,cy+mid*si,abs(co)*length+abs(si)*breadth,
                    abs(si)*length+abs(co)*breadth,height)
        support(-2.34,2.34,1.80,.84)
        support(roof[0][0]+.15,roof[-1][0]-.16,1.54,1.14)
        support(roof[1][0]+.15,roof[-2][0]-.06,1.29,max(h for _,h in roof))

    car(29,5.15,math.pi,'pearl')
    car(-22,-5.25,0,'graphite')
    car(6.25,26.76,math.pi/2,'pearl',True)
    car(3.72,26.76,math.pi/2,'graphite')
    car(1.18,26.76,math.pi/2,'pearl')

    # Tiled building rear court, frame 39.
    car(22.01,27.36,math.pi,'pearl')
    car(22.32,30.03,math.pi,'graphite')
