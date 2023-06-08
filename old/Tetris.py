from collections import defaultdict

import pygame as pg
import random

pg.init()
pg.display.set_caption("TETRIS.py")
FPS = 60
WSIZE = (440, 500)
TSIDE = 25
MSIZE = (10, 20)

font = pg.font.SysFont("", 40)


def rotate_right90(points):
    # x, y => -y, x
    return [(-p[1], p[0]) for p in points]


def new_figure():
    global player_figure, player_color, next_figure, next_color, pos, game_over
    player_figure = next_figure[:]
    player_color = next_color
    next_figure = random.choice(figures)
    next_color = random.choice(colors)
    pos = [5, 1]

    if check_collide():
        game_over = True


def check_collide():
    for point in player_figure:
        x, y = pos[0] + point[0], pos[1] + point[1]
        if (x, y) in field or not (0 <= x < MSIZE[0] and 0 <= y < MSIZE[1]):
            return True
    return False


def del_line(iy):
    global field
    new_field = {}
    for p, color, in field.items():
        if p[1] > iy:
            new_field[p] = color
        if p[1] < iy:
            new_field[(p[0], p[1] + 1)] = color
    field = new_field


screen = pg.display.set_mode(WSIZE)
clock = pg.time.Clock()

colors = ("red", "green", "orange", "blue", "violet", "yellow")
field = {}
line_color = "#27272A"

figures = [((-1, 0), (0, 0), (1, 0), (1, 1)),  # Г
           ((-1, 0), (0, 0), (1, 0), (1, -1)),  # Г 2
           ((-1, 0), (0, 0), (1, 0), (0, -1)),  # 3
           ((-1, 0), (0, 0), (1, 1), (0, 1)),  #
           ((-1, 1), (0, 0), (1, 0), (0, 1)),
           ((-1, 0), (0, 0), (1, 0), (2, 0)),
           ]

game_over = False
speed_boost = False
timer = 0
best_score = score = 0

global player_figure, player_color, pos
next_figure = random.choice(figures)
next_color = random.choice(colors)
new_figure()

running = True
while running:
    clock.tick(FPS)
    screen.fill("black")

    best_score = max(score, best_score)
    text = font.render(f"TETRIS", True, "White")
    screen.blit(text, (MSIZE[0] * TSIDE + 50, 40))
    text = font.render(f"Score: {score}", True, "Yellow")
    screen.blit(text, (MSIZE[0] * TSIDE + 15, WSIZE[1] - 100))
    text = font.render(f"Best: {best_score}", True, "Yellow")
    screen.blit(text, (MSIZE[0] * TSIDE + 15, WSIZE[1] - 60))

    # обработка событий
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if game_over:
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # restart
                game_over = False
                field = {}
                score = 0
                new_figure()
                new_figure()
        else:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    speed_boost = True
                elif event.key == pg.K_LEFT:
                    pos[0] -= 1
                    if check_collide():
                        pos[0] += 1
                elif event.key == pg.K_RIGHT:
                    pos[0] += 1
                    if check_collide():
                        pos[0] -= 1
                elif event.key == pg.K_UP:
                    _player_figure = player_figure
                    player_figure = rotate_right90(player_figure)
                    if check_collide():
                        player_figure = _player_figure

    if not game_over:
        # отрисовка игрока
        for point in player_figure:
            x, y = pos[0] + point[0], pos[1] + point[1]
            pg.draw.rect(screen, player_color, (x * TSIDE, y * TSIDE, TSIDE, TSIDE))
    # отрисовка след фигуры
    for point in next_figure:
        x, y = MSIZE[0] + 3.2 + point[0], 4 + point[1]
        pg.draw.rect(screen, next_color, (x * TSIDE, y * TSIDE, TSIDE - 1, TSIDE - 1))
    lines = defaultdict(int)
    # отрисовка поля
    for ixy, cell_color in field.items():
        x, y = ixy
        pg.draw.rect(screen, cell_color, (x * TSIDE, y * TSIDE, TSIDE, TSIDE))
        lines[y] += 1
    # удаление заполненных линий
    for iy, c in lines.items():
        if c == MSIZE[0]:
            del_line(iy)
            score += 10
    # отрисовка сетки
    for ix in range(MSIZE[0] + 1):
        pg.draw.line(screen, line_color, (ix * TSIDE, 0), (ix * TSIDE, MSIZE[1] * TSIDE), 1)
    for iy in range(MSIZE[1] + 1):
        pg.draw.line(screen, line_color, (0, iy * TSIDE), (MSIZE[0] * TSIDE, iy * TSIDE), 1)

    if game_over:
        text = font.render("GAME OVER", True, "black")
        screen.blit(text, ((WSIZE[0] - text.get_width()) // 2, WSIZE[1] // 2))
        text = font.render("GAME OVER", True, "white")
        screen.blit(text, (2+(WSIZE[0] - text.get_width()) // 2, WSIZE[1] // 2+2))
    else:
        # падение вниз
        if timer <= 0 or speed_boost:
            pos[1] += 1
            if check_collide():
                speed_boost = False
                pos[1] -= 1
                for point in player_figure:
                    xy = pos[0] + point[0], pos[1] + point[1]
                    field[xy] = player_color
                new_figure()
                score += 1

            timer = 30
        timer -= 1
    pg.display.flip()
