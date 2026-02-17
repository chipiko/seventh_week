import pygame
import sys
import random

pygame.init()

# Window
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (240, 240, 0)
BLACK = (0, 0, 0)

font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 48)

# Paddle
paddle_width = 120
paddle_height = 15
paddle_x = WIDTH // 2 - paddle_width // 2
paddle_y = HEIGHT - 40
paddle_speed = 8

# Ball
ball_radius = 10
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_dx = 5
ball_dy = -5

# Bricks
brick_rows = 5
brick_cols = 10
brick_width = WIDTH // brick_cols
brick_height = 30

bricks = []

def create_bricks():
    global bricks
    bricks = []
    for row in range(brick_rows):
        for col in range(brick_cols):
            brick_rect = pygame.Rect(
                col * brick_width,
                row * brick_height + 50,
                brick_width - 5,
                brick_height - 5
            )
            bricks.append(brick_rect)

create_bricks()

score = 0
lives = 3
game_over = False
game_win = False

def reset_game():
    global ball_x, ball_y, ball_dx, ball_dy
    global score, lives, game_over, game_win, paddle_x

    paddle_x = WIDTH // 2 - paddle_width // 2
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_dx = 5
    ball_dy = -5
    score = 0
    lives = 3
    game_over = False
    game_win = False
    create_bricks()

# Game Loop
while True:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (game_over or game_win):
                reset_game()

    keys = pygame.key.get_pressed()

    if not game_over and not game_win:
        # Paddle movement
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width:
            paddle_x += paddle_speed

        # Ball movement
        ball_x += ball_dx
        ball_y += ball_dy

        # Wall collision
        if ball_x <= 0 or ball_x >= WIDTH:
            ball_dx *= -1
        if ball_y <= 0:
            ball_dy *= -1

        # Paddle collision
        paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
        ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius,
                                ball_radius * 2, ball_radius * 2)

        if ball_rect.colliderect(paddle_rect):
            ball_dy *= -1

        # Brick collision
        for brick in bricks[:]:
            if ball_rect.colliderect(brick):
                bricks.remove(brick)
                ball_dy *= -1
                score += 10
                break

        # Ball falls down
        if ball_y > HEIGHT:
            lives -= 1
            ball_x = WIDTH // 2
            ball_y = HEIGHT // 2
            ball_dy = -5

            if lives <= 0:
                game_over = True

        if len(bricks) == 0:
            game_win = True

    # Draw paddle
    pygame.draw.rect(screen, BLUE, (paddle_x, paddle_y, paddle_width, paddle_height))

    # Draw ball
    pygame.draw.circle(screen, WHITE, (ball_x, ball_y), ball_radius)

    # Draw bricks
    for brick in bricks:
        pygame.draw.rect(screen, random.choice([RED, GREEN, YELLOW]), brick)

    # UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))

    if game_over:
        over_text = big_font.render("GAME OVER", True, RED)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(over_text, (WIDTH//2 - 160, HEIGHT//2 - 40))
        screen.blit(restart_text, (WIDTH//2 - 120, HEIGHT//2 + 20))

    if game_win:
        win_text = big_font.render("YOU WIN!", True, GREEN)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(win_text, (WIDTH//2 - 130, HEIGHT//2 - 40))
        screen.blit(restart_text, (WIDTH//2 - 120, HEIGHT//2 + 20))

    pygame.display.update()
