"""Generate original tiling finishes and an alpha-cutout spray of plane-tree leaves."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import math,random
rng=random.Random(415)
dst=Path(__file__).parent/'finishes'
dst.mkdir(exist_ok=True)
img=Image.new('RGBA',(256,256));d=ImageDraw.Draw(img)
def leaf(x,y,angle,length):
    u=(math.cos(angle),math.sin(angle));v=(-u[1],u[0])
    def pt(a,b):
        return (x+length*(a*u[0]+b*v[0]),y+length*(a*u[1]+b*v[1]))
    shade=rng.uniform(.65,1.28)
    poly=[pt(a,b) for a,b in [(0,0),(.12,.24),(.36,.23),(.46,.52),(.62,.30),(.84,.30),(.76,.13),(1,0),(.72,-.15),(.82,-.35),(.52,-.28),(.38,-.48),(.26,-.22),(.09,-.16)]]
    d.polygon(poly,fill=(int(75*shade),int(102*shade),int(46*shade),255))
    d.line([pt(.07,0),pt(.87,0)],fill=(107,126,76,255),width=1)
    for a in [.32,.57]:d.line([pt(a,0),pt(a+.15,.20)],fill=(95,116,63,255),width=1)
for i in range(10):
    x0,y0=123,239;x1=rng.uniform(30,224);y1=rng.uniform(28,170)
    d.line((x0,y0,x1,y1),fill=(71,64,40,255),width=2)
    a=math.atan2(y1-y0,x1-x0)
    for k in range(1,8):
        t=k/8;x=x0+(x1-x0)*t;y=y0+(y1-y0)*t
        leaf(x,y,a+(1 if k%2 else -1)*rng.uniform(.62,1.22),rng.uniform(22,49))
img.save(dst/'leaf-spray.png')
for name in ['tile','granite','bark','sidewalk','violet']:
    n=384;im=Image.new('RGB',(n,n));d=ImageDraw.Draw(im)
    if name=='violet':
        for x in range(n):
            t=x/(n-1);d.line((x,0,x,n),fill=(int(137-78*t),int(46+18*t),int(97+58*t)))
    elif name=='bark':
        im.paste((158,153,130),(0,0,n,n))
        for _ in range(430):
            x=rng.randrange(n);y=rng.randrange(n);r=rng.uniform(3,36);c=rng.choice([(126,127,107),(185,180,155),(137,137,112),(173,167,147)])
            pts=[(x+math.cos(k)*r*rng.uniform(.45,1),y+math.sin(k)*r*1.6*rng.uniform(.45,1)) for k in range(7)]
            for dx in [-n,0,n]:
                for dy in [-n,0,n]:d.polygon([(a+dx,b+dy) for a,b in pts],fill=c)
    else:
        im.paste((134,131,123),(0,0,n,n))
        w,h={'tile':(24,36),'granite':(96,128),'sidewalk':(64,96)}[name]
        for y in range(-h,n,h):
            for x in range(-w,n,w):
                bx=x+((y//h)%2)*w//2 if name=='sidewalk' else x
                c=rng.randint(155,185) if name!='tile' else rng.randint(173,192)
                if name=='sidewalk' and rng.random()<.085:c-=60
                d.rectangle((bx+1,y+1,bx+w-1,y+h-1),fill=(c+5,c+3,c-3))
        pix=im.load()
        for y in range(n):
            for x in range(n):
                variance=rng.gauss(0,8 if name=='granite' else 3)
                pix[x,y]=tuple(max(0,min(255,int(v+variance))) for v in pix[x,y])
    if name=='sidewalk':
        from PIL import ImageOps, ImageChops
        photo=Image.open(dst.parents[1]/'public/materials/brushed_concrete_03_diff.jpg').convert('L').resize((n,n))
        detail=ImageOps.colorize(ImageOps.autocontrast(photo),'#898379','#ffffff')
        im=Image.blend(im,ImageChops.multiply(im,detail),.83)
    im.save(dst/(name+'.jpg'),quality=90)

# Preserve the grain of the scanned concrete while matching the lighter street facades.
concrete = Image.open(dst.parents[1] / 'public/materials/brushed_concrete_03_diff.jpg').convert('L')
for name, channels in [
    ('stone', [(1.10, 42), (1.10, 41), (1.06, 40)]),
    ('plaster', [(.82, 107), (.82, 104), (.82, 97)]),
]:
    tinted = [concrete.point([round(value * scale + offset) for value in range(256)])
              for scale, offset in channels]
    Image.merge('RGB', tinted).save(dst / (name + '-neutral.jpg'), quality=91)
