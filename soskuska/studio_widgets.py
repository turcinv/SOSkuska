"""Native study-studio visuals. Drawing/layout only; no database or network access."""
import calendar
import math
from datetime import date
from PIL import Image, ImageDraw
import customtkinter as ctk
from theme import COLORS as C
from localization import tr

MONTHS = ('January','February','March','April','May','June','July','August',
          'September','October','November','December')


def nav_icon(name, active=False):
    """Small line icons drawn locally, with no external assets or Tk globals."""
    image=Image.new('RGBA',(72,72))
    draw=ImageDraw.Draw(image)
    color=C['nav_accent'][0] if active else C['nav_secondary'][0]
    def line(points):draw.line([(x*3,y*3) for x,y in points],fill=color,width=4,joint='curve')
    def box(rect,radius=2):draw.rounded_rectangle(tuple(n*3 for n in rect),radius=radius*3,outline=color,width=4)
    if name=='Dashboard':
        for rect in [(4,4,10,10),(14,4,20,10),(4,14,10,20),(14,14,20,20)]:box(rect,1)
    elif name=='My Subjects':
        box((4,4,9,20),1);box((11,4,16,20),1);line([(18,5),(21,19)])
    elif name=='Flashcards':
        box((7,4,21,17));line([(4,8),(4,20),(17,20)])
    elif name=='Practice Tests':
        box((5,3,19,21));line([(8,9),(10,11),(15,6)]);line([(8,16),(15,16)])
    elif name=='AI Tutor':
        line([(12,2),(14,9),(21,12),(14,15),(12,22),(10,15),(3,12),(10,9),(12,2)])
    elif name=='Statistics':
        line([(4,20),(4,13)]);line([(12,20),(12,5)]);line([(20,20),(20,9)])
    else:
        draw.ellipse((23,23,49,49),outline=color,width=4)
        for angle in range(0,360,45):
            a=math.radians(angle)
            line([(12+6*math.cos(a),12+6*math.sin(a)),(12+9*math.cos(a),12+9*math.sin(a))])
    return ctk.CTkImage(light_image=image,dark_image=image,size=(22,22))


def _rgb(value):
    value=value.lstrip('#')
    return tuple(int(value[i:i+2],16) for i in (0,2,4))


def _mix(first,second,t):
    a,b=_rgb(first),_rgb(second)
    return tuple(round(a[i]+(b[i]-a[i])*t) for i in range(3))


def _paw(draw,cx,cy,r,fill):
    """One paw print centred on its main pad; r is the pad radius."""
    draw.ellipse((cx-r,cy-r*.8,cx+r,cy+r*.8),fill=fill)
    for dx,dy in ((-1.05,-1.25),(-.38,-1.75),(.38,-1.75),(1.05,-1.25)):
        tr_=r*.42
        draw.ellipse((cx+dx*r-tr_,cy+dy*r-tr_*1.15,cx+dx*r+tr_,cy+dy*r+tr_*1.15),fill=fill)


def paw_icon(size=22,role='accent'):
    """Small paw mark used beside the greeting; paired with the theme role."""
    variants=[]
    for mode in (0,1):
        image=Image.new('RGBA',(size*4,size*4))
        _paw(ImageDraw.Draw(image),size*2,size*2.55,size*.95,C[role][mode])
        variants.append(image)
    return ctk.CTkImage(light_image=variants[0],dark_image=variants[1],size=(size,size))


