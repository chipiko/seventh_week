import pygame, sys, random, math

pygame.init()

WIDTH, HEIGHT = 960, 540
FPS = 60
TILE = 48

GRAVITY = 0.8
FRICTION = -0.12
ACC = 0.8
JUMP = -16

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer V5 - Boss Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)
big_font = pygame.font.SysFont("consolas", 48)

WHITE=(240,240,240)
GRAY=(120,120,120)
BLUE=(80,130,255)
RED=(220,60,60)
GREEN=(60,220,120)
BLACK=(20,20,20)
PURPLE=(170,80,200)
ORANGE=(255,140,0)

# ---------------- GAME STATES ----------------
MENU=0
PLAYING=1
PAUSED=2
GAMEOVER=3
VICTORY=4

game_state=MENU

# ---------------- GROUPS ----------------
platforms=pygame.sprite.Group()
enemies=pygame.sprite.Group()
projectiles=pygame.sprite.Group()
all_sprites=pygame.sprite.Group()

# ---------------- CAMERA ----------------
class Camera:
    def __init__(self):
        self.offset=pygame.Vector2(0,0)

    def update(self,target):
        target_offset=pygame.Vector2(
            target.rect.centerx-WIDTH//2,
            target.rect.centery-HEIGHT//2
        )
        self.offset += (target_offset-self.offset)*0.1

camera=Camera()

# ---------------- TILE ----------------
class Tile(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image=pygame.Surface((TILE,TILE))
        self.image.fill(GRAY)
        self.rect=self.image.get_rect(topleft=(x,y))

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
        self.hp=10
        self.facing=1
        self.on_ground=False
        self.attack_cd=0
        self.invincible=0

    def input(self):
        k=pygame.key.get_pressed()
        self.acc.x=0
        if k[pygame.K_a]:
            self.acc.x=-ACC; self.facing=-1
        if k[pygame.K_d]:
            self.acc.x=ACC; self.facing=1

    def jump(self):
        if self.on_ground:
            self.vel.y=JUMP

    def attack(self):
        if self.attack_cd==0:
            hitbox=pygame.Rect(
                self.rect.centerx+30*self.facing,
                self.rect.centery-20,50,40)
            for e in enemies:
                if hitbox.colliderect(e.rect):
                    e.hp-=1
            self.attack_cd=20

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

        if self.attack_cd>0:self.attack_cd-=1
        if self.invincible>0:self.invincible-=1

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

# ---------------- BOSS ----------------
class Boss(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image=pygame.Surface((80,80))
        self.image.fill(ORANGE)
        self.rect=self.image.get_rect(midbottom=(x,y))
        self.hp=30
        self.shoot_timer=0

    def update(self):
        if self.shoot_timer<=0:
            projectile=Projectile(self.rect.centerx,self.rect.centery)
            projectiles.add(projectile)
            all_sprites.add(projectile)
            self.shoot_timer=60 if self.hp>15 else 30
        else:
            self.shoot_timer-=1

# ---------------- PROJECTILE ----------------
class Projectile(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image=pygame.Surface((12,12))
        self.image.fill(PURPLE)
        self.rect=self.image.get_rect(center=(x,y))
        angle=math.atan2(player.rect.centery-y,player.rect.centerx-x)
        self.vel=pygame.Vector2(math.cos(angle)*6,math.sin(angle)*6)

    def update(self):
        self.rect.x+=self.vel.x
        self.rect.y+=self.vel.y
        if pygame.sprite.collide_rect(self,player) and player.invincible==0:
            player.hp-=1
            player.invincible=60
            self.kill()

# ---------------- LOAD ----------------
def load_game():
    platforms.empty(); enemies.empty(); projectiles.empty(); all_sprites.empty()
    for i in range(20):
        tile=Tile(i*TILE,HEIGHT-48)
        platforms.add(tile); all_sprites.add(tile)

    global player,boss
    player=Player(200,300)
    boss=Boss(700,HEIGHT-48)

    enemies.add(boss)
    all_sprites.add(player,boss)

# ---------------- INIT ----------------
load_game()

# ---------------- LOOP ----------------
while True:
    clock.tick(FPS)

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type==pygame.KEYDOWN:
            if game_state==MENU:
                game_state=PLAYING
            elif game_state==PLAYING:
                if e.key==pygame.K_SPACE: player.jump()
                if e.key==pygame.K_e: player.attack()
                if e.key==pygame.K_ESCAPE: game_state=PAUSED
            elif game_state==PAUSED:
                if e.key==pygame.K_ESCAPE: game_state=PLAYING
            elif game_state in (GAMEOVER,VICTORY):
                if e.key==pygame.K_r:
                    load_game()
                    game_state=PLAYING

    if game_state==PLAYING:
        player.update()
        boss.update()
        projectiles.update()
        camera.update(player)

        if boss.hp<=0:
            game_state=VICTORY

        if player.hp<=0:
            game_state=GAMEOVER

    screen.fill(WHITE)

    if game_state==MENU:
        screen.blit(big_font.render("PRESS ANY KEY TO START",True,BLACK),(200,250))
    elif game_state in (PLAYING,PAUSED,GAMEOVER,VICTORY):
        for s in all_sprites:
            screen.blit(s.image,s.rect.topleft-camera.offset)

        for p in projectiles:
            screen.blit(p.image,p.rect.topleft-camera.offset)

        ui=font.render(f"HP:{player.hp}   Boss HP:{boss.hp}",True,BLACK)
        screen.blit(ui,(20,20))

        if game_state==PAUSED:
            screen.blit(big_font.render("PAUSED",True,BLACK),(380,200))
        if game_state==GAMEOVER:
            screen.blit(big_font.render("GAME OVER - R",True,RED),(250,250))
        if game_state==VICTORY:
            screen.blit(big_font.render("YOU WIN! - R",True,GREEN),(280,250))

    pygame.display.flip()
