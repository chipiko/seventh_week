import pygame
import sys

pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 960, 540
FPS = 60
TILE_SIZE = 48

GRAVITY = 0.8
FRICTION = -0.12
PLAYER_ACC = 0.8
PLAYER_JUMP = -16

# ---------------- WINDOW ----------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer")
clock = pygame.time.Clock()

# ---------------- COLORS ----------------
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
BLUE = (60, 120, 255)
RED = (220, 60, 60)
GREEN = (60, 200, 120)

# ---------------- LEVEL MAP ----------------
level_map = [
    "........................",
    "........................",
    "........................",
    "...............E........",
    ".............#####......",
    ".........................",
    ".......#####.............",
    ".........................",
    ".........................",
    ".....#####...............",
    ".........................",
    "#########################",
]

# ---------------- CAMERA ----------------
class Camera:
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)

    def update(self, target):
        self.offset.x = target.rect.centerx - WIDTH // 2
        self.offset.y = target.rect.centery - HEIGHT // 2

# ---------------- PLATFORM ----------------
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect(topleft=(x, y))

# ---------------- PLAYER ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((36, 46))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.pos = pygame.Vector2(self.rect.topleft)
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)
        self.on_ground = False

    def input(self):
        keys = pygame.key.get_pressed()
        self.acc.x = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.acc.x = PLAYER_ACC

    def jump(self):
        if self.on_ground:
            self.vel.y = PLAYER_JUMP
            self.on_ground = False

    def update(self, platforms):
        self.input()

        self.acc.y = GRAVITY
        self.acc.x += self.vel.x * FRICTION

        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        self.rect.x = self.pos.x
        self.collide(platforms, 'x')

        self.rect.y = self.pos.y
        self.collide(platforms, 'y')

    def collide(self, platforms, direction):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hits:
            if direction == 'x':
                if self.vel.x > 0:
                    self.rect.right = platform.rect.left
                if self.vel.x < 0:
                    self.rect.left = platform.rect.right
                self.pos.x = self.rect.x
                self.vel.x = 0

            if direction == 'y':
                if self.vel.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                if self.vel.y < 0:
                    self.rect.top = platform.rect.bottom
                self.pos.y = self.rect.y
                self.vel.y = 0

# ---------------- ENEMY ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((36, 36))
        self.image.fill(RED)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = 2
        self.direction = 1

    def update(self, platforms):
        self.rect.x += self.speed * self.direction
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            self.direction *= -1

# ---------------- LOAD LEVEL ----------------
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

for row_idx, row in enumerate(level_map):
    for col_idx, tile in enumerate(row):
        x = col_idx * TILE_SIZE
        y = row_idx * TILE_SIZE

        if tile == "#":
            p = Platform(x, y)
            platforms.add(p)
            all_sprites.add(p)

        if tile == "E":
            e = Enemy(x + TILE_SIZE // 2, y + TILE_SIZE)
            enemies.add(e)
            all_sprites.add(e)

player = Player(100, 200)
all_sprites.add(player)

camera = Camera()

# ---------------- GAME LOOP ----------------
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_ESCAPE:
                running = False

    player.update(platforms)
    enemies.update(platforms)
    camera.update(player)

    screen.fill(WHITE)

    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect.topleft - camera.offset)

    pygame.display.flip()

pygame.quit()
sys.exit()
