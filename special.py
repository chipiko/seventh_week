import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")

clock = pygame.time.Clock()

WHITE = (255,255,255)
BLACK = (30,30,40)
GREEN = (50,200,50)
RED = (200,50,50)
BLUE = (80,120,255)
GRAY = (120,120,120)
YELLOW = (240,200,70)

font = pygame.font.SysFont("arial", 22)
big_font = pygame.font.SysFont("arial", 48)

# Path points
path = [(0,300),(200,300),(200,150),(500,150),(500,400),(800,400),(800,250),(1000,250)]

enemies = []
towers = []
bullets = []

money = 200
lives = 10
wave = 1
spawn_timer = 0
game_over = False

def spawn_enemy():
    enemies.append({
        "x": path[0][0],
        "y": path[0][1],
        "speed": 1.5 + wave*0.2,
        "hp": 3 + wave,
        "point": 0
    })

def reset_game():
    global enemies,towers,bullets,money,lives,wave,game_over
    enemies = []
    towers = []
    bullets = []
    money = 200
    lives = 10
    wave = 1
    game_over = False

while True:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mx,my = pygame.mouse.get_pos()
            if money >= 100:
                towers.append({"x":mx,"y":my,"range":120,"cooldown":0})
                money -= 100

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()

    if not game_over:

        spawn_timer += 1
        if spawn_timer > 60:
            spawn_enemy()
            spawn_timer = 0

        # Enemy movement
        for enemy in enemies[:]:
            target = path[enemy["point"]+1]
            angle = math.atan2(target[1]-enemy["y"], target[0]-enemy["x"])
            enemy["x"] += math.cos(angle)*enemy["speed"]
            enemy["y"] += math.sin(angle)*enemy["speed"]

            if math.hypot(target[0]-enemy["x"], target[1]-enemy["y"]) < 5:
                enemy["point"] += 1
                if enemy["point"] >= len(path)-1:
                    enemies.remove(enemy)
                    lives -= 1
                    if lives <= 0:
                        game_over = True

        # Towers shooting
        for tower in towers:
            tower["cooldown"] -= 1
            if tower["cooldown"] <= 0:
                for enemy in enemies:
                    dist = math.hypot(enemy["x"]-tower["x"], enemy["y"]-tower["y"])
                    if dist < tower["range"]:
                        bullets.append({
                            "x":tower["x"],
                            "y":tower["y"],
                            "target":enemy
                        })
                        tower["cooldown"] = 40
                        break

        # Bullet movement
        for bullet in bullets[:]:
            if bullet["target"] not in enemies:
                bullets.remove(bullet)
                continue

            target = bullet["target"]
            angle = math.atan2(target["y"]-bullet["y"], target["x"]-bullet["x"])
            bullet["x"] += math.cos(angle)*8
            bullet["y"] += math.sin(angle)*8

            if math.hypot(target["x"]-bullet["x"], target["y"]-bullet["y"]) < 10:
                target["hp"] -= 1
                bullets.remove(bullet)
                if target["hp"] <= 0:
                    enemies.remove(target)
                    money += 20
                    if money % 200 == 0:
                        wave += 1
                break

    # Draw path
    pygame.draw.lines(screen, GRAY, False, path, 10)

    # Draw towers
    for tower in towers:
        pygame.draw.circle(screen, BLUE, (int(tower["x"]),int(tower["y"])),15)

    # Draw enemies
    for enemy in enemies:
        pygame.draw.circle(screen, RED, (int(enemy["x"]),int(enemy["y"])),15)

    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(screen, YELLOW, (int(bullet["x"]),int(bullet["y"])),5)

    # UI
    screen.blit(font.render(f"Money: {money}",True,WHITE),(10,10))
    screen.blit(font.render(f"Lives: {lives}",True,WHITE),(10,40))
    screen.blit(font.render(f"Wave: {wave}",True,WHITE),(10,70))

    if game_over:
        text = big_font.render("GAME OVER",True,RED)
        restart = font.render("Press R to Restart",True,WHITE)
        screen.blit(text,(WIDTH//2-150,HEIGHT//2-40))
        screen.blit(restart,(WIDTH//2-120,HEIGHT//2+20))

    pygame.display.update()