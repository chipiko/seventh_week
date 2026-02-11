import pygame, sys, random

pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 960, 540
FPS = 60
TILE = 48

GRAVITY = 0.8
FRICTION = -0.12
ACC = 0.8
JUMP = -16

# ---------------- WINDOW ----------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer V4")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)

# ---------------- COLORS ----------------
WHITE=(240,240,240)
GRAY=(130,130,130)
BLUE=(80,130,255)
RED=(220,60,60)
GREEN=(60,220,120)
YELLOW=(240,220,70)
PURPLE=(170,80,200)
BLACK=(20,20,20)
CYAN=(60,240,240)

# ---------------- LEVEL ----------------
level_map = [
"................................",
".................P..............",
".............C.................",
"..............E.................",
".........#####..................",
"............................S...",
"......C.........................",
"...........#####................",
"............................E...",
"...............................",
"...............#####...........",
"################################",
]

# ---------------- GROUPS ----------------
platforms=pygame.sprite.Group()
enemies=pygame.sprite.Group()
coins=pygame.sprite.Group()
spikes=pygame.sprite.Group()
powers=pygame.sprite.Group()
portal_group=pygame.sprite.Group()
all_sprites=pygame.sprite.Group()

# ---------------- CAMERA ----------------
class Camera:
    def __init__(self):
        self.offset=pygame.Vector2(0,0)
        self.shake=0

    def update(self,target):
        target_offset=pygame.Vector2(
            target.rect.centerx-WIDTH//2,
            target.rect.centery-HEIGHT//2
        )
        self.offset += (target_offset-self.offset)*0.1
        if self.shake>0:
            self.offset+=pygame.Vector2(random.randint(-5,5),random.randint(-5,5))
            self.shake-=1

# ---------------- TILE ----------------
class Tile(pygame.sprite.Sprite):
    def __init__(self,x,y,color):
        super().__init__()
        self.image=pygame.Surface((TILE,TILE))
        self.image.fill(color)
        self.rect=self.image.get_rect(topleft=(x,y))

class Spike(Tile):
    def __init__(self,x,y):
        super().__init__(x,y,PURPLE)

class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image=pygame.Surface((20,20))
        self.image.fill(YELLOW)
        self.rect=self.image.get_rect(center=(x,y))

class PowerUp(pygame.sprite.Sprite):
    def __init__(self,x,y,type):
        super().__init__()
        self.type=type
        self.image=pygame.Surface((22,22))
        self.image.fill(CYAN if type=="speed" else GREEN)
        self.rect=self.image.get_rect(center=(x,y))

