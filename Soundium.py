import pygame,time,math,random,sys,os,copy,requests,threading,urllib,re,pytube
import PyUI as pyui
from bs4 import BeautifulSoup
##pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
screenw = 800
screenh = 600

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

logo = pygame.image.load(resource_path('assets\\soundium_icon black.png'))
logo.set_colorkey((0,0,0))
logow = pygame.image.load(resource_path('assets\\soundium_icon white.png'))
logow.set_colorkey((255,255,255))
pygame.display.set_icon(logow)
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
pygame.display.set_caption('Soundium')
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

def makefileable(name):
    swaps = {'’':"'"}
    for a in list(swaps):
        name = name.replace(a,swaps[a])

    nstring = ''
    for a in name:
        if ord(a)>126:
            nstring+=asciify(a)
        else:
            nstring+=a
    
    special = '\/:*?"<>|'
    for a in special:
        nstring = nstring.replace(a,'')
    return nstring

def asciify(text):
    dat = [ord(a) for a in text]
    st = ''
    for a in dat:
        st+=chr((a-32)%94+32)
    return st

def loadimage(url,name,thumbnail=False):
    if thumbnail:
        path = pyui.resourcepath(f'data\\thumbnails\\{name}.png')
    else:
        path = pyui.resourcepath(f'data\\images\\{name}.png')
    if not os.path.isfile(path):
        img_data = requests.get(url).content
        with open(path, 'wb') as handler:
            handler.write(img_data)
    return path

def songdatapull(data):
    info = {}
    info['album'] = data['album']['name']
    info['name'] = data['name']
    artists = [a['name'] for a in data['artists']]
    artist = ''
    for a in artists:
        artist = artist+a+','
    artist = artist.removesuffix(',')
    info['artist'] = artist
    info['length'] = data['duration_ms']/1000
    info['image_url'] = data['album']['images'][0]['url']
    return info

def spotifyplaylistpull(link):
    try:
        import spotipy
    except:
        return 0
    from spotipy.oauth2 import SpotifyClientCredentials
    client_id = 'bbafafb36cc04da98d011939cf935c33'
    client_secret = '4864d4b57ec44d20b4ef67607e810e51'
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    print('---loading spotify')
    try:
        data = sp.playlist(link)
        fulltracks = sp.playlist_tracks(link,limit=100)
        lenn = len(fulltracks['items'])
        while lenn != 0:
            extendor = sp.playlist_tracks(link,limit=100,offset=len(fulltracks['items']))
            fulltracks['items'] += extendor['items']
            lenn = len(extendor['items'])
        data['tracks'] = fulltracks
    except:
        print('invalid link')
        return 0
    songdata = []
    print(len(data['tracks']['items']))
    for a in data['tracks']['items']:
        songdata.append(songdatapull(a['track']))
    files = []
    for a in songdata:
        print('loading:',a['name'])
        files.append(makedat(a))
    print('-------------finished')
    return [[readdat(a)['dat_path'] for a in files],data['name']]

def downloadyoutube(url,name,music,refresh=True):
    print('downloading',name)
    yt = pytube.YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    mp3 = audio.download(pyui.resourcepath(''),'temp.mp3')
    path = pyui.resourcepath(f"data\\mp3s\\{name}.mp3")
    os.system("cd "+pyui.resourcepath(''))
    os.system(f'ffmpeg -i "temp.mp3" -ab 160k -f mp3 "{path}"')
    if refresh:
        if music.selected == -1:
            music.scanmp3s(f'http://img.youtube.com/vi/{url.split("=")[-1]}/0.jpg')
        else:
            music.songdata[music.allsongs.index(music.selected)]['mp3_path'] = pyui.resourcepath(f'data\\mp3s\\{name}.mp3')
            music.songdata[music.allsongs.index(music.selected)]['downloaded'] = True
            songmp3 = pygame.mixer.Sound(music.songdata[music.allsongs.index(music.selected)]['mp3_path'])
            music.songdata[music.allsongs.index(music.selected)]['length'] = songmp3.get_length()
            makedat(music.songdata[music.allsongs.index(music.selected)],True)
        music.loadmusic()
        music.loadplaylists()
        music.refreshsongtable(True,True)
        music.awaitingthreads['download youtube'][0] = True

def fullautodownload(download):
    for i,song in enumerate(download):
        print(f'downloading {song["name"]} {i+1}/{len(download)}')
        term = asciify(f'{song["name"]} {song["artist"]}'.replace(' ','+'))
        html = urllib.request.urlopen(f'https://www.youtube.com/results?search_query="{term}"')
        url = re.findall(r'watch\?v=(\S{11})',html.read().decode())[0]
        name = song['name']+'-'+song['artist']
        downloadyoutube('https://www.youtube.com/watch?v='+url,name,music,False)
        song['mp3_path'] = pyui.resourcepath(f'data\\mp3s\\{name}.mp3')
        song['downloaded'] = True
        songmp3 = pygame.mixer.Sound(song['mp3_path'])
        song['length'] = songmp3.get_length()
        makedat(song,True)
    music.loadmusic()
    music.loadplaylists()
    music.refreshsongtable(True,True)
    music.awaitingthreads['fullautodownload'][0] = True