def stat_icon(kind):
    """Rounded tile with a line icon for summary tiles (40 x 40 logical px)."""
    variants=[]
    for mode in (0,1):
        s=3
        image=Image.new('RGBA',(40*s,40*s))
        draw=ImageDraw.Draw(image)
        draw.rounded_rectangle((0,0,40*s-1,40*s-1),radius=12*s,fill=C['selected'][mode])
        ink=C['accent'][mode];w=int(2.4*s)
        def p(x,y):return (x*s,y*s)
        if kind=='time':
            draw.ellipse((*p(10,10),*p(30,30)),outline=ink,width=w)
            draw.line([p(20,14),p(20,20),p(25,23)],fill=ink,width=w,joint='curve')
        elif kind=='sessions':
            draw.ellipse((*p(10,10),*p(30,30)),fill=ink)
            draw.line([p(15,20.5),p(18.6,24),p(25.5,16.5)],fill=C['selected'][mode],width=int(2.8*s),joint='curve')
        elif kind=='streak':
            flame=[p(20,9),p(25,15),p(28,21),p(27,26),p(23.5,30.5),p(16.5,30.5),p(13,26),p(12.5,21),p(15,17),p(17,20),p(18,15)]
            draw.polygon(flame,outline=ink,width=w)
            draw.ellipse((*p(17.2,23),*p(22.8,29.5)),fill=ink)
        else:
            draw.line([p(20,13),p(20,28)],fill=ink,width=w)
            draw.line([p(9,12),p(15,11),p(20,13),p(25,11),p(31,12),p(31,27),p(25,26),p(20,28),p(15,26),p(9,27),p(9,12)],fill=ink,width=w,joint='curve')
        variants.append(image)
    return ctk.CTkImage(light_image=variants[0],dark_image=variants[1],size=(40,40))


