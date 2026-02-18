import pygame
import sys
import random
import os

pygame.init()

# Window
WIDTH = 900
HEIGHT = 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker PRO")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (15, 15, 25)
BLUE = (70, 120, 255)
RED = (220, 70, 70)
GREEN = (70, 220, 120)
YELLOW = (240, 200, 70)
PURPLE = (180, 70, 220)

font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 48)

# Paddle
paddle_width = 130
paddle_height = 15
paddle_x = WIDTH // 2 - paddle_width // 2
paddle_y = HEIGHT - 50
paddle_speed = 9

# Balls (multi-ball support)
balls = []

# Bricks
brick_rows = 6
brick_cols = 12
brick_width = WIDTH // brick_cols
brick_height = 30
bricks = []

# PowerUps
powerups = []

score = 0
lives = 3
game_over = False
game_win = False
game_start = True

highscore = 0
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        highscore = int(f.read())

def save_highscore():
    global highscore
    if score > highscore:
        highscore = score
        with open("highscore.txt", "w") as f:
            f.write(str(highscore))

def create_bricks():
    bricks.clear()
    colors = [RED, GREEN, YELLOW, PURPLE]
    for row in range(brick_rows):
        for col in range(brick_cols):
            rect = pygame.Rect(
                col * brick_width + 2,
                row * brick_height + 60,
                brick_width - 4,
                brick_height - 4
            )
            bricks.append([rect, random.choice(colors)])

def spawn_ball():
    balls.append({
        "x": WIDTH // 2,
        "y": HEIGHT // 2,
        "dx": random.choice([-5, 5]),
        "dy": -5
    })

create_bricks()
spawn_ball()

def reset_game():
    global paddle_width, paddle_x, score, lives, game_over, game_win
    paddle_width = 130
    paddle_x = WIDTH // 2 - paddle_width // 2
    score = 0
    lives = 3
    game_over = False
    game_win = False
    balls.clear()
    powerups.clear()
    create_bricks()
    spawn_ball()

# Game Loop
while True:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_highscore()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_start:
                game_start = False
            if event.key == pygame.K_r and (game_over or game_win):
                reset_game()
                game_start = True

    keys = pygame.key.get_pressed()

    if not game_start and not game_over and not game_win:

        # Paddle movement
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:
            paddle_x += paddle_speed

        paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)

        # Ball logic
        for ball in balls[:]:
            ball["x"] += ball["dx"]
            ball["y"] += ball["dy"]

            if ball["x"] <= 0 or ball["x"] >= WIDTH:
                ball["dx"] *= -1
            if ball["y"] <= 0:
                ball["dy"] *= -1

            ball_rect = pygame.Rect(ball["x"]-8, ball["y"]-8, 16, 16)

            # Paddle collision (angle control)
            if ball_rect.colliderect(paddle_rect):
                offset = (ball["x"] - paddle_x) / paddle_width
                ball["dx"] = (offset - 0.5) * 12
                ball["dy"] *= -1

            # Brick collision
            for brick in bricks[:]:
                if ball_rect.colliderect(brick[0]):
                    bricks.remove(brick)
                    ball["dy"] *= -1
                    score += 10

                    # Random powerup drop
                    if random.random() < 0.2:
                        powerups.append([brick[0].x, brick[0].y, random.choice(["expand", "life", "multiball"])])
                    break

            if ball["y"] > HEIGHT:
                balls.remove(ball)

        if len(balls) == 0:
            lives -= 1
            if lives <= 0:
                game_over = True
                save_highscore()
            else:
                spawn_ball()

        # PowerUps
        for p in powerups[:]:
            p[1] += 4
            rect = pygame.Rect(p[0], p[1], 20, 20)
            if rect.colliderect(paddle_rect):
                if p[2] == "expand":
                    paddle_width += 40
                elif p[2] == "life":
                    lives += 1
                elif p[2] == "multiball":
                    spawn_ball()
                powerups.remove(p)

            elif p[1] > HEIGHT:
                powerups.remove(p)

        if len(bricks) == 0:
            game_win = True
            save_highscore()

    # Draw Paddle
    pygame.draw.rect(screen, BLUE, (paddle_x, paddle_y, paddle_width, paddle_height))

    # Draw Balls
    for ball in balls:
        pygame.draw.circle(screen, WHITE, (int(ball["x"]), int(ball["y"])), 8)

    # Draw Bricks
    for brick in bricks:
        pygame.draw.rect(screen, brick[1], brick[0])

    # Draw PowerUps
    for p in powerups:
        color = GREEN if p[2]=="expand" else YELLOW if p[2]=="life" else PURPLE
        pygame.draw.rect(screen, color, (p[0], p[1], 20, 20))

    # UI
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {lives}", True, WHITE), (10, 40))
    screen.blit(font.render(f"High Score: {highscore}", True, WHITE), (10, 70))

    if game_start:
        text = big_font.render("PRESS SPACE TO START", True, WHITE)
        screen.blit(text, (WIDTH//2 - 260, HEIGHT//2 - 40))

    if game_over:
        text = big_font.render("GAME OVER", True, RED)
        screen.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 40))

    if game_win:
        text = big_font.render("YOU WIN!", True, GREEN)
        screen.blit(text, (WIDTH//2 - 120, HEIGHT//2 - 40))

    pygame.display.update()
