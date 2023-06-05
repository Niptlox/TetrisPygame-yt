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
SMARTBOT = True


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


def check_collide(_player_figure=None, _pos=None):
    if _player_figure is None:
        _player_figure = player_figure
        _pos = pos
    for point in _player_figure:
        x, y = _pos[0] + point[0], _pos[1] + point[1]
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


K_SPEED = 0
K_LEFT = 1
K_RIGHT = 2
K_ROTATE = 3


def player_step(key):
    global player_figure, speed_boost
    if key == K_SPEED:
        speed_boost = True
    elif key == K_LEFT:
        pos[0] -= 1
        if check_collide():
            pos[0] += 1
    elif key == K_RIGHT:
        pos[0] += 1
        if check_collide():
            pos[0] -= 1
    elif key == K_ROTATE:
        _player_figure = player_figure
        player_figure = rotate_right90(player_figure)
        if check_collide():
            player_figure = _player_figure


first = True


def step_q(fig, y):
    min_y = min([y + p[1] for p in fig])
    max_y = max([y + p[1] for p in fig])
    return max_y, len([1 for p in fig if (y + p[1]) == max_y])


def compare_q(q1, q2):
    if q1[0] > q2[0] or (q1[0] == q2[0] and q1[1] > q2[1]):
        return True
    return False


def smartbot(start_x=2, start_y=2):
    # maxy, x, rotates
    best = (-1, 0, 0)
    for x in range(MSIZE[0]):
        for k in range(3):
            fig = player_figure
            for i in range(k):
                fig = rotate_right90(fig)

            if check_collide(fig, (x, start_y)):
                break
            for iy in range(1, MSIZE[1]):
                y = start_y + iy
                if check_collide(fig, (x, y)):
                    q = step_q(fig, y - 1)
                    if best[0] == -1 or compare_q(q, best[0]):
                        best = (q, x, k)
                    break
    return best


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
    key = None
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
                    key = K_SPEED
                elif event.key == pg.K_LEFT:
                    key = K_LEFT
                elif event.key == pg.K_RIGHT:
                    key = K_RIGHT
                elif event.key == pg.K_UP:
                    key = K_ROTATE
            player_step(key)

    if not game_over:
        if SMARTBOT:
            best_step = smartbot()
            if best_step[0] != -1:
                # if best_step[2]:
                #     player_step(K_ROTATE)
                # if best_step[1] != pos[1]:
                #     if best_step[1] > pos[1]:
                #         player_step(K_RIGHT)
                #     else:
                #         player_step(K_LEFT)
                for ix in range(abs(pos[0] - best_step[1])):
                    if best_step[1] > pos[1]:
                        player_step(K_RIGHT)
                    else:
                        player_step(K_LEFT)
                for ik in range(best_step[2]):
                    player_step(K_ROTATE)
            player_step(K_SPEED)

        # отрисовка игрока
        for point in player_figure:
            x, y = pos[0] + point[0], pos[1] + point[1]
            pg.draw.rect(screen, player_color, (x * TSIDE, y * TSIDE, TSIDE, TSIDE))
    # отрисовка след фигуры
    for point in next_figure:
        x, y = MSIZE[0] + 3.2 + point[0], 4 + point[1]
        pg.draw.rect(screen, next_color, (x * TSIDE, y * TSIDE, TSIDE - 1, TSIDE - 1))
    lines = defaultdict(int)
    # отрисовка остальных фигур
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
        screen.blit(text, (2 + (WSIZE[0] - text.get_width()) // 2, WSIZE[1] // 2 + 2))
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