class Portal(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image=pygame.Surface((40,60))
        self.image.fill(GREEN)
        self.rect=self.image.get_rect(midbottom=(x,y))

# ---------------- PLAYER ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image=pygame.Surface((36,46))
        self.image.fill(BLUE)
        self.rect=self.image.get_rect(midbottom=(x,y))
        self.pos=pygame.Vector2(self.rect.topleft)
        self.vel=pygame.Vector2(0,0)
        self.acc=pygame.Vector2(0,0)

        self.hp=5
        self.max_hp=5
        self.coins=0
        self.kills=0
        self.on_ground=False
        self.facing=1
        self.dash_cd=0
        self.attack_cd=0
        self.invincible=0
        self.speed_boost=0
        self.regen_timer=0

    def input(self):
        k=pygame.key.get_pressed()
        self.acc.x=0
        speed=ACC*2 if self.speed_boost>0 else ACC

        if k[pygame.K_a]:
            self.acc.x=-speed; self.facing=-1
        if k[pygame.K_d]:
            self.acc.x=speed; self.facing=1

    def jump(self):
        if self.on_ground:
            self.vel.y=JUMP

    def dash(self):
        if self.dash_cd==0:
            self.vel.x=20*self.facing
            self.dash_cd=40

    def attack(self):
        if self.attack_cd==0:
            hitbox=pygame.Rect(
                self.rect.centerx+30*self.facing,
                self.rect.centery-20,40,40)
            for e in enemies:
                if hitbox.colliderect(e.rect):
                    e.hp-=1
                    e.rect.x+=20*self.facing
            self.attack_cd=25

    def update(self):
        self.input()
        self.acc.y=GRAVITY
        self.acc.x+=self.vel.x*FRICTION
        self.vel+=self.acc
        self.pos+=self.vel+0.5*self.acc

        self.rect.x=self.pos.x
        self.collide(platforms,'x')
        self.rect.y=self.pos.y
        self.collide(platforms,'y')

        if self.dash_cd>0:self.dash_cd-=1
        if self.attack_cd>0:self.attack_cd-=1
        if self.invincible>0:self.invincible-=1
        if self.speed_boost>0:self.speed_boost-=1

        # regen
        if self.regen_timer>120 and self.hp<self.max_hp:
            self.hp+=1
            self.regen_timer=0
        else:
            self.regen_timer+=1

    def collide(self,group,d):
        for p in pygame.sprite.spritecollide(self,group,False):
            if d=='x':
                if self.vel.x>0:self.rect.right=p.rect.left
                if self.vel.x<0:self.rect.left=p.rect.right
                self.pos.x=self.rect.x; self.vel.x=0
            if d=='y':
                if self.vel.y>0:
                    self.rect.bottom=p.rect.top
                    self.on_ground=True
                if self.vel.y<0:self.rect.top=p.rect.bottom
                self.pos.y=self.rect.y; self.vel.y=0

# ---------------- ENEMY ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image=pygame.Surface((36,36))
        self.image.fill(RED)
        self.rect=self.image.get_rect(midbottom=(x,y))
        self.hp=3
        self.speed=2
        self.start_x=x

    def update(self):
        if abs(player.rect.centerx-self.rect.centerx)<250:
            self.rect.x+=self.speed if player.rect.centerx>self.rect.centerx else -self.speed
        else:
            if abs(self.rect.x-self.start_x)>100:
                self.rect.x-=self.speed if self.rect.x>self.start_x else -self.speed

# ---------------- LOAD ----------------
def load_level():
    platforms.empty(); enemies.empty(); coins.empty()
    spikes.empty(); powers.empty(); portal_group.empty(); all_sprites.empty()
    for r,row in enumerate(level_map):
        for c,t in enumerate(row):
            x,y=c*TILE,r*TILE
            if t=="#":
                tile=Tile(x,y,GRAY); platforms.add(tile); all_sprites.add(tile)
            if t=="E":
                e=Enemy(x+TILE//2,y+TILE); enemies.add(e); all_sprites.add(e)
            if t=="C":
                coin=Coin(x+TILE//2,y+TILE//2); coins.add(coin); all_sprites.add(coin)
            if t=="S":
                s=Spike(x,y); spikes.add(s); all_sprites.add(s)
            if t=="P":
                portal=Portal(x+TILE//2,y+TILE); portal_group.add(portal); all_sprites.add(portal)

    all_sprites.add(player)

# ---------------- INIT ----------------
player=Player(100,200)
camera=Camera()
load_level()

# ---------------- LOOP ----------------
while True:
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type==pygame.QUIT: pygame.quit(); sys.exit()
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_SPACE: player.jump()
            if e.key==pygame.K_LSHIFT: player.dash()
            if e.key==pygame.K_e: player.attack()
            if e.key==pygame.K_r:
                player.__init__(100,200)
                load_level()

    player.update()
    enemies.update()

    # damage
    if pygame.sprite.spritecollide(player,spikes,False) and player.invincible==0:
        player.hp-=1; player.invincible=60; camera.shake=10; player.regen_timer=0

    for en in enemies.copy():
        if en.hp<=0:
            en.kill(); player.kills+=1
        elif pygame.sprite.collide_rect(player,en) and player.invincible==0:
            player.hp-=1; player.invincible=60; camera.shake=10; player.regen_timer=0

    player.coins+=len(pygame.sprite.spritecollide(player,coins,True))

    if pygame.sprite.spritecollide(player,portal_group,False):
        load_level(); player.pos=pygame.Vector2(100,200)

    camera.update(player)

    screen.fill(WHITE)
    for s in all_sprites:
        screen.blit(s.image,s.rect.topleft-camera.offset)

    ui=font.render(f"HP:{player.hp}  Coins:{player.coins}  Kills:{player.kills}",True,BLACK)
    screen.blit(ui,(20,20))

    pygame.display.flip()
