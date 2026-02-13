import pygame, sys, random, math

pygame.init()

WIDTH, HEIGHT = 960, 540
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arena Shooter V1")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 20)
big_font = pygame.font.SysFont("consolas", 48)

WHITE=(240,240,240)
BLACK=(20,20,20)
RED=(220,60,60)
GREEN=(60,220,120)
BLUE=(80,130,255)
YELLOW=(240,220,70)
GRAY=(120,120,120)

MENU,PLAYING,PAUSED,GAMEOVER=0,1,2,3
game_state=MENU

# ---------------- PLAYER ----------------
class Player:
    def __init__(self):
        self.pos=pygame.Vector2(WIDTH//2,HEIGHT//2)
        self.vel=pygame.Vector2(0,0)
        self.speed=5
        self.radius=18
        self.hp=100
        self.score=0
        self.shoot_cd=0
        self.dash_cd=0
        self.invincible=0

    def update(self):
        keys=pygame.key.get_pressed()
        move=pygame.Vector2(0,0)

        if keys[pygame.K_w]: move.y=-1
        if keys[pygame.K_s]: move.y=1
        if keys[pygame.K_a]: move.x=-1
        if keys[pygame.K_d]: move.x=1

        if move.length()>0:
            move=move.normalize()

        self.pos+=move*self.speed

        self.pos.x=max(self.radius,min(WIDTH-self.radius,self.pos.x))
        self.pos.y=max(self.radius,min(HEIGHT-self.radius,self.pos.y))

        if self.shoot_cd>0: self.shoot_cd-=1
        if self.dash_cd>0: self.dash_cd-=1
        if self.invincible>0: self.invincible-=1

    def shoot(self):
        if self.shoot_cd==0:
            mx,my=pygame.mouse.get_pos()
            angle=math.atan2(my-self.pos.y,mx-self.pos.x)
            bullets.append(Bullet(self.pos.x,self.pos.y,angle))
            self.shoot_cd=10

    def dash(self):
        if self.dash_cd==0:
            mx,my=pygame.mouse.get_pos()
            direction=pygame.Vector2(mx-self.pos.x,my-self.pos.y)
            if direction.length()>0:
                direction=direction.normalize()
                self.pos+=direction*120
                self.dash_cd=60
                self.invincible=20

# ---------------- BULLET ----------------
class Bullet:
    def __init__(self,x,y,angle):
        self.pos=pygame.Vector2(x,y)
        self.vel=pygame.Vector2(math.cos(angle)*10,math.sin(angle)*10)
        self.radius=4

    def update(self):
        self.pos+=self.vel

# ---------------- ENEMY ----------------
class Enemy:
    def __init__(self):
        side=random.choice(["top","bottom","left","right"])
        if side=="top":
            self.pos=pygame.Vector2(random.randint(0,WIDTH),-20)
        elif side=="bottom":
            self.pos=pygame.Vector2(random.randint(0,WIDTH),HEIGHT+20)
        elif side=="left":
            self.pos=pygame.Vector2(-20,random.randint(0,HEIGHT))
        else:
            self.pos=pygame.Vector2(WIDTH+20,random.randint(0,HEIGHT))

        self.speed=random.uniform(1.5,2.5)
        self.radius=16
        self.hp=2

    def update(self):
        direction=player.pos-self.pos
        if direction.length()>0:
            direction=direction.normalize()
        self.pos+=direction*self.speed

# ---------------- PARTICLE ----------------
class Particle:
    def __init__(self,x,y):
        self.pos=pygame.Vector2(x,y)
        self.vel=pygame.Vector2(random.uniform(-3,3),random.uniform(-3,3))
        self.life=30

    def update(self):
        self.pos+=self.vel
        self.life-=1

# ---------------- INIT ----------------
def reset_game():
    global player, bullets, enemies, particles, wave_timer
    player=Player()
    bullets=[]
    enemies=[]
    particles=[]
    wave_timer=0

reset_game()

# ---------------- LOOP ----------------
while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type==pygame.KEYDOWN:
            if game_state==MENU:
                game_state=PLAYING
            elif game_state==PLAYING:
                if event.key==pygame.K_ESCAPE:
                    game_state=PAUSED
                if event.key==pygame.K_LSHIFT:
                    player.dash()
            elif game_state==PAUSED:
                if event.key==pygame.K_ESCAPE:
                    game_state=PLAYING
            elif game_state==GAMEOVER:
                if event.key==pygame.K_r:
                    reset_game()
                    game_state=PLAYING

        if event.type==pygame.MOUSEBUTTONDOWN and game_state==PLAYING:
            player.shoot()

    if game_state==PLAYING:
        player.update()

        for b in bullets[:]:
            b.update()
            if b.pos.x<0 or b.pos.x>WIDTH or b.pos.y<0 or b.pos.y>HEIGHT:
                bullets.remove(b)

        for e in enemies[:]:
            e.update()

            if (e.pos-player.pos).length()<e.radius+player.radius and player.invincible==0:
                player.hp-=10
                player.invincible=30
                if player.hp<=0:
                    game_state=GAMEOVER

            for b in bullets[:]:
                if (e.pos-b.pos).length()<e.radius+b.radius:
                    e.hp-=1
                    bullets.remove(b)
                    for _ in range(6):
                        particles.append(Particle(e.pos.x,e.pos.y))
                    if e.hp<=0:
                        enemies.remove(e)
                        player.score+=10

        for p in particles[:]:
            p.update()
            if p.life<=0:
                particles.remove(p)

        wave_timer+=1
        if wave_timer>60:
            enemies.append(Enemy())
            wave_timer=0

    screen.fill(BLACK)

    if game_state==MENU:
        screen.blit(big_font.render("ARENA SHOOTER",True,WHITE),(280,200))
        screen.blit(font.render("PRESS ANY KEY TO START",True,WHITE),(340,280))

    elif game_state in (PLAYING,PAUSED,GAMEOVER):
        pygame.draw.circle(screen,BLUE,(int(player.pos.x),int(player.pos.y)),player.radius)

        for b in bullets:
            pygame.draw.circle(screen,YELLOW,(int(b.pos.x),int(b.pos.y)),b.radius)

        for e in enemies:
            pygame.draw.circle(screen,RED,(int(e.pos.x),int(e.pos.y)),e.radius)

        for p in particles:
            pygame.draw.circle(screen,GRAY,(int(p.pos.x),int(p.pos.y)),3)

        ui=font.render(f"HP:{player.hp}   Score:{player.score}",True,WHITE)
        screen.blit(ui,(20,20))

        if game_state==PAUSED:
            screen.blit(big_font.render("PAUSED",True,WHITE),(400,230))

        if game_state==GAMEOVER:
            screen.blit(big_font.render("GAME OVER - R",True,RED),(260,250))

    pygame.display.flip()
