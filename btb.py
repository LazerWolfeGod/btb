import pygame,math,random,sys,os,copy
import PyUI as pyui
pygame.init()
screenw = 800
screenh = 600
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
pygame.display.set_caption('btb')
pygame.scrap.init()
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
ui.defaultcol = (16,163,127)
ui.defaulttextcol = (255,255,255)
ui.defaultanimationspeed = 20

def sectostr(sec):
    h = int(sec//3600)
    m = str(int(sec%3600//60))
    s = str(int(sec%60))
    ms = sec%1
    if len(s) == 1: s = '0'+s
    if h == 0:
        return f'{m}:{s}'
    else:
        return f'{h}:{m}:{s}'

class funcercm:
    def __init__(self,param,music):
        self.func = lambda: music.controlmenu(param)
class funcerpl:
    def __init__(self,param,music):
        self.func = lambda: music.moveplaylist(param)
        
class MUSIC:
    def __init__(self):
        self.shuffle = False
        self.playing = False
        self.storevolume = 1
        
        self.loadmusic()
        self.playlists = []
        self.playlists.append([[self.allsongs[a] for a in range(len(self.allsongs))],'All Music'])
        self.activeplaylist = 0
        self.activesong = -1
        self.generatequeue()
        self.songhistory = []
        self.nextsong()

        self.makegui()
        
    def loadmusic(self):
        files = [pyui.resourcepath('songs\\'+f) for f in os.listdir(pyui.resourcepath('songs')) if f[len(f)-4:]=='.mp3']
        self.allsongs = [f for f in files]
        self.songdata = []
        for a in self.allsongs:
            self.songdata.append({'path':a})
            fl = a.removesuffix('.mp3')
            name = fl.split('\\')[-1]
            fl+='.dat'
            if not os.path.isfile(fl):
                songmp3 = pygame.mixer.Sound(a)
                length = round(songmp3.get_length())
                with open(fl,'w') as f:
                    f.write(f'name:{name}\n')
                    f.write(f'artist:unknown\n')
                    f.write(f'length:{length}\n')
            with open(fl,'r') as f:
                data = f.readlines()
            for b in data:
                split = b.replace('\n',':').split(':')
                self.songdata[-1][split[0]] = split[1]
    def generatequeue(self):
        if not self.shuffle:
            if self.activesong == -1:
                self.queue = copy.copy(self.playlists[self.activeplaylist][0])
            else:
                self.queue = [self.playlists[self.activeplaylist][0][a] for a in range(self.playlists[self.activeplaylist][0].index(self.activesong),len(self.playlists[self.activeplaylist][0]))]

    def nextsong(self):
        pygame.mixer.music.unload()
        self.missedtime = 0
        self.realtime = 0
        if self.activesong != -1:
            self.songhistory.append(self.activesong)
        if len(self.queue)!=0:
            self.activesong = self.queue[0]
            del self.queue[0]
            pygame.mixer.music.load(self.activesong)
            songmp3 = pygame.mixer.Sound(self.activesong)
            self.songlength = round(songmp3.get_length())
            self.refreshsongdisplays()
            

            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            pygame.mixer.music.play()
            if not self.playing:
                pygame.mixer.music.pause()
        else:
            self.activesong = -1
    def prevsong(self):
        self.queue.insert(0,0)
             
    def update(self):
        if self.activesong!=-1:
            self.realtime = round(pygame.mixer.music.get_pos()/1000)+self.missedtime
            if sectostr(self.realtime)!=ui.IDs['songtime'].text:
                if not ui.IDs['song duration button'].holding:
                    ui.IDs['song duration'].slider = self.realtime
                ui.IDs['songtime'].text = sectostr(self.realtime)
                ui.IDs['songtime'].refresh(ui)
                ui.IDs['songtime'].resetcords(ui)
    def refreshsongdisplays(self):
        if 'songlength' in ui.IDs:
            ui.IDs['song duration'].maxp = self.songlength
            ui.IDs['songlength'].text = sectostr(self.songlength)
            ui.IDs['songlength'].refresh(ui)
            ui.IDs['songlength'].resetcords(ui)
            ui.IDs['song title'].text = self.songdata[self.allsongs.index(self.activesong)]['name']
            ui.IDs['song title'].refresh(ui)
            ui.IDs['song title'].resetcords(ui)
            ui.IDs['artist name'].text = self.songdata[self.allsongs.index(self.activesong)]['artist']
            ui.IDs['artist name'].refresh(ui)
            ui.IDs['artist name'].resetcords(ui)
            
    def makegui(self):
        self.songbarwidth = 0.4
        ## main 3 buttons
        ui.makerect(0,0,screenw,93,col=(32,33,35),anchor=(0,'h-93'),layer=4,scalesize=False,ID='controlbar')
        ui.makebutton(0,0,'{pause rounded=0.1}',30,anchor=('w/2','h-60'),toggletext='{play rounded=0.05}',toggleable=True,togglecol=(16,163,127),center=True,width=49,height=49,roundedcorners=100,scalesize=False,clickdownsize=2,command=self.playpause,toggle=self.playing,ID='playpause button',layer=5)
        ui.makebutton(0,0,'{skip rounded=0.05 left}',22,anchor=('w/2-55','h-60'),center=True,width=45,height=45,roundedcorners=100,scalesize=False,clickdownsize=2,layer=5)
        ui.makebutton(0,0,'{skip rounded=0.05}',22,anchor=('w/2+55','h-60'),center=True,width=45,height=45,roundedcorners=100,scalesize=False,clickdownsize=2,command=self.nextsong,layer=5)

        ## song progress slider
        ui.makeslider(0,0,screenw*self.songbarwidth,12,maxp=self.songlength,anchor=('w/2','h-19'),center=True,border=1,roundedcorners=4,button=ui.makebutton(0,0,'',width=20,height=20,clickdownsize=0,borderdraw=False,backingdraw=False,runcommandat=1,command=self.setsongtime,ID='song duration button'),movetoclick=True,scalesize=False,col=(131,243,216),backingcol=(16,163,127),ID='song duration',layer=5)
        ui.maketext(0,0,sectostr(0),20,backingcol=(32,33,35),anchor=('w*'+str((1-self.songbarwidth)/2)+'-8','h-19'),objanchor=('w','h/2'),scalesize=False,ID='songtime',layer=5)
        ui.maketext(0,0,sectostr(self.songlength),20,backingcol=(32,33,35),anchor=('w*'+str((1+self.songbarwidth)/2)+'+8','h-19'),objanchor=('0','h/2'),scalesize=False,ID='songlength',layer=5)

        ## volume control
        ui.makeslider(0,0,100,12,maxp=1,anchor=('w-10','h-46'),objanchor=('w','h/2'),border=1,roundedcorners=4,button=ui.makebutton(0,0,'',width=20,height=20,clickdownsize=0,borderdraw=False,backingdraw=False,runcommandat=1,command=self.setvolume,ID='volume button'),movetoclick=True,scalesize=False,col=(131,243,216),backingcol=(16,163,127),startp=self.storevolume,ID='volume',layer=5)
        ui.makebutton(0,0,'{speaker}',20,anchor=('w-120','h-46'),objanchor=('w','h/2'),roundedcorners=10,scalesize=False,clickdownsize=2,spacing=4,toggleable=True,togglecol=(16,163,127),toggletext='{mute}',command=self.mutetoggle,ID='mute button',layer=5)

        ## song title/image
        ui.maketext(0,0,'',70,anchor=('50','h-46'),center=True,scalesize=False,img=pyui.loadinganimation(12),ID='img',layer=5)
        ui.maketext(0,0,'Song',20,anchor=('90','h-45'),objanchor=(0,'h'),backingcol=(32,33,35),maxwidth=200,textcenter=False,scalesize=False,ID='song title',layer=5)
        ui.maketext(0,0,'Artist',15,anchor=('90','h-45'),backingcol=(32,33,35),maxwidth=200,textcol=(220,220,220),scalesize=False,ID='artist name',layer=5)  
        
        ## playlist
        titles = [ui.maketext(0,0,'Image',30,textcenter=True,col=(62,63,75)),
                  ui.maketext(0,0,'Song',30,textcenter=True,col=(62,63,75)),
                  ui.maketext(0,0,'Artist',30,textcenter=True,col=(62,63,75)),
                  ui.maketext(0,0,'Length',30,textcenter=True,col=(62,63,75)),'']
        ui.maketable(160,100,[],titles,ID='playlist',boxwidth=[80,150,120,80],boxheight=[40],backingdraw=True,textsize=20,verticalspacing=4,textcenter=False,col=(62,63,75),scalesize=False,scalex=False,scaley=False,roundedcorners=4)
        self.refreshsongtable()
        ui.maketext(0,5,self.playlists[self.activeplaylist][1],80,anchor=(160+ui.IDs['playlist'].width/2,0),center=True,centery=False,scalesize=False,scalex=False,scaley=False,ID='playlist name')
        ui.maketext(0,65,str(len(self.playlists[self.activeplaylist][0]))+' songs',30,anchor=(160+ui.IDs['playlist'].width/2,0),center=True,centery=False,scalesize=False,scalex=False,scaley=False,ID='playlist info')

        ## side bar
        ui.makerect(150,0,4,1000,layer=2,scalesize=False,scalex=False,scaley=False)
        ui.maketext(75,30,'Playlists',40,center=True,scalesize=False,scalex=False,scaley=False)
        ui.makebutton(10,50,'+',55,roundedcorners=30,width=35,height=35,textoffsety=-3,scalesize=False,scalex=False,scaley=False,command=self.makeplaylist)
        ui.maketable(10,95,[['']],roundedcorners=4,textsize=20,boxwidth=130,scalesize=False,scalex=False,scaley=False,verticalspacing=3,ID='playlist table')
        self.refreshplaylisttable()
        
        ## control menu
        ui.makewindowedmenu(0,0,100,140,'control','main',col=(52,53,65),scalesize=False,scalex=False,scaley=False,roundedcorners=10,ID='controlmenu')
        ui.makebutton(5,5,'Play',30,col=(62,63,75),textcol=(240,240,240),roundedcorners=8,width=90,height=40,menu='control',command=self.playselected,scalesize=False,scalex=False,scaley=False)
        ui.makebutton(5,50,'Queue',30,col=(62,63,75),textcol=(240,240,240),roundedcorners=8,width=90,height=40,menu='control',command=self.queueselected,scalesize=False,scalex=False,scaley=False)
        ui.makebutton(5,95,'Info',30,col=(62,63,75),textcol=(240,240,240),roundedcorners=8,width=90,height=40,menu='control',command=self.infomenu,scalesize=False,scalex=False,scaley=False)

        ## info editor
        ui.makewindowedmenu(160,20,400,156,'song info','main',col=(52,53,65),scalesize=False,scalex=False,scaley=False,roundedcorners=10,colorkey=(2,2,2))
        ui.maketable(5,5,[['Name',ui.maketextbox(0,0,'',200,2,roundedcorners=2,textsize=30,col=(62,63,75),ID='inputinfo name')],
                          ['Artist',ui.maketextbox(0,0,'',200,2,roundedcorners=2,textsize=30,col=(62,63,75),ID='inputinfo artist')],
                          ['Image',ui.maketextbox(0,0,'',200,2,roundedcorners=2,textsize=30,col=(62,63,75),ID='inputinfo image')],
                          ['File',ui.maketext(0,0,'',30,roundedcorners=2,col=(62,63,75),ID='inputinfo file')]],boxwidth=[-1,300],menu='song info',roundedcorners=4,textsize=30,scalesize=False,scalex=False,scaley=False,verticalspacing=3,col=(62,63,75))
        ui.makebutton(200,138,'Save',30,self.saveinfo,'song info',roundedcorners=8,spacing=2,horizontalspacing=14,center=True,clickdownsize=2)
        self.refreshsongdisplays()
    def setsongtime(self):
        if ui.IDs['song duration button'].clickedon == 2 and self.activesong!=-1:
            self.missedtime = ui.IDs['song duration'].slider-pygame.mixer.music.get_pos()/1000
            pygame.mixer.music.set_pos(ui.IDs['song duration'].slider)
    def setvolume(self):
        pygame.mixer.music.set_volume(ui.IDs['volume'].slider)
        if ui.IDs['volume'].slider == 0:
            ui.IDs['mute button'].toggle = False
        else:
            ui.IDs['mute button'].toggle = True
    def mutetoggle(self):
        if not ui.IDs['mute button'].toggle:
            self.storevolume = ui.IDs['volume'].slider
            ui.IDs['volume'].slider = 0
        else:
            ui.IDs['volume'].slider = self.storevolume
        self.setvolume()
            
    def playpause(self):
        self.playing = ui.IDs['playpause button'].toggle
        if self.playing:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
    def refreshsongtable(self):
        ui.IDs['playlist'].wipe(ui,False)
        data = []
        for a in self.playlists[self.activeplaylist][0]:
            func = funcercm(a,self)
            obj = ui.makebutton(0,0,'{dots}',20,command=func.func,col=(62,63,75),clickdownsize=1,roundedcorners=4)
            dat = self.songdata[self.allsongs.index(a)]
            data.append(['-',dat['name'],dat['artist'],sectostr(float(dat['length'])),obj])
        ui.IDs['playlist'].data = data
        ui.IDs['playlist'].refresh(ui)
        ui.IDs['playlist'].refreshcords(ui)
    def refreshplaylisttable(self):
        ui.IDs['playlist table'].wipe(ui)
        data = []
        for a in self.playlists:
            func = funcerpl(self.playlists.index(a),self)
            data.append([ui.makebutton(0,0,a[1],25,clickdownsize=1,roundedcorners=4,verticalspacing=4,command=func.func)])
        ui.IDs['playlist table'].data = data
        ui.IDs['playlist table'].refresh(ui)
        ui.IDs['playlist table'].refreshcords(ui)
    def makeplaylist(self):
        self.playlists.append([[],'New Playlist'])
        self.moveplaylist(len(self.playlists)-1)
        self.refreshplaylisttable()
    def moveplaylist(self,playlist):
        self.activeplaylist = playlist
        self.refreshsongtable()
        ui.IDs['playlist name'].text = self.playlists[self.activeplaylist][1]
        ui.IDs['playlist name'].refresh(ui)
        ui.IDs['playlist name'].resetcords(ui)
        ui.IDs['playlist info'].text = str(len(self.playlists[self.activeplaylist][0]))+' songs'
        ui.IDs['playlist info'].refresh(ui)
        ui.IDs['playlist info'].resetcords(ui)
        
    def controlmenu(self,song):
        self.selected = song
        mpos = pygame.mouse.get_pos()
        ui.IDs['controlmenu'].x = mpos[0]
        ui.IDs['controlmenu'].y = mpos[1]
        ui.IDs['controlmenu'].startanchor = mpos
        ui.movemenu('control','down')
    def infomenu(self):
        dat = self.songdata[self.allsongs.index(self.selected)]
        ui.IDs['inputinfo name'].text = dat['name']
        ui.IDs['inputinfo artist'].text = dat['artist']
        ui.IDs['inputinfo file'].text = self.selected.removeprefix(os.getcwd())
        ui.IDs['inputinfo name'].refresh(ui)
        ui.IDs['inputinfo artist'].refresh(ui)
        ui.IDs['inputinfo file'].refresh(ui)
        ui.movemenu('song info','down')
    def saveinfo(self):
        name = ui.IDs['inputinfo name'].text
        artist = ui.IDs['inputinfo artist'].text
        self.songdata[self.allsongs.index(self.selected)]['name'] = name
        self.songdata[self.allsongs.index(self.selected)]['artist'] = artist
        length = self.songdata[self.allsongs.index(self.selected)]['length']
        fl = self.selected.removesuffix('.mp3')
        fl+='.dat'
        with open(fl,'w') as f:
            f.write(f'name:{name}\n')
            f.write(f'artist:{artist}\n')
            f.write(f'length:{length}\n')
        self.refreshsongtable()
        
    def playselected(self):
        self.activesong = self.selected
        self.generatequeue()
        ui.menuback()
        self.nextsong()
        if not self.playing:
            ui.IDs['playpause button'].toggle = True
            self.playpause()
    def queueselected(self):
        self.queue.insert(0,self.selected)
        ui.menuback()

    

music = MUSIC()

while not done:
    pygameeventget = ui.loadtickdata()
    for event in pygameeventget:
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.VIDEORESIZE:
            screenw = event.w
            screenh = event.h
            ui.IDs['controlbar'].width = screenw
            ui.IDs['song duration'].width = event.w*music.songbarwidth
            ui.IDs['song duration'].resetcords(ui)
        if event.type == pygame.mixer.music.get_endevent():
            music.nextsong()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and ui.activemenu == 'main':
                if ui.IDs['playpause button'].toggle: ui.IDs['playpause button'].toggle = False
                else: ui.IDs['playpause button'].toggle = True
                music.playpause()
    
    screen.fill((62,63,75))
    music.update()
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)
pygame.mixer.music.stop()
pygame.quit() 
