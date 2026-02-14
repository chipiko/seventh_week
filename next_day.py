import pygame
import random
import sys

pygame.init()

# Window
WIDTH = 600
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 48)

# Player
player_width = 50
player_height = 60
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 80
player_speed = 7
player_hp = 3

# Bullet
bullets = []
bullet_speed = 10

# Enemy
enemies = []
enemy_speed = 3
enemy_spawn_delay = 40
spawn_counter = 0

score = 0
game_over = False

def spawn_enemy():
    x = random.randint(0, WIDTH - 40)
    y = -50
    enemies.append([x, y])

def draw_player(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, player_width, player_height))

def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, GREEN, (bullet[0], bullet[1], 5, 15))

def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy[0], enemy[1], 40, 40))

def reset_game():
    global bullets, enemies, score, player_hp, game_over
    bullets = []
    enemies = []
    score = 0
    player_hp = 3
    game_over = False

# Game Loop
while True:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bullets.append([player_x + player_width // 2 - 2, player_y])
            if event.key == pygame.K_r and game_over:
                reset_game()

    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed

        # Bullets movement
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)

        # Enemy spawn
        spawn_counter += 1
        if spawn_counter >= enemy_spawn_delay:
            spawn_enemy()
            spawn_counter = 0

        # Enemy movement
        for enemy in enemies[:]:
            enemy[1] += enemy_speed
            if enemy[1] > HEIGHT:
                enemies.remove(enemy)
                player_hp -= 1
                if player_hp <= 0:
                    game_over = True

        # Collision
        for enemy in enemies[:]:
            for bullet in bullets[:]:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], 40, 40)
                bullet_rect = pygame.Rect(bullet[0], bullet[1], 5, 15)

                if enemy_rect.colliderect(bullet_rect):
                    if enemy in enemies:
                        enemies.remove(enemy)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    score += 1
                    break

    # Draw
    draw_player(player_x, player_y)
    draw_bullets()
    draw_enemies()

    # UI
    hp_text = font.render(f"HP: {player_hp}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(hp_text, (10, 10))
    screen.blit(score_text, (10, 40))

    if game_over:
        over_text = big_font.render("GAME OVER", True, RED)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(over_text, (WIDTH//2 - 150, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - 110, HEIGHT//2 + 10))

    pygame.display.update()