def cat_avatar(size=46):
    """Circular mascot avatar for the local profile; no personal data."""
    s=4;n=size*s
    image=Image.new('RGBA',(n,n))
    draw=ImageDraw.Draw(image)
    draw.ellipse((0,0,n-1,n-1),fill='#C9B6F2')
    ink='#2B2A34'
    def p(x,y):return (x*n,y*n)
    draw.polygon([p(.25,.48),p(.30,.20),p(.45,.36)],fill=ink)
    draw.polygon([p(.75,.48),p(.70,.20),p(.55,.36)],fill=ink)
    draw.ellipse((*p(.22,.30),*p(.78,.80)),fill=ink)
    draw.rectangle((*p(.30,.72),*p(.70,1.0)),fill=ink)
    mask=Image.new('L',(n,n));ImageDraw.Draw(mask).ellipse((0,0,n-1,n-1),fill=255)
    for cx in (.39,.61):
        draw.arc((*p(cx-.07,.47),*p(cx+.07,.59)),start=200,end=340,fill='#F6F3FA',width=max(2,n//36))
    clipped=Image.new('RGBA',(n,n));clipped.paste(image,(0,0),mask)
    return ctk.CTkImage(light_image=clipped,dark_image=clipped,size=(size,size))


SCENE_SIZE=(360,150)


def study_scene(fade):
    """Night-window scene with a sitting cat, fading on the left into ``fade``.

    ``fade`` is a paired (Light, Dark) theme role so the image blends into the
    focus panel in both appearances.
    """
    width,height=SCENE_SIZE;s=3
    W,H=width*s,height*s
    variants=[]
    palettes=(('#9B88DA','#C4B3F0','#7462BE','#E9E1F8','#2E2547'),
              ('#2F2944','#5A4A86','#4C4170','#C9B6F2','#15131D'))
    for mode in (0,1):
        top,bottom,deep,glow,ink=palettes[mode]
        sky=Image.new('RGB',(W,H))
        sky_draw=ImageDraw.Draw(sky)
        for y in range(H):
            sky_draw.line([(0,y),(W,y)],fill=_mix(top,bottom,y/H))
        image=sky.convert('RGBA')
        draw=ImageDraw.Draw(image)
        def p(x,y):return (x*s,y*s)
        # Window with mullions, moon, stars and a skyline.
        draw.rounded_rectangle((*p(150,16),*p(318,118)),radius=8*s,fill=deep,outline=glow,width=2*s)
        draw.line([p(234,16),p(234,118)],fill=glow,width=2*s)
        draw.line([p(150,64),p(318,64)],fill=glow,width=2*s)
        draw.ellipse((*p(276,26),*p(298,48)),fill=glow)
        draw.ellipse((*p(283,22),*p(303,44)),fill=deep)
        for x,y in ((170,30),(200,44),(252,28),(214,24),(300,82),(262,52)):
            draw.ellipse((*p(x-1.2,y-1.2),*p(x+1.2,y+1.2)),fill=glow)
        skyline=[(152,118),(152,96),(166,96),(166,88),(178,88),(178,100),(192,100),(192,84),(204,84),(204,98),
                 (236,98),(236,90),(250,90),(250,80),(262,80),(262,96),(280,96),(280,86),(296,86),(296,100),(316,100),(316,118)]
        draw.polygon([p(x,y) for x,y in skyline],fill=_mix(deep,ink,.55))
        # Sill and cat silhouette looking out of the window.
        draw.rounded_rectangle((*p(138,116),*p(330,126)),radius=3*s,fill=_mix(glow,top,.35))
        draw.ellipse((*p(196,78),*p(236,118)),fill=ink)
        draw.ellipse((*p(204,56),*p(230,82)),fill=ink)
        draw.polygon([p(205,64),p(207,48),p(215,58)],fill=ink)
        draw.polygon([p(229,64),p(227,48),p(219,58)],fill=ink)
        draw.line([p(234,112),p(250,114),p(258,104),p(254,94)],fill=ink,width=5*s,joint='curve')
        # Potted plant on the right and a soft curtain on the left.
        draw.polygon([p(300,116),p(304,100),p(322,100),p(326,116)],fill=_mix(ink,deep,.3))
        for box in ((298,78,312,100),(310,72,324,98),(304,64,318,90),(316,84,332,102)):
            draw.ellipse(tuple(v*s for v in box),fill=_mix(ink,'#3E6B5A',.35))
        curtain=Image.new('RGBA',(W,H));curtain_draw=ImageDraw.Draw(curtain)
        curtain_draw.polygon([p(118,0),p(146,0),p(140,60),p(150,126),p(126,126),p(132,62)],fill=(*_rgb(glow),70))
        image=Image.alpha_composite(image,curtain)
        # Rounded right corners, then fade the left third into the panel colour.
        shape=Image.new('L',(W,H));ImageDraw.Draw(shape).rounded_rectangle((-40*s,0,W-1,H-1),radius=18*s,fill=255)
        ramp=Image.linear_gradient('L').rotate(90).resize((W,H))
        ramp=ramp.point(lambda v:min(255,int(v*2.2)))
        alpha=Image.composite(ramp,Image.new('L',(W,H)),shape)
        base=Image.new('RGBA',(W,H),(*_rgb(C[fade][mode]),255))
        image.putalpha(alpha)
        variants.append(Image.alpha_composite(base,image).convert('RGB'))
    return ctk.CTkImage(light_image=variants[0],dark_image=variants[1],size=SCENE_SIZE)


def sidebar_decor():
    """Tail swoosh and paw prints for the bottom of the always-dark sidebar."""
    width,height=180,70;s=3
    image=Image.new('RGBA',(width*s,height*s))
    draw=ImageDraw.Draw(image)
    color=(*_rgb(C['nav_decor'][0]),200)
    points=[]
    for i in range(41):
        t=i/40
        points.append(((6+t*118)*s,(44-18*math.sin(math.pi*t*1.7))*s))
    draw.line(points,fill=color,width=6*s,joint='curve')
    paw=(*_rgb(C['nav_decor'][0]),150)
    _paw(draw,140*s,40*s,6*s,paw)
    _paw(draw,162*s,22*s,5*s,paw)
    return ctk.CTkImage(light_image=image,dark_image=image,size=(width,height))


class FocusClock(ctk.CTkFrame):
    def __init__(self,parent,app):
        super().__init__(parent,fg_color='transparent',width=248,height=248)
        self.app=app
        self.grid_propagate(False)
        self.face=ctk.CTkLabel(self,text='',width=248,height=248)
        self.face.grid(row=0,column=0)
        family='Menlo' if app.tk.call('tk','windowingsystem')=='aqua' else 'Consolas' if app.tk.call('tk','windowingsystem')=='win32' else 'DejaVu Sans Mono'
        self.time_label=ctk.CTkLabel(self,text='',font=ctk.CTkFont(family=family,size=48),text_color=C['focus_text'])
        self.time_label.place(relx=.5,rely=.45,anchor='center')
        self.caption_label=app.label(self,'',12,'focus_secondary',wraplength=190,justify='center')
        self.caption_label.place(relx=.5,rely=.62,anchor='center')
        self.percent=None

    def set(self,remaining,total,caption):
        self.time_label.configure(text=f'{remaining//60:02d}:{remaining%60:02d}')
        self.caption_label.configure(text=caption)
        percent=round(100*(1-remaining/max(1,total)))
        percent=max(0,min(100,percent))
        if self.percent==percent:return
        self.percent=percent
        variants=[]
        for mode in (0,1):
            image=Image.new('RGBA',(744,744))
            draw=ImageDraw.Draw(image)
            track=C['focus_track'][mode]
            tick=('#B7A4CF','#766086')[mode]
            draw.ellipse((57,57,687,687),outline=track,width=9)
            if percent:draw.arc((57,57,687,687),start=-90,end=-90+percent*3.6,fill=C['focus_accent'][mode],width=9)
            for index in range(48):
                a=index*math.pi/24-math.pi/2
                outer=298;inner=286 if index%4==0 else 292
                draw.line([(372+inner*math.cos(a),372+inner*math.sin(a)),
                           (372+outer*math.cos(a),372+outer*math.sin(a))],fill=tick,width=3)
            variants.append(image)
        self.image=ctk.CTkImage(light_image=variants[0],dark_image=variants[1],size=(248,248))
        self.face.configure(image=self.image)


class MonthAgenda(ctk.CTkFrame):
    def __init__(self,parent,app):
        super().__init__(parent,fg_color=C['card'],corner_radius=18)
        self.app=app
        self.grid_columnconfigure(tuple(range(7)),weight=1,uniform='calendar')
        self.title=app.label(self,'',16,bold=True)
        self.title.grid(row=0,column=0,columnspan=7,sticky='ew',padx=18,pady=(18,14))
        for index,key in enumerate(('Mon','Tue','Wed','Thu','Fri','Sat','Sun')):
            label=ctk.CTkLabel(self,text=tr(app,key),font=app.font(10),text_color=C['secondary'])
            label.grid(row=1,column=index,padx=2,pady=(0,6))
        self.cells=[]
        for index in range(42):
            label=ctk.CTkLabel(self,text='',height=28,corner_radius=8,font=app.font(11),width=28)
            label.grid(row=2+index//7,column=index%7,padx=2,pady=2)
            self.cells.append(label)
        self.hint=app.label(self,'',11,'secondary',wraplength=250)
        self.hint.grid(row=8,column=0,columnspan=7,sticky='ew',padx=18,pady=(10,16))

    def show(self,today,exams):
        self.title.configure(text=tr(self.app,'{v0} {v1}',v0=tr(self.app,MONTHS[today.month-1]),v1=today.year))
        dates={item['exam_date'] for item in exams}
        weeks=calendar.Calendar(firstweekday=0).monthdayscalendar(today.year,today.month)
        days=[day for week in weeks for day in week]
        for index,cell in enumerate(self.cells):
            day=days[index] if index<len(days) else 0
            if not day:cell.configure(text='',fg_color='transparent');cell.grid_remove();continue
            cell.grid()
            exam=date(today.year,today.month,day).isoformat() in dates
            selected=day==today.day
            cell.configure(text=str(day)+(' •' if exam else ''),
                fg_color=C['primary'] if selected else C['selected'] if exam else 'transparent',
                text_color=C['on_primary'] if selected else C['text'])
        self.hint.configure(text=tr(self.app,'Exam dates are marked with a dot.'))
