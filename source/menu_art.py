"""Illustrative artwork for the observed retail sign frames."""
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from pathlib import Path
import math,random
dst=Path(__file__).parent/'finishes'
def font(size):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',size)
im=Image.new('RGB',(400,900));d=ImageDraw.Draw(im)
for y in range(900):
    t=y/899;d.line((0,y,400,y),fill=(int(39+73*t),int(64+79*t),int(130+67*t)))
d.text((200,68),'EDIYA COFFEE',font=font(20),fill='#f6f4ef',anchor='mt')
# Generic label deliberately avoids inventing a product or a price.
d.multiline_text((200,209),'ICED\nDRINKS',font=font(69),fill='#fff9ed',anchor='mm',align='center',spacing=-9)
cups=Image.open(dst/'drinks.png').convert('RGBA');cups.thumbnail((395,415))
im.paste(cups,((400-cups.width)//2,370),cups)
d.line((42,772,358,772),fill='#e5d6ca',width=2)
im.save(dst/'drink-board.jpg',quality=91)
rng=random.Random(67);im=Image.new('RGB',(190,960),'#e1c5d2');d=ImageDraw.Draw(im)
for i in range(4):
    cy=123+i*232;d.ellipse((16,cy-89,174,cy+69),fill='#88827d');d.ellipse((19,cy-92,171,cy+63),fill='#ede5d5')
    if i%2==0:
        for x,y in [(65,cy-24),(111,cy-25),(87,cy+13)]:
            d.ellipse((x-24,y-22,x+25,y+23),fill='#34392e');d.ellipse((x-20,y-18,x+20,y+18),fill='#e7d9bb')
            for col in ['#d0933a','#8d5c45','#708653']:
                u=x+rng.randrange(-11,12);v=y+rng.randrange(-8,8);d.rectangle((u,v,u+7,v+6),fill=col)
    else:
        d.ellipse((41,cy-65,151,cy+34),fill='#ad5833')
        for j in range(14):
            x=rng.randint(59,125);y=rng.randint(cy-46,cy+10);d.rounded_rectangle((x,y,x+15,y+7),4,fill=rng.choice(['#d77f44','#e69d60','#c36d40']))
    d.line((44,cy+88,145,cy+88),fill='#80596b',width=2)
im.save(dst/'food-strip.jpg',quality=90)
