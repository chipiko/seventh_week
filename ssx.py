import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")

clock = pygame.time.Clock()

WHITE = (255,255,255)
BLACK = (25,25,35)
GREEN = (50,200,50)
RED = (200,50,50)
BLUE = (80,120,255)
YELLOW = (240,200,70)

font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 48)

# Player
player = pygame.Rect(100, 400, 40, 60)
player_vel_y = 0
gravity = 0.8
jump_power = -15
speed = 6
on_ground = False
lives = 3
score = 0
game_over = False

# Platforms
platforms = [
    pygame.Rect(0,550,1000,50),
    pygame.Rect(200,450,200,20),
    pygame.Rect(500,350,200,20),
    pygame.Rect(750,250,150,20)
]

# Coins
coins = []
for i in range(10):
    coins.append(pygame.Rect(random.randint(100,900), random.randint(100,400), 20, 20))

# Enemies
enemies = [
    pygame.Rect(300,510,40,40),
    pygame.Rect(600,510,40,40)
]

def reset_game():
    global player, player_vel_y, lives, score, game_over
    player.x = 100
    player.y = 400
    player_vel_y = 0
    lives = 3
    score = 0
    game_over = False

while True:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:

        # Horizontal movement
        if keys[pygame.K_LEFT]:
            player.x -= speed
        if keys[pygame.K_RIGHT]:
            player.x += speed

        # Gravity
        player_vel_y += gravity
        player.y += player_vel_y
        on_ground = False

        # Platform collision
        for platform in platforms:
            if player.colliderect(platform) and player_vel_y >= 0:
                player.bottom = platform.top
                player_vel_y = 0
                on_ground = True

        # Jump
        if keys[pygame.K_UP] and on_ground:
            player_vel_y = jump_power

        # Enemy collision
        for enemy in enemies:
            if player.colliderect(enemy):
                lives -= 1
                player.x = 100
                player.y = 400
                if lives <= 0:
                    game_over = True

        # Coin collection
        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)
                score += 10

        if len(coins) == 0:
            coins = []
            for i in range(10):
                coins.append(pygame.Rect(random.randint(100,900), random.randint(100,400), 20, 20))

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, BLUE, platform)

    # Draw player
    pygame.draw.rect(screen, GREEN, player)

    # Draw coins
    for coin in coins:
        pygame.draw.circle(screen, YELLOW, coin.center, 10)

    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)

    # UI
    screen.blit(font.render(f"Lives: {lives}", True, WHITE), (10,10))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10,40))

    if game_over:
        text = big_font.render("GAME OVER", True, RED)
        restart = font.render("Press R to Restart", True, WHITE)
        screen.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 40))
        screen.blit(restart, (WIDTH//2 - 120, HEIGHT//2 + 20))

    pygame.display.update()