import pygame,math,random,sys,os
import PyUI as pyui
pygame.init()
screenw = 1200
screenh = 900
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
pygame.scrap.init()
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
ui.defaultcol = (16,163,127)
ui.defaulttextcol = (255,255,255)


ui.makerect(0,0,screenw,93,col=(32,33,35),anchor=(0,'h-93'),layer=0,scalesize=False,ID='controlbar')
ui.makebutton(0,0,'{play rounded=0.05}',30,anchor=('w/2','h-60'),toggletext='{pause rounded=0.1}',toggleable=True,togglecol=(16,163,127),center=True,width=49,height=49,roundedcorners=100,scalesize=False,clickdownsize=2)
ui.makebutton(0,0,'{skip rounded=0.05 left}',22,anchor=('w/2-55','h-60'),center=True,width=45,height=45,roundedcorners=100,scalesize=False,clickdownsize=2)
ui.makebutton(0,0,'{skip rounded=0.05}',22,anchor=('w/2+55','h-60'),center=True,width=45,height=45,roundedcorners=100,scalesize=False,clickdownsize=2)

ui.makeslider(0,0,200,12,anchor=('w/2','h-19'),center=True,border=1,roundedcorners=4,button=ui.makebutton(0,0,'',width=20,height=20,border=1,clickdownsize=1,roundedcorners=4,borderdraw=False,backingdraw=False))



v = 0

while not done:
    pygameeventget = ui.loadtickdata()
    for event in pygameeventget:
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.VIDEORESIZE:
            screenw = event.w
            screenh = event.h
            ui.IDs['controlbar'].width = screenw
    screen.fill((62,63,75))
    
    v+=0.1  
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)
pygame.quit() 