def makedat(info,overwrite=False):
    if 'name' in info: name = makefileable(info['name'])
    else: name = 'unknown'
    if 'artist' in info: artist = makefileable(info['artist'])
    else: artist = 'unknown'
    if 'album' in info: album = makefileable(info['album'])
    else: album = 'unknown'
    if 'length' in info: length = info['length']
    else: length = 0
    if 'time' in info: tim = info['time']
    else: tim = time.time()
    if 'image_url' in info: image_url = info['image_url']
    else: image_url = 'none'
    if 'image_path' in info: image_path = info['image_path']
    else:
        if image_url == 'none':image_path = 'none'
        else:
            if album == 'unknown': image_path = loadimage(image_url,name)
            else: image_path = loadimage(image_url,album)
    if 'mp3_path' in info: mp3_path = info['mp3_path']
    else: mp3_path = 'none'
    if 'downloaded' in info: downloaded = info['downloaded']
    else: downloaded = False
    if 'dat_path' in info: file = info['dat_path']
    else:
        if mp3_path == 'none': file = pyui.resourcepath(f'data\\songs\\{name}-{artist}.dat')
        else:
            n = path.split('\\')[-1].removesuffix('.mp3')
            file = pyui.resourcepath('data\\songs\\'+n+'.dat')
    if not(os.path.isfile(file)) or overwrite:
        try:
            with open(file,'w') as f:
                f.write(f'name:{name}\n')
                f.write(f'artist:{artist}\n')
                f.write(f'album:{album}\n')
                f.write(f'length:{length}\n')
                f.write(f'image_path:{image_path}\n')
                f.write(f'image_url:{image_url}\n')
                f.write(f'mp3_path:{mp3_path}\n')
                f.write(f'dat_path:{file}\n')
                f.write(f'downloaded:{downloaded}\n')
                f.write(f'time:{tim}\n')
        except Exception as e:
            os.remove(file)
            info['name'] = asciify(info['name'])
            makedat(info)
            print('failed to save:',name,e,info)
            
    return file

def readdat(path):
    with open(path,'r') as f:
        data = f.readlines()
    info = {}
    for b in data:
        b = b.removesuffix('\n')
        split = b.split(':',1)
        if split[1] == 'False': split[1] = False
        elif split[1] == 'True': split[1] = True
        elif split[0] == 'time': split[1] = float(split[1])
        info[split[0]] = split[1]
    info['dat_path'] = path
    return info

def makeplst(pl):
    path = pyui.resourcepath(f'data\\playlists\\{makefileable(pl[1])}.plst')
    with open(path,'w') as f:
        f.write(pl[1]+'\n')
        for a in pl[0]:
            f.write(f'{a}\n')
def readplst(title='',path=''):
    if path == '':
        path = pyui.resourcepath(f'data\\playlists\\{makefileable(title)}.plst')
##    if title == '':
##        title = path.split('\\')[-1].removesuffix('.plst')
    pl = []
    with open(path,'r') as f:
        data = f.readlines()
    title = data[0].removesuffix('\n')
    for a in data[1:]:
        pl.append(a.removesuffix('\n'))
    return [pl,title]
    

class funcercm:
    def __init__(self,param,music):
        self.func = lambda: music.controlmenu(param)
class funcerpl:
    def __init__(self,param,music):
        self.func = lambda: music.moveplaylist(param)
class funceram:
    def __init__(self,param,music):
        self.func = lambda: music.addtoplaylist(param)
class funceryt:
    def __init__(self,url,name,music):
        self.func = lambda: music.downloadyoutube(url,name)
class funcerps:
    def __init__(self,song,music):
        self.func = lambda: music.playselected(song)
        
