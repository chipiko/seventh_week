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
pygame.display.set_caption("Platformer V3")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)

# ---------------- COLORS ----------------
WHITE = (240,240,240)
GRAY = (130,130,130)
BLUE = (80,130,255)
RED = (220,60,60)
GREEN = (80,220,120)
YELLOW = (240,220,70)
BLACK = (20,20,20)
PURPLE = (180,80,200)

# ---------------- LEVELS ----------------
levels = [
[
"........................",
"..............C.........",
"..............E.........",
".............#####......",
".........................",
"......C.................",
".......#####......S....",
".........................",
".........................",
".....#####...............",
".........................",
"#########################",
],
[
"........................",
"........C...............",
"........E.......C.......",
"......#####.............",
"....................S...",
".....C..................",
"....#####...............",
"....................E...",
".........................",
".....#####...............",
".........................",
"#########################",
]
]

# ---------------- CAMERA ----------------
class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0,0)
        self.shake = 0

    def update(self, target):
        self.offset.x = target.rect.centerx - WIDTH//2
        self.offset.y = target.rect.centery - HEIGHT//2
        if self.shake > 0:
            self.offset += pygame.Vector2(random.randint(-4,4), random.randint(-4,4))
            self.shake -= 1

# ---------------- TILES ----------------
class Tile(pygame.sprite.Sprite):
    def __init__(self,x,y,color):
        super().__init__()
        self.image = pygame.Surface((TILE,TILE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x,y))

class Spike(Tile):
    def __init__(self,x,y):
        super().__init__(x,y,PURPLE)

class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.Surface((20,20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x,y))

# ---------------- PLAYER ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.Surface((36,46))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(midbottom=(x,y))

        self.pos = pygame.Vector2(self.rect.topleft)
        self.vel = pygame.Vector2(0,0)
        self.acc = pygame.Vector2(0,0)

        self.hp = 5
        self.coins = 0
        self.on_ground = False
        self.facing = 1
        self.dash_cd = 0

    def input(self):
        k = pygame.key.get_pressed()
        self.acc.x = 0
        if k[pygame.K_a] or k[pygame.K_LEFT]:
            self.acc.x = -ACC
            self.facing = -1
        if k[pygame.K_d] or k[pygame.K_RIGHT]:
            self.acc.x = ACC
            self.facing = 1

    def jump(self):
        if self.on_ground:
            self.vel.y = JUMP
            self.on_ground = False

    def dash(self):
        if self.dash_cd == 0:
            self.vel.x = 20 * self.facing
            self.dash_cd = 40

    def update(self, platforms):
        self.input()
        self.acc.y = GRAVITY
        self.acc.x += self.vel.x * FRICTION

        self.vel += self.acc
        self.pos += self.vel + 0.5*self.acc

        self.rect.x = self.pos.x
        self.collide(platforms,'x')
        self.rect.y = self.pos.y
        self.collide(platforms,'y')

        if self.dash_cd > 0:
            self.dash_cd -= 1

    def collide(self, platforms, d):
        for p in pygame.sprite.spritecollide(self,platforms,False):
            if d == 'x':
                if self.vel.x > 0: self.rect.right = p.rect.left
                if self.vel.x < 0: self.rect.left = p.rect.right
                self.pos.x = self.rect.x
                self.vel.x = 0
            if d == 'y':
                if self.vel.y > 0:
                    self.rect.bottom = p.rect.top
                    self.on_ground = True
                if self.vel.y < 0:
                    self.rect.top = p.rect.bottom
                self.pos.y = self.rect.y
                self.vel.y = 0

# ---------------- ENEMY ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.Surface((36,36))
        self.image.fill(RED)
        self.rect = self.image.get_rect(midbottom=(x,y))
        self.hp = 2
        self.speed = 2

    def update(self, player):
        if abs(player.rect.centerx - self.rect.centerx) < 250:
            self.rect.x += self.speed if player.rect.centerx > self.rect.centerx else -self.speed

# ---------------- LOAD LEVEL ----------------
def load_level(idx):
    platforms.empty(); enemies.empty(); coins.empty(); spikes.empty(); all.empty()
    lvl = levels[idx]
    for r,row in enumerate(lvl):
        for c,t in enumerate(row):
            x,y = c*TILE, r*TILE
            if t == "#":
                p = Tile(x,y,GRAY); platforms.add(p); all.add(p)
            if t == "E":
                e = Enemy(x+TILE//2,y+TILE); enemies.add(e); all.add(e)
            if t == "C":
                c1 = Coin(x+TILE//2,y+TILE//2); coins.add(c1); all.add(c1)
            if t == "S":
                s = Spike(x,y); spikes.add(s); all.add(s)

# ---------------- GROUPS ----------------
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
spikes = pygame.sprite.Group()
all = pygame.sprite.Group()

player = Player(100,200)
all.add(player)

camera = Camera()
level_index = 0
load_level(level_index)

# ---------------- GAME LOOP ----------------
while True:
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE: player.jump()
            if e.key == pygame.K_LSHIFT: player.dash()
            if e.key == pygame.K_r: exec(open(__file__).read())

    player.update(platforms)
    enemies.update(player)

    if pygame.sprite.spritecollide(player,spikes,False):
        player.hp -= 1
        camera.shake = 10
        if player.hp <= 0:
            exec(open(__file__).read())

    for en in enemies.copy():
        if pygame.sprite.collide_rect(player,en):
            player.hp -= 1
            camera.shake = 10
            en.kill()

    player.coins += len(pygame.sprite.spritecollide(player,coins,True))

    if player.rect.x > len(levels[level_index][0])*TILE - 100:
        level_index = (level_index + 1) % len(levels)
        load_level(level_index)
        player.pos = pygame.Vector2(100,200)

    camera.update(player)

    screen.fill(WHITE)
    for s in all:
        screen.blit(s.image, s.rect.topleft - camera.offset)

    ui = font.render(f"HP:{player.hp}  Coins:{player.coins}  Level:{level_index+1}", True, BLACK)
    screen.blit(ui,(20,20))

    pygame.display.flip()
