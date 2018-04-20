import pygame
from pygame.locals import *
import math
import random
import os

pygame.init()
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Image Fleet")

bgmap = pygame.Surface((800,600))

#fontを調べる
#fo = pygame.font.get_fonts()
#print(fo)

#takaoフォントなど漢字フォントがあれば漢字の表示もOK
#font = pygame.font.SysFont("takao", 32)
#fontT = pygame.font.SysFont("takao", 46)

font = pygame.font.SysFont("", 32)
fontT = pygame.font.SysFont("", 46)

parhFileNames = []
stellarSystems = []
stellarNo=0

searchPath = ["/home/"]#検索したいpathを設定

cd=[]
ct=[0,0,1,2,3,4,5,0]
un=[]

dx=[[-1,0,-1,1,-1,0],[0,1,-1,1,0,1]]
dy=[-1,-1,0,0,1,1]

class Unit:
    def __init__(self,x,y,c):
        self.x=x
        self.y=y
        self.c=c
        self.hp=1
        self.pos=0
    def setPos(self):
        self.pos=self.y*150+self.x
    def __lt__(self, other):
        return self.pos > other.pos

def locatePrint(x, y, s, t):
    if t==1:
        text = fontT.render(s, True, (100, 70, 10))
    else:
        text = font.render(s, True, (120, 120, 120))
    screen.blit(text, [x * 50, y * 50])

def setUnit(imgData):
    del un[:]
    img=pygame.transform.smoothscale(imgData,(150,100))
    for x in range(150):
        for y in range(100):
            c=img.get_at((x,y))
            rc=getNearColor(c)
            if rc>=1 and rc<=6:
                un.append(Unit(x,y,rc))
    print(len(un))

def unitThink0(u):
    #ランダム
    r=random.randint(0,5)
    h=(u.y%2)
    rx=u.x+dx[h][r]
    ry=u.y+dy[r]
    return rx,ry

def unitThink1(u):
    #なんとなく真ん中
    global gcx,gcy
    bl=20000
    nx=0
    ny=0
    for j in range(2):
        r=random.randint(0,5)
        h=(u.y%2)
        rx=u.x+dx[h][r]
        ry=u.y+dy[r]
        l=abs(gcx-rx)**2+abs(gcy-ry)**2
        if l<bl:
            bl=l
            nx=rx
            ny=ry
    return nx,ny

def unitThink2(u):
    #なんとなく真ん中　攻撃優先
    global gcx,gcy
    bl=20000
    nx=0
    ny=0
    for j in range(3):
        r=random.randint(0,5)
        h=(u.y%2)
        rx=u.x+dx[h][r]
        ry=u.y+dy[r]
        l=abs(gcx-rx)**2+abs(gcy-ry)**2
        c=getColorData(rx,ry)
        if c!=u.c and c>0:l=0
        if l<bl:
            bl=l
            nx=rx
            ny=ry
    return nx,ny

def unitThink3(u):
    #ランダム　攻撃優先
    bl=20000
    nx=0
    ny=0
    for j in range(3):
        r=random.randint(0,5)
        h=(u.y%2)
        rx=u.x+dx[h][r]
        ry=u.y+dy[r]
        l=random.randint(5,15)
        c=getColorData(rx,ry)
        if c!=u.c and c>0:l=0
        if l<bl:
            bl=l
            nx=rx
            ny=ry
    return nx,ny

def unitThink4(u):
    #攻撃優先
    bl=20000
    nx=-1000
    ny=-1000
    for j in range(6):
        h=(u.y%2)
        rx=u.x+dx[h][j]
        ry=u.y+dy[j]
        l=20000
        c=getColorData(rx,ry)
        if c!=u.c and c>0:l=0
        if l<bl:
            bl=l
            nx=rx
            ny=ry
    return nx,ny

def unitThink5(u):
    #なんとなく真ん中２　攻撃優先
    global gcx,gcy
    bl=20000
    nx=u.x
    ny=u.y
    for j in range(4):
        r=random.randint(0,5)
        h=(u.y%2)
        rx=u.x+dx[h][r]
        ry=u.y+dy[r]
        l=abs(gcx-rx)**2+abs(gcy-ry)**2
        c=getColorData(rx,ry)
        if c==u.c:
            l=20001
        elif c!=u.c and c>0:l=0
        if l<bl:
            bl=l
            nx=rx
            ny=ry
    return nx,ny

