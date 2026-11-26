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
