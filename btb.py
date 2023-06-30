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
    
class MUSIC:
    def __init__(self):
        self.shuffle = False
        self.playing = False
        
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
        files = [pyui.resourcepath('songs\\'+f) for f in os.listdir(pyui.resourcepath('songs'))]
        self.allsongs = [f for f in files]
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
            self.refreshlengthtimer()


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
    def refreshlengthtimer(self):
        if 'songlength' in ui.IDs:
            ui.IDs['songlength'].text = sectostr(self.songlength)
            ui.IDs['songlength'].refresh(ui)
            ui.IDs['songlength'].resetcords(ui)
            
    def makegui(self):
        self.songbarwidth = 0.4
        ui.makerect(0,0,screenw,93,col=(32,33,35),anchor=(0,'h-93'),layer=0,scalesize=False,ID='controlbar')
        ui.makebutton(0,0,'{pause rounded=0.1}',30,anchor=('w/2','h-60'),toggletext='{play rounded=0.05}',toggleable=True,togglecol=(16,163,127),center=True,width=49,height=49,roundedcorners=100,scalesize=False,clickdownsize=2,command=self.playpause,toggle=self.playing,ID='playpause button')
        ui.makebutton(0,0,'{skip rounded=0.05 left}',22,anchor=('w/2-55','h-60'),center=True,width=45,height=45,roundedcorners=100,scalesize=False,clickdownsize=2)
        ui.makebutton(0,0,'{skip rounded=0.05}',22,anchor=('w/2+55','h-60'),center=True,width=45,height=45,roundedcorners=100,scalesize=False,clickdownsize=2,command=self.nextsong)

        ui.makeslider(0,0,screenw*self.songbarwidth,12,maxp=self.songlength,anchor=('w/2','h-19'),center=True,border=1,roundedcorners=4,button=ui.makebutton(0,0,'',width=20,height=20,clickdownsize=0,borderdraw=False,backingdraw=False,runcommandat=1,command=self.setsongtime,ID='song duration button'),movetoclick=True,scalesize=False,col=(131,243,216),backingcol=(16,163,127),ID='song duration')
        ui.maketext(0,0,sectostr(0),20,backingcol=(32,33,35),anchor=('w*'+str((1-self.songbarwidth)/2)+'-8','h-19'),objanchor=('w','h/2'),scalesize=False,ID='songtime')
        ui.maketext(0,0,sectostr(self.songlength),20,backingcol=(32,33,35),anchor=('w*'+str((1+self.songbarwidth)/2)+'+8','h-19'),objanchor=('0','h/2'),scalesize=False,ID='songlength')

        ui.makeslider(0,0,100,12,maxp=1,anchor=('w-20','h-46'),objanchor=('w','h/2'),border=1,roundedcorners=4,button=ui.makebutton(0,0,'',width=20,height=20,clickdownsize=0,borderdraw=False,backingdraw=False,runcommandat=1,command=self.setvolume,ID='volume button'),movetoclick=True,scalesize=False,col=(131,243,216),backingcol=(16,163,127),startp=1,ID='volume')
        
    def setsongtime(self):
        if ui.IDs['song duration button'].clickedon == 2 and self.activesong!=-1:
            self.missedtime = ui.IDs['song duration'].slider-pygame.mixer.music.get_pos()/1000
            pygame.mixer.music.set_pos(ui.IDs['song duration'].slider)
    def setvolume(self):
        pygame.mixer.music.set_volume(ui.IDs['volume'].slider)
    def playpause(self):
        self.playing = ui.IDs['playpause button'].toggle
        if self.playing:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    

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
    
    screen.fill((62,63,75))
    music.update()
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)
pygame.mixer.music.stop()
pygame.quit() 