def think(u):
    if ct[u.c]==0:return unitThink0(u)
    if ct[u.c]==1:return unitThink1(u)
    if ct[u.c]==2:return unitThink2(u)
    if ct[u.c]==3:return unitThink3(u)
    if ct[u.c]==4:return unitThink4(u)
    if ct[u.c]==5:return unitThink5(u)
    return -1,-1

def moveUnit():
    for i in range(len(un)):
        nx,ny=think(un[i])
        if nx>=0 and nx<=150 and ny>=0 and ny<=100:
            if getColorData(nx,ny)==0:
                un[i].x=nx
                un[i].y=ny
            if getColorData(nx,ny)!=un[i].c:
                chengeUnit(nx,ny,un[i].c)

def printscore(tn):
    global stellarNo
    score=[0,0,0,0,0,0]
    for i in range(1,len(un)-1):
        score[un[i].c-1]+=1
    locatePrint(6, 0, "Image Fleet",1)
    locatePrint(2, 1, "StellarSystem  "+stellarSystems[stellarNo].replace('.jpg', ' age')+" "+str(tn),0)
    for i in range(1,7):
        box = pygame.Surface((20,10))
        box.fill(cd[i])
        screen.blit(box,(100*i,520),(0,0, 20, 10))
        locatePrint(i*2, 11, str(score[i-1]),0)

def chengeUnit(x,y,c):
    pos=x+y*150
    index = [i for i, u in enumerate(un) if u.pos == pos]
    if random.randint(0,1)==1:
        if len(index)>0:un[index[0]].c=c
    else:
        if len(index)>0:un[index[0]].hp=0

def getColorData(x,y):
    return getNearColor(screen.get_at((x*4+100+(y%2)*2,y*4+100)))

def unitDraw():
    for i in range(len(un)):
        screen.set_at((un[i].x*4+100+(un[i].y%2)*2,un[i].y*4+100),cd[un[i].c])

def unitPos():
    for i in range(len(un)):
        un[i].setPos()

def unitRelease():
    t=len(un)-1
    for i in range(len(un)):
        if un[t-i].hp==0:
            del un[t-i]

def setColorData():
    for b in range(2):
        for g in range(2):
            for r in range(2):
                cd.append(pygame.Color(r*255,g*255,b*255,255))

def getNearColor(c):
    bs=600
    bi=-1
    for i in range(len(cd)):
        s=abs(c.r-cd[i].r)+abs(c.g-cd[i].g)+abs(c.b-cd[i].b)
        if s<bs:
            bs=s
            bi=i
    return bi

def fileSearch():
    esw=0
    while len(searchPath)>0 and esw==0:
        try:
            ld = os.listdir(searchPath[0])
        except:
            del searchPath[0]
            continue
        for i in range(len(ld)):
            fileName=searchPath[0] + ld[i]
            if os.path.isdir(fileName):
                searchPath.append(fileName+"/")
            elif (fileName+" ").count(".jpg ")>0:
                parhFileNames.append(fileName)
                stellarSystems.append(ld[i])
                if len(parhFileNames)%1000==0:
                    print(len(parhFileNames))
                if len(parhFileNames)>5000:esw=1
        del searchPath[0]

def bgSet():
    global stellarNo
    for i in range(5):
        r=random.randint(0,len(parhFileNames)-1)
        try:
            setUnit(pygame.image.load(parhFileNames[r]))
            stellarNo=r
            print(parhFileNames[r])
            break
        except:
            print("error file="+parhFileNames[r])
            continue

def main():
    global gcx,gcy
    pygame.mixer.music.load('Bolero1930boston.mp3')
    pygame.mixer.music.play(-1)
    end_game = False
    bgSet()
    screen.fill((0,0,0))
    unitDraw()
    tn=0
    while not end_game:
        gcx=75+50*math.cos(tn/100)
        gcy=50+30*math.sin(tn/100)
        unitPos()
        un.sort()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:end_game = True
            if event.type == MOUSEBUTTONDOWN:
                bgSet()
                tn=0
                screen.fill((0,0,0))
                unitDraw()
                continue
        moveUnit()
        unitRelease()
        screen.fill((0,0,0))
        printscore(tn)
        unitDraw()
        pygame.display.flip()
        pygame.time.delay(10)
        tn+=1
    pygame.quit()
    quit()

fileSearch()
setColorData()
main()