class MUSIC:
    def __init__(self):
        self.shuffle = False
        self.playing = False
        self.storevolume = 1
        self.songlength = 1
        self.awaitingthreads = {}
        self.selected = -1

        self.initfiles()
        self.scanmp3s()
        self.loadmusic()
        self.loadplaylists()
        self.activeplaylist = 0
        self.playingplaylist = 0
        self.activesong = -1
        self.generatequeue()
        self.loadhistory()

        self.makegui()


    def initfiles(self):
        if not os.path.isdir(pyui.resourcepath('data')):
            os.mkdir(pyui.resourcepath('data'))
        if not os.path.isdir(pyui.resourcepath('data\\songs')):
            os.mkdir(pyui.resourcepath('data\\songs'))
        if not os.path.isdir(pyui.resourcepath('data\\mp3s')):
            os.mkdir(pyui.resourcepath('data\\mp3s'))
        if not os.path.isdir(pyui.resourcepath('data\\playlists')):
            os.mkdir(pyui.resourcepath('data\\playlists'))
        if not os.path.isdir(pyui.resourcepath('data\\images')):
            os.mkdir(pyui.resourcepath('data\\images'))
        if not os.path.isdir(pyui.resourcepath('data\\thumbnails')):
            os.mkdir(pyui.resourcepath('data\\thumbnails'))
    def scanmp3s(self,image='none'):
        dats = [pyui.resourcepath('data\\songs\\'+f) for f in os.listdir(pyui.resourcepath('data\\songs')) if f[len(f)-4:]=='.dat']
        data = [readdat(a) for a in dats]
        used = [a['mp3_path'].lower() for a in data]
        
        files = [pyui.resourcepath('data\\mp3s\\'+f) for f in os.listdir(pyui.resourcepath('data\\mp3s')) if f[len(f)-4:] in ['.mp3','.wav']]
        for a in files:
            fl = a.split('\\')[-1]
            fl = fl.rsplit('.')[0]
            name = fl
            fl = pyui.resourcepath('data\\songs\\'+fl+'.dat')
            if not(os.path.isfile(fl)) and not(a.lower() in used):
                print('Processed:',a)
                songmp3 = pygame.mixer.Sound(a)
                length = round(songmp3.get_length())
                makedat({'name':name,'length':length,'mp3_path':a,'dat_path':fl,'downloaded':True,'image_url':image})
    def loadmusic(self):
        files = [pyui.resourcepath('data\\songs\\'+f) for f in os.listdir(pyui.resourcepath('data\\songs')) if f[len(f)-4:]=='.dat']
        self.songdata = []
        self.allsongs = []
        for file in files:
            self.songdata.append(readdat(file))
        self.songdata.sort(key=lambda x: x['time'])
        for a in self.songdata:
            self.allsongs.append(a['dat_path'])
    def loadplaylists(self):
        self.playlists = []
        self.playlists.append([[self.allsongs[a] for a in range(len(self.allsongs))],'All Music'])
        self.playlists.append([[self.allsongs[a] for a in range(len(self.allsongs))],'Queue'])
        self.playlists.append([[self.allsongs[a] for a in range(len(self.allsongs))],'History'])
        
        files = [pyui.resourcepath('data\\playlists\\'+f) for f in os.listdir(pyui.resourcepath('data\\playlists')) if f[len(f)-5:]=='.plst']
        for a in files:
            self.playlists.append(readplst(path=a))
    def loadhistory(self):
        self.songhistory = []
        if not os.path.isfile(pyui.resourcepath('data\\history.txt')):
            with open(pyui.resourcepath('data\\history.txt'),'w'):
                pass
        with open(pyui.resourcepath('data\\history.txt'),'r') as fl:
            lines = fl.readlines()
        for a in lines:
            self.songhistory.append(a.split(' ',1)[1])
        
        
    def generatequeue(self):
        if ('shuffle button' in ui.IDs) and not ui.IDs['shuffle button'].toggle:
            self.queue = [self.playlists[self.playingplaylist][0][a] for a in range(0,len(self.playlists[self.playingplaylist][0]))]
            random.shuffle(self.queue)
            if self.activesong in self.queue:
                self.queue.remove(self.activesong)
        else:
            if self.activesong == -1:
                self.queue = copy.copy(self.playlists[self.playingplaylist][0])
            else:
                self.queue = [self.playlists[self.playingplaylist][0][a] for a in range(self.playlists[self.playingplaylist][0].index(self.activesong),len(self.playlists[self.playingplaylist][0]))]
        self.refreshqueue()
    def nextsong(self):
        pygame.mixer.music.unload()
        self.missedtime = 0
        self.realtime = 0
        if self.activesong != -1:
            self.songhistory.append(self.songdata[self.allsongs.index(self.activesong)]['dat_path'])
            with open(pyui.resourcepath('data\\history.txt'),'a') as f:
                f.write(f"{time.time()} {self.songdata[self.allsongs.index(self.activesong)]['dat_path']}\n")
        if len(self.queue)!=0:
            self.activesong = self.queue[0]
            del self.queue[0]
            while len(self.queue)>0 and not(self.songdata[self.allsongs.index(self.activesong)]['downloaded']):
                self.activesong = self.queue[0]
                del self.queue[0]
            self.refreshqueue()
            if self.songdata[self.allsongs.index(self.activesong)]['downloaded']:
                pygame.mixer.music.load(self.songdata[self.allsongs.index(self.activesong)]['mp3_path'])
                songmp3 = pygame.mixer.Sound(self.songdata[self.allsongs.index(self.activesong)]['mp3_path'])
                self.songlength = round(songmp3.get_length())
                self.refreshsongdisplays()
                pygame.mixer.music.set_endevent(pygame.USEREVENT)
                pygame.mixer.music.play()
                if not self.playing:
                    pygame.mixer.music.pause()
            else:
                if 'playpause button' in ui.IDs: ui.IDs['playpause button'].toggle = False
                self.playing = False
                self.activesong = -1
        else:
            if 'playpause button' in ui.IDs: ui.IDs['playpause button'].toggle = False
            self.playing = False
            self.activesong = -1
    def prevsong(self):
        if len(self.songhistory)>0:
            current = self.activesong
            self.queue.insert(0,self.songhistory[-1])
            self.nextsong()
            self.queue.insert(0,current)
            del self.songhistory[-1]
            del self.songhistory[-1]
             
    def update(self):
        if ui.activemenu == 'main':
            self.selected = -1
        delitem = False
        try:
            for a in self.awaitingthreads:
                if self.awaitingthreads[a][0]:
                    self.awaitingthreads[a][1]()
                    delitem = a
        except Exception as e:
            pass
        if delitem!=False:
            del self.awaitingthreads[delitem]
        if self.activesong!=-1:
            self.realtime = round(pygame.mixer.music.get_pos()/1000)+self.missedtime
            if sectostr(self.realtime)!=ui.IDs['songtime'].text:
                if not ui.IDs['song duration button'].holding:
                    ui.IDs['song duration'].slider = self.realtime
                ui.IDs['songtime'].text = sectostr(self.realtime)
                ui.IDs['songtime'].refresh(ui)
                ui.IDs['songtime'].resetcords(ui)
    def refreshsongdisplays(self):
        if self.activesong != -1 and 'song duration' in ui.IDs:
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
            ui.IDs['song img'].textsize = 70
            if self.songdata[self.allsongs.index(self.activesong)]['image_path'] != 'none':
                ui.IDs['song img'].img = pygame.image.load(self.songdata[self.allsongs.index(self.activesong)]['image_path'])
                if ui.IDs['song img'].img.get_width()/ui.IDs['song img'].img.get_height()>1.1:
                    ui.IDs['song img'].textsize*=0.75
            else:
                ui.IDs['song img'].img = logo
                ui.IDs['song img'].colorkey = (0,0,0)
                ui.IDs['song img'].textsize = 58
            ui.IDs['song img'].refresh(ui)
            ui.IDs['song img'].resetcords(ui)
            
    def makegui(self):
        self.songbarwidth = 0.4
        ## main 3 buttons
        ui.makerect(0,0,screenw,93,col=(32,33,35),anchor=(0,'h-93'),layer=4,scalesize=False,ID='controlbar')
        ui.makebutton(0,0,'{pause rounded=0.1}',30,anchor=('w/2','h-60'),toggletext='{play rounded=0.05}',toggleable=True,togglecol=(16,163,127),center=True,width=49,height=49,roundedcorners=100,scalesize=False,clickdownsize=2,command=self.playpause,toggle=self.playing,ID='playpause button',layer=5)
        ui.makebutton(0,0,'{skip rounded=0.05 left}',22,anchor=('w/2-55','h-60'),center=True,width=45,height=45,roundedcorners=100,scalesize=False,clickdownsize=2,layer=5,command=self.prevsong)
        ui.makebutton(0,0,'{skip rounded=0.05}',22,anchor=('w/2+55','h-60'),center=True,width=45,height=45,roundedcorners=100,scalesize=False,clickdownsize=2,command=self.nextsong,layer=5)

        ## song progress slider
        ui.makeslider(0,0,screenw*self.songbarwidth,12,maxp=self.songlength,anchor=('w/2','h-19'),center=True,border=1,roundedcorners=4,button=ui.makebutton(0,0,'',width=20,height=20,clickdownsize=0,borderdraw=False,backingdraw=False,runcommandat=1,command=self.setsongtime,ID='song duration button'),movetoclick=True,scalesize=False,col=(131,243,216),backingcol=(16,163,127),ID='song duration',layer=5)
        ui.maketext(0,0,sectostr(0),20,backingcol=(32,33,35),anchor=('w*'+str((1-self.songbarwidth)/2)+'-8','h-19'),objanchor=('w','h/2'),scalesize=False,ID='songtime',layer=5)
        ui.maketext(0,0,sectostr(self.songlength),20,backingcol=(32,33,35),anchor=('w*'+str((1+self.songbarwidth)/2)+'+8','h-19'),objanchor=('0','h/2'),scalesize=False,ID='songlength',layer=5)

        ## volume control
        ui.makeslider(0,0,100,12,maxp=1,anchor=('w-10','h-46'),objanchor=('w','h/2'),border=1,roundedcorners=4,button=ui.makebutton(0,0,'',width=20,height=20,clickdownsize=0,borderdraw=False,backingdraw=False,runcommandat=1,command=self.setvolume,ID='volume button'),movetoclick=True,scalesize=False,col=(131,243,216),backingcol=(16,163,127),startp=self.storevolume,ID='volume',layer=5)
        ui.makebutton(0,0,'{speaker}',20,anchor=('w-120','h-46'),objanchor=('w','h/2'),roundedcorners=10,scalesize=False,clickdownsize=2,spacing=4,toggleable=True,togglecol=(16,163,127),toggletext='{mute}',command=self.mutetoggle,ID='mute button',layer=5)
        ui.makebutton(0,0,'{shuffle}',20,self.generatequeue,anchor=('w-162','h-46'),objanchor=('w','h/2'),roundedcorners=10,scalesize=False,clickdownsize=1,spacing=4,toggleable=True,toggletext='{shuffle (16,180,107)}',ID='shuffle button',layer=5,width=35,height=35,backingdraw=False,borderdraw=False)


        ## song title/image
        ui.maketext(0,0,'',70,anchor=('50','h-46'),center=True,scalesize=False,img=pyui.loadinganimation(12),ID='song img',layer=5)
        ui.maketext(0,0,'Song',20,anchor=('90','h-45'),objanchor=(0,'h'),backingcol=(32,33,35),maxwidth=200,textcenter=False,scalesize=False,ID='song title',layer=5)
        ui.maketext(0,0,'Artist',15,anchor=('90','h-45'),backingcol=(32,33,35),maxwidth=200,textcol=(220,220,220),scalesize=False,ID='artist name',layer=5)  
        
        ## playlist
        titles = [ui.maketext(0,0,'Image',30,textcenter=True,col=(62,63,75)),
                  ui.maketext(0,0,'Song',30,textcenter=True,col=(62,63,75)),
                  ui.maketext(0,0,'Album',30,textcenter=True,col=(62,63,75)),
                  ui.maketext(0,0,'Length',30,textcenter=True,col=(62,63,75)),'']
        wid = int((screenw-315-12)/3)
        ui.maketable(160,100,[],titles,ID='playlist',boxwidth=[70,wid,wid,wid,70],boxheight=[40],backingdraw=True,textsize=20,verticalspacing=4,textcenter=False,col=(62,63,75),scalesize=False,scalex=False,scaley=False,roundedcorners=4,clickablerect=pygame.Rect(160,100,4000,screenh-193),guessheight=70)
        self.refreshsongtable(False,False)
        ui.makerect(156,0,3000,100,col=(62,63,75),scalesize=False,scalex=False,scaley=False,layer=2,ID='title backing')
        ui.maketext(0,0,self.playlists[self.activeplaylist][1],80,anchor=('(w-175)/2+160',36),center=True,scalesize=False,scalex=False,scaley=False,ID='playlist name',layer=3,backingcol=(62,63,75))
        ui.maketext(0,65,str(len(self.playlists[self.activeplaylist][0]))+' songs',30,anchor=('(w-175)/2+160',0),center=True,centery=False,scalesize=False,scalex=False,scaley=False,ID='playlist info',layer=3,backingcol=(62,63,75))
        ui.makescroller(0,0,screenh-193,self.shiftsongtable,maxp=ui.IDs['playlist'].height,pageheight=screenh-200,anchor=('w',100),objanchor=('w',0),ID='scroller',scalesize=False,scalex=False,scaley=False,runcommandat=1)
            
        ## side bar
        ui.makerect(150,0,4,1000,layer=2,scalesize=False,scalex=False,scaley=False,ID='playlists spliter')
        ui.maketext(75,30,'Playlists',40,center=True,scalesize=False,scalex=False,scaley=False,backingcol=(62,63,75))
        ui.makebutton(12,50,'+',55,roundedcorners=30,width=35,height=35,textoffsety=-3,scalesize=False,scalex=False,scaley=False,command=self.makeplaylist,clickdownsize=2)
        ui.makebutton(50,50,'Import',32,roundedcorners=30,height=35,scalesize=False,scalex=False,scaley=False,command=self.importplaylist,clickdownsize=2)
        ui.maketable(5,95,[['']],roundedcorners=4,textsize=20,boxwidth=140,scalesize=False,scalex=False,scaley=False,verticalspacing=3,ID='playlist table')
        self.refreshplaylisttable()
        
        ## control menu
        ui.makewindowedmenu(0,0,100,275,'control','main',col=(52,53,65),scalesize=False,scalex=False,scaley=False,roundedcorners=10,ID='controlmenu')
        ui.makebutton(5,5,'Play',30,col=(62,63,75),textcol=(240,240,240),roundedcorners=8,width=90,height=40,menu='control',command=self.playselected,scalesize=False,scalex=False,scaley=False)
        ui.makebutton(5,50,'Queue',30,col=(62,63,75),textcol=(240,240,240),roundedcorners=8,width=90,height=40,menu='control',command=self.queueselected,scalesize=False,scalex=False,scaley=False)
        ui.makebutton(5,95,'Info',30,col=(62,63,75),textcol=(240,240,240),roundedcorners=8,width=90,height=40,menu='control',command=self.infomenu,scalesize=False,scalex=False,scaley=False)
        ui.makebutton(5,140,'Add',30,col=(62,63,75),textcol=(240,240,240),roundedcorners=8,width=90,height=40,menu='control',command=self.addmenu,scalesize=False,scalex=False,scaley=False)
        ui.makebutton(5,185,'Remove',30,col=(62,63,75),textcol=(240,240,240),roundedcorners=8,width=90,height=40,menu='control',command=self.removesong,scalesize=False,scalex=False,scaley=False)
        ui.makebutton(5,230,'Download',25,col=(62,63,75),textcol=(240,240,240),roundedcorners=8,width=90,height=40,menu='control',command=self.downloadsong,scalesize=False,scalex=False,scaley=False)

        ## add menu
        ui.makewindowedmenu(160,20,200,255,'add menu','main',col=(52,53,65),scalesize=False,scalex=False,scaley=False,roundedcorners=10,colorkey=(2,2,2),ID='add menu')
        ui.maketable(5,5,[],['Playlist'],menu='add menu',roundedcorners=4,boxwidth=190,textsize=30,scalesize=False,scalex=False,scaley=False,verticalspacing=3,col=(62,63,75),ID='playlist add')
        
        ## info editor
        ui.makewindowedmenu(160,20,600,305,'song info','main',col=(52,53,65),scalesize=False,scalex=False,scaley=False,roundedcorners=10,colorkey=(2,2,2))
        ui.maketable(5,5,[['Name',ui.maketextbox(0,0,'',400,10,height=50,roundedcorners=2,textsize=30,col=(62,63,75),ID='inputinfo name',linelimit=10)],
                          ['Artist',ui.maketextbox(0,0,'',400,10,height=50,roundedcorners=2,textsize=30,col=(62,63,75),ID='inputinfo artist',linelimit=10)],
                          ['Album',ui.maketextbox(0,0,'',400,10,height=50,roundedcorners=2,textsize=30,col=(62,63,75),ID='inputinfo album',linelimit=10)],
                          ['Image',ui.maketextbox(0,0,'',400,10,height=50,roundedcorners=2,textsize=30,col=(62,63,75),ID='inputinfo image',linelimit=10)],
                          ['Mp3',ui.maketextbox(0,0,'',400,10,height=50,roundedcorners=2,textsize=30,col=(62,63,75),ID='inputinfo mp3',linelimit=10)]],boxwidth=[-1,504],boxheight=50,menu='song info',roundedcorners=4,textsize=30,scalesize=False,scalex=False,scaley=False,verticalspacing=3,col=(62,63,75))
        ui.makebutton(300,270,'Save',30,self.saveinfo,'song info',roundedcorners=8,spacing=2,horizontalspacing=14,center=True,centery=False,clickdownsize=2,scalesize=False,scalex=False,scaley=False)
        ui.makebutton(543,270,'Delete',30,self.deldat,'song info',roundedcorners=8,spacing=2,horizontalspacing=14,center=True,centery=False,clickdownsize=2,scalesize=False,scalex=False,scaley=False,col=(180,60,60))
        self.refreshsongdisplays()

        ## playlist editor
        ui.makebutton(0,0,'{pencil}',25,self.plsteditmenu,anchor=('w-5',5),objanchor=('w',0),roundedcorners=10,width=40,height=40,textoffsety=-1,scalesize=False,scalex=False,scaley=False,layer=3,clickdownsize=2)
        ui.makewindowedmenu(160,10,600,99,'plstedit menu','main',col=(52,53,65),scalesize=False,scalex=False,scaley=False,roundedcorners=10,colorkey=(2,2,2),ID='plstedit menu')
        ui.maketable(5,5,[['Name',ui.maketextbox(0,0,'',400,10,height=50,roundedcorners=2,textsize=30,col=(62,63,75),ID='inputinfo plstname',linelimit=10,verticalspacing=2,command=self.saveplstinfo,commandifenter=True)]],menu='plstedit menu',roundedcorners=4,boxwidth=[84,500],boxheight=50,textsize=30,scalesize=False,scalex=False,scaley=False,verticalspacing=3,col=(62,63,75),ID='plstedit table')
        ui.makebutton(300,64,'Save',30,self.saveplstinfo,'plstedit menu',roundedcorners=8,spacing=2,horizontalspacing=14,center=True,centery=False,clickdownsize=2,scalesize=False,scalex=False,scaley=False)
        ui.makebutton(595,94,'Delete',30,self.deleteplst,'plstedit menu',roundedcorners=8,spacing=2,horizontalspacing=14,objanchor=('w','h'),clickdownsize=2,scalesize=False,scalex=False,scaley=False,col=(180,60,60))
        
        ## downloading playlist
        ui.makebutton(159,5,'{arrow stick=0.4 point=0.2 down}',30,command=self.downloadplaylist,layer=3,roundedcorners=10,spacing=5,clickdownsize=2,width=40,height=40,textoffsetx=1,scalesize=False)
        ui.makewindowedmenu(160,10,300,140,'download playlist','main',(63,64,75),roundedcorners=10,colorkey=(0,0,0),scalesize=False)
        ui.maketext(150,10,'Auto Download',35,'download playlist',objanchor=('w/2',0),backingcol=(63,64,75),textcenter=True,scalesize=False)
        ui.maketext(150,40,'x Songs from playlist?',35,'download playlist',ID='download playlist text',objanchor=('w/2',0),backingcol=(63,64,75),textcenter=True,scalesize=False)
        ui.makebutton(150,80,'Download',40,self.fullautodownload,'download playlist',ID='download playlist button',objanchor=('w/2',0),roundedcorners=5,verticalspacing=5,scalesize=False)
        


        ## download new
        ui.makebutton(204,5,'{search}',24,command=self.downloadnew,layer=3,roundedcorners=10,spacing=5,clickdownsize=2,width=40,height=40,textoffsetx=1,scalesize=False)
        ui.makewindowedmenu(0,0,600,519,'download new','main',(63,64,75),anchor=('w/2','h/2'),objanchor=('w/2','h/2'),roundedcorners=10,colorkey=(11,183,2),scalesize=False)
        ui.maketext(13,26,'Search',30,'download new',scalesize=False,layer=4,objanchor=(0,'h/2'),backingcol=(43,44,55))
        ui.makebutton(-46,25,'{search}',18,menu='download new',scalesize=False,objanchor=(0,'h/2'),anchor=('580',0),layer=4,spacing=2,clickdownsize=1,roundedcorners=9,col=(63,64,75),borderdraw=False,hovercol=(59,60,71),command=self.searchyoutube)
        ui.makebutton(-20,25,'{cross}',16,menu='download new',scalesize=False,objanchor=(0,'h/2'),anchor=('580',0),layer=4,spacing=2,clickdownsize=1,roundedcorners=9,col=(63,64,75),borderdraw=False,hovercol=(59,60,71),width=30,height=30,textoffsetx=1,textoffsety=1)
        ui.maketextbox(10,10,'',580,menu='download new',commandifenter=True,height=30,scalesize=False,textsize=28,verticalspacing=2,roundedcorners=5,col=(63,64,75),layer=3,borderdraw=True,leftborder=80,rightborder=56,command=self.searchyoutube,ID='search bar')
        ui.maketable(10,50,[],['Image','Title',''],'download new',roundedcorners=5,verticalspacing=3,col=(6,64,75),boxwidth=[110,362,100],boxheight=[25],textsize=25,scalesize=False,ID='search table',guessheight=84)
        
  
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
    def playselected(self,selected=''):
        self.playingplaylist = self.activeplaylist
        ui.IDs['playpause button'].toggle = True
        if selected=='':
            ui.menuback()
            selected = self.selected
        self.activesong = selected
        self.generatequeue()
        self.nextsong()
        self.playpause()
    def queueselected(self):
        self.queue.insert(0,self.selected)
        self.refreshqueue()
        ui.menuback()
    def refreshqueue(self):
        if self.activeplaylist == 1:
            self.refreshsongtable()
    def shiftsongtable(self):
        ui.IDs['playlist'].y = 100-ui.IDs['scroller'].scroll
        ui.IDs['playlist'].refreshcords(ui)
    def refreshsongtable(self,thread=True,scroller=True):
        self.awaitingthreads['songs refresh'] = [False,pyui.emptyfunction]
        if thread:
            thread = threading.Thread(target=lambda: self.refreshsongtable2(scroller))
            thread.start()
        else:
            self.refreshsongtable2(scroller)
    def refreshsongtable2(self,scroller):
        tempqueue = []
        count = 0
        while len(tempqueue)<30 and count != len(self.queue):
            if self.songdata[self.allsongs.index(self.queue[count])]['downloaded']:
                tempqueue.append(self.queue[count])
            count+=1
        self.playlists[1] = [tempqueue,self.playlists[1][1]]
        self.playlists[2] = [self.songhistory[:30],self.playlists[2][1]]
        ui.IDs['playlist'].disable()
        ui.IDs['playlist'].wipe(ui,False)
        data = []
        for a in self.playlists[self.activeplaylist][0]:
            if os.path.isfile(a):
                func = funcercm(a,self)
                obj = ui.makebutton(-100,-100,'{dots}',20,command=func.func,col=(62,63,75),clickdownsize=1,roundedcorners=4,enabled=False)
                dat = self.songdata[self.allsongs.index(a)]
                func = funcerps(a,self)
                if dat['image_path'] == 'none':
                    if dat['downloaded']: img = ui.makebutton(-100,-100,'',37,command=func.func,col=(62,63,75),img=logo,roundedcorners=4,scalesize=False,enabled=False,border=1,hovercol=pyui.shiftcolor((72,63,75),-5),colorkey=(0,0,0),verticalspacing=3)
                    else: img = ui.maketext(-100,-100,'-',20,col=(62,63,75),roundedcorners=4,textcenter=True,scalesize=False,enabled=False)
                else:
                    image = pygame.image.load(dat['image_path'])
                    if image.get_width()/image.get_height()>1.1: txtsize = 48
                    else: txtsize = 64
                    if dat['downloaded']: img = ui.makebutton(-100,-100,'',txtsize,command=func.func,img=image,col=(62,63,75),roundedcorners=4,scalesize=False,enabled=False,verticalspacing=3,border=1)
                    else: img = ui.maketext(-100,-100,'',txtsize,img=image,col=(62,63,75),roundedcorners=4,textcenter=True,scalesize=False,enabled=False)
                data.append([img,dat['name']+'\n{"- '+dat['artist']+'" (150,150,160)}',dat['album'],sectostr(float(dat['length'])),obj])
        ui.IDs['playlist'].data = data
        ui.IDs['playlist'].refresh(ui)
        if scroller:
            ui.IDs['scroller'].scroller = 0
            ui.IDs['scroller'].maxp = ui.IDs['playlist'].height
            ui.IDs['scroller'].refresh(ui)
            self.shiftsongtable()
        self.awaitingthreads['songs refresh'][0] = True
    def refreshplaylisttable(self):
        ui.IDs['playlist table'].wipe(ui)
        data = []
        for a in self.playlists:
            name = a[1].removesuffix('.plst')
            if name[len(name)-5:] != '%del%':
                func = funcerpl(self.playlists.index(a),self)
                data.append([ui.makebutton(0,0,a[1],25,clickdownsize=1,roundedcorners=4,verticalspacing=4,command=func.func,maxwidth=130)])
        ui.IDs['playlist table'].data = data
        ui.IDs['playlist table'].refresh(ui)
        ui.IDs['playlist table'].refreshcords(ui)
    def importplaylist(self):
        ID = 'import playlist'
        if not (ID in self.awaitingthreads):
            self.thread = threading.Thread(target=lambda: self.getinput(ID))
            self.input = []
            self.awaitingthreads[ID] = [False,self.importplaylist2]
            self.thread.start()
    def importplaylist2(self):
        self.awaitinginput = False
        link = self.input
        pl = spotifyplaylistpull(link)
        if pl != 0:
            self.loadmusic()
            self.playlists.append(pl)
            makeplst(pl)
            self.moveplaylist(len(self.playlists)-1)
            self.refreshplaylisttable()
    def getinput(self,ID):
        self.input = input('Enter your spotify link: ')
        self.awaitingthreads[ID][0] = True
    def makeplaylist(self):
        self.playlists.append([[],'New Playlist '+str(len(self.playlists)+1)])
        makeplst([[],'New Playlist '+str(len(self.playlists))])
        self.moveplaylist(len(self.playlists)-1)
        self.refreshplaylisttable()
    def moveplaylist(self,playlist):
        if not ('songs refresh' in self.awaitingthreads):
            ui.IDs['scroller'].scroll = 0
            self.shiftsongtable()
            self.activeplaylist = playlist
            self.refreshsongtable(scroller=True)
            self.refreshplaylistdisplay()
    def refreshplaylistdisplay(self):
        ui.IDs['playlist name'].text = self.playlists[self.activeplaylist][1]
        ui.IDs['playlist name'].refresh(ui)
        ui.IDs['playlist name'].resetcords(ui)
        ui.IDs['playlist info'].text = str(len(self.playlists[self.activeplaylist][0]))+' songs'
        ui.IDs['playlist info'].refresh(ui)
        ui.IDs['playlist info'].resetcords(ui)
    def addtoplaylist(self,playlist):
        self.playlists[[a[1] for a in self.playlists].index(playlist)][0].append(self.selected)
        makeplst(self.playlists[[a[1] for a in self.playlists].index(playlist)])
        ui.menuback()
    def removesong(self):
        ui.menuback()
        if self.activeplaylist != 0:
            self.playlists[self.activeplaylist][0].remove(self.selected)
            makeplst(self.playlists[self.activeplaylist])
            self.refreshsongtable()
    def controlmenu(self,song):
        self.selected = song
        mpos = pygame.mouse.get_pos()
        if screenw-mpos[0]<ui.IDs['controlmenu'].width: wid = ui.IDs['controlmenu'].width
        else: wid = 0
        if screenh-mpos[1]-100<ui.IDs['controlmenu'].height: hei = ui.IDs['controlmenu'].height
        else: hei = 0
        ui.IDs['controlmenu'].smartcords(mpos[0]-wid,mpos[1]-hei)
        ui.movemenu('control','down')
    def infomenu(self):
        dat = self.songdata[self.allsongs.index(self.selected)]
        ui.IDs['inputinfo name'].text = dat['name']
        ui.IDs['inputinfo artist'].text = dat['artist']
        ui.IDs['inputinfo album'].text = dat['album']
        ui.IDs['inputinfo image'].text = dat['image_path']
        ui.IDs['inputinfo mp3'].text = dat['mp3_path']
        ui.IDs['inputinfo name'].refresh(ui)
        ui.IDs['inputinfo artist'].refresh(ui)
        ui.IDs['inputinfo album'].refresh(ui)
        ui.IDs['inputinfo image'].refresh(ui)
        ui.IDs['inputinfo mp3'].refresh(ui)
        ui.movemenu('song info','down')
    def addmenu(self,download=False):
        data = []
        for a in range(3,len(self.playlists)):
            if self.playlists[a][1][len(self.playlists[a][1]-5):] != '%del%':
                func = funceram(self.playlists[a][1],self)
                data.append([ui.makebutton(0,0,self.playlists[a][1],25,clickdownsize=1,roundedcorners=4,verticalspacing=4,command=func.func)])
        ui.IDs['playlist add'].data = data
        ui.IDs['playlist add'].refresh(ui)
        ui.IDs['playlist add'].refreshcords(ui)
        ui.IDs['add menu'].height = ui.IDs['playlist add'].height+10
        ui.movemenu('add menu','down')
    def plsteditmenu(self):
        if self.activeplaylist>2:
            ui.IDs['inputinfo plstname'].text = self.playlists[self.activeplaylist][1]
            ui.IDs['inputinfo plstname'].refresh(ui)
            ui.movemenu('plstedit menu','down')
    def deleteplst(self):
        ui.IDs['inputinfo plstname'].text = self.playlists[self.activeplaylist][1]+'%del%'
        self.saveplstinfo()
        self.moveplaylist(0)
    def saveplstinfo(self):
        name = ui.IDs['inputinfo plstname'].text
        old = self.playlists[self.activeplaylist][1]
        self.playlists[self.activeplaylist][1] = name
        os.remove(f'data\\playlists\\{makefileable(old)}.plst')
        makeplst(self.playlists[self.activeplaylist])
        self.refreshplaylisttable()
        self.refreshplaylistdisplay()
        ui.menuback()
    def saveinfo(self):
        name = ui.IDs['inputinfo name'].text
        artist = ui.IDs['inputinfo artist'].text
        album = ui.IDs['inputinfo album'].text
        image = ui.IDs['inputinfo image'].text
        mp3 = ui.IDs['inputinfo mp3'].text
        if len(image.split('\\')) == 1 and (image!='none' and image!=''):
            image = pyui.resourcepath(f'data\\images\\{image}')
        if image == '': image = 'none'
        if len(mp3.split('\\')) == 1:
            mp3 = pyui.resourcepath(f'data\\mp3s\\{mp3}')
        self.songdata[self.allsongs.index(self.selected)]['name'] = name
        self.songdata[self.allsongs.index(self.selected)]['artist'] = artist
        self.songdata[self.allsongs.index(self.selected)]['album'] = album
        if os.path.isfile(image) or image == 'none':
            self.songdata[self.allsongs.index(self.selected)]['image_path'] = image
        if os.path.isfile(mp3):
            self.songdata[self.allsongs.index(self.selected)]['mp3_path'] = mp3
            self.songdata[self.allsongs.index(self.selected)]['downloaded'] = True
        length = self.songdata[self.allsongs.index(self.selected)]['length']
        info = self.songdata[self.allsongs.index(self.selected)]
        info['dat_path'] = self.selected
        makedat(info,True)
        self.refreshsongtable()
        ui.menuback()
    def deldat(self):
        ui.menuback()
        os.remove(self.selected)
        self.songdata.remove(self.songdata[self.allsongs.index(self.selected)])
        self.allsongs.remove(self.selected)
        self.loadmusic()
        self.refreshsongtable()
    def downloadsong(self):
        info = self.songdata[self.allsongs.index(self.selected)]
        ui.movemenu('download new','down')
        ui.IDs['search bar'].text = asciify(info['name']+' - '+info['artist'])
        ui.IDs['search bar'].refresh(ui)
        self.searchyoutube()
    def downloadplaylist(self):
        count = len([1 for a in self.playlists[self.activeplaylist][0] if not self.songdata[self.allsongs.index(a)]['downloaded']])
        ui.IDs['download playlist text'].text = f'{count} Songs from playlist?'
        ui.IDs['download playlist text'].refresh(ui)
        ui.movemenu('download playlist','down')
    def downloadnew(self):
        ui.movemenu('download new','down')
    def searchyoutube(self):
        if not('youtube search' in self.awaitingthreads):
            self.awaitingthreads['youtube search'] = [False,pyui.emptyfunction]
            thread = threading.Thread(target=self.searchyoutube2)
            thread.start()
    def searchyoutube2(self):
        term = ui.IDs['search bar'].text.replace(' ','+')
        html = urllib.request.urlopen(f'https://www.youtube.com/results?search_query="{term}"')
        links = re.findall(r'watch\?v=(\S{11})',html.read().decode())
        rem = []
        for a in range(len(links)):
            if links[a] in links[:max(a,0)]:
                rem.append(links[a])
        for b in rem:
            links.remove(b)
        ui.IDs['search table'].wipe(ui)
        data = []
        a = 0
        while len(data)<min(5,len(links)):
            dat = BeautifulSoup(requests.get(f'https://www.youtube.com/watch?v={links[a]}').text,'html.parser')
            title = str(dat.find_all(name='title')[0]).replace('<title>','').replace('</title>','').removesuffix(' - YouTube')
            if not('#' in title):
                func = funceryt(f'https://www.youtube.com/watch?v={links[a]}',title,music)
                obj = ui.makebutton(-100,-100,'Download',25,func.func,roundedcorners=5,col=(6,64,75),enabled=False,clickdownsize=2)
                thumbnail = 'thumbnail'+str(random.randint(0,100000000))
                loadimage(f'http://img.youtube.com/vi/{links[a]}/0.jpg',thumbnail,True)
                textobj = ui.maketext(-100,-100,'',78,img=pygame.image.load(pyui.resourcepath(f'data\\thumbnails\\{thumbnail}.png')),backingcol=(6,64,75))
                data.append([textobj,title,obj])
                ui.IDs['search table'].data = data
                ui.IDs['search table'].threadrefresh(ui)
            a+=1        
        self.awaitingthreads['youtube search'][0] = True
    def downloadyoutube(self,url,name):
        if not('download youtube' in self.awaitingthreads):
            self.awaitingthreads['download youtube'] = [False,pyui.emptyfunction]
            thread = threading.Thread(target=downloadyoutube(url,name,self))
            thread.start()

    def fullautodownload(self):
        if not('fullautodownload' in self.awaitingthreads):
            download = [self.songdata[self.allsongs.index(a)] for a in self.playlists[self.activeplaylist][0] if not self.songdata[self.allsongs.index(a)]['downloaded']]
            self.awaitingthreads['fullautodownload'] = [False,pyui.emptyfunction]
            thread = threading.Thread(target=fullautodownload(download))
            thread.start()
     
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
            ui.IDs['playlists spliter'].height = screenh
            ui.IDs['title backing'].width = screenw
            ui.IDs['song duration'].width = event.w*music.songbarwidth
            ui.IDs['song duration'].resetcords(ui)
            ui.IDs['scroller'].height = screenh-193
            ui.IDs['scroller'].pageheight = screenh-200
            ui.IDs['scroller'].refresh(ui)
            wid = int((screenw-315-12)/3)
            ui.IDs['playlist'].boxwidth = [70,wid,wid,wid,70]
            ui.IDs['playlist'].clickablerect = pygame.Rect(160,100,4000,screenh-193)
            ui.IDs['playlist'].refresh(ui)
            ui.IDs['playlist'].refreshcords(ui)
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
