import pygame
import random
import math
import sys

pygame.init()

# Window
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
GRAY = (100, 100, 100)

font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 48)

# Player
player = {
    "x": WIDTH//2,
    "y": HEIGHT//2,
    "speed": 4,
    "hp": 100
}

bullets = []
zombies = []

score = 0
wave = 1
spawn_timer = 0
game_over = False
start_time = pygame.time.get_ticks()

def spawn_zombie():
    side = random.choice(["top","bottom","left","right"])
    if side == "top":
        x = random.randint(0, WIDTH)
        y = -40
    elif side == "bottom":
        x = random.randint(0, WIDTH)
        y = HEIGHT+40
    elif side == "left":
        x = -40
        y = random.randint(0, HEIGHT)
    else:
        x = WIDTH+40
        y = random.randint(0, HEIGHT)

    zombies.append({
        "x": x,
        "y": y,
        "speed": 1.5 + wave*0.2,
        "hp": 2
    })

def reset_game():
    global bullets, zombies, score, wave, game_over, player, start_time
    bullets = []
    zombies = []
    score = 0
    wave = 1
    game_over = False
    player["x"] = WIDTH//2
    player["y"] = HEIGHT//2
    player["hp"] = 100
    start_time = pygame.time.get_ticks()

# Game Loop
while True:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my - player["y"], mx - player["x"])
            bullets.append({
                "x": player["x"],
                "y": player["y"],
                "dx": math.cos(angle)*10,
                "dy": math.sin(angle)*10
            })

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()

    keys = pygame.key.get_pressed()

    if not game_over:

        # Sprint
        speed = player["speed"]
        if keys[pygame.K_LSHIFT]:
            speed = 7

        # Movement
        if keys[pygame.K_w]: player["y"] -= speed
        if keys[pygame.K_s]: player["y"] += speed
        if keys[pygame.K_a]: player["x"] -= speed
        if keys[pygame.K_d]: player["x"] += speed

        player["x"] = max(0, min(WIDTH, player["x"]))
        player["y"] = max(0, min(HEIGHT, player["y"]))

        # Spawn zombies
        spawn_timer += 1
        if spawn_timer > 60 - min(wave*2, 40):
            spawn_zombie()
            spawn_timer = 0

        # Increase difficulty
        if score // 20 + 1 > wave:
            wave += 1

        # Bullet movement
        for bullet in bullets[:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]
            if bullet["x"] < 0 or bullet["x"] > WIDTH or bullet["y"] < 0 or bullet["y"] > HEIGHT:
                bullets.remove(bullet)

        # Zombie movement
        for zombie in zombies[:]:
            angle = math.atan2(player["y"] - zombie["y"], player["x"] - zombie["x"])
            zombie["x"] += math.cos(angle)*zombie["speed"]
            zombie["y"] += math.sin(angle)*zombie["speed"]

            zombie_rect = pygame.Rect(zombie["x"]-15, zombie["y"]-15, 30, 30)
            player_rect = pygame.Rect(player["x"]-15, player["y"]-15, 30, 30)

            if zombie_rect.colliderect(player_rect):
                player["hp"] -= 0.3
                if player["hp"] <= 0:
                    game_over = True

            for bullet in bullets[:]:
                bullet_rect = pygame.Rect(bullet["x"]-4, bullet["y"]-4, 8, 8)
                if zombie_rect.colliderect(bullet_rect):
                    zombie["hp"] -= 1
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if zombie["hp"] <= 0:
                        zombies.remove(zombie)
                        score += 1
                    break

    # Draw player
    pygame.draw.circle(screen, GREEN, (int(player["x"]), int(player["y"])), 15)

    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(screen, WHITE, (int(bullet["x"]), int(bullet["y"])), 4)

    # Draw zombies
    for zombie in zombies:
        pygame.draw.circle(screen, RED, (int(zombie["x"]), int(zombie["y"])), 15)

    # UI
    elapsed_time = (pygame.time.get_ticks() - start_time)//1000
    screen.blit(font.render(f"HP: {int(player['hp'])}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 40))
    screen.blit(font.render(f"Wave: {wave}", True, WHITE), (10, 70))
    screen.blit(font.render(f"Time: {elapsed_time}s", True, WHITE), (10, 100))

    if game_over:
        text = big_font.render("GAME OVER", True, RED)
        restart = font.render("Press R to Restart", True, WHITE)
        screen.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 40))
        screen.blit(restart, (WIDTH//2 - 120, HEIGHT//2 + 20))

    pygame.display.update()
