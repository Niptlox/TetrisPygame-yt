import random

import pygame as pg

pg.init()
# tile size
TSIZE = 25
# screen size
WSIZE = (TSIZE * 18, TSIZE * 20)
FPS = 30
# field size
FSIZE = (10, 20)

font1 = pg.font.SysFont('Roboto', 40)
font2 = pg.font.SysFont('Roboto', 42, bold=True)
font3 = pg.font.SysFont('Roboto', 45, bold=True)

screen = pg.display.set_mode(WSIZE)
clock = pg.time.Clock()
pg.display.set_caption("TETRIS v0")

figures = {
    "I": ((-1, 0), (0, 0), (1, 0), (2, 0)),
    "J": ((-1, -1), (-1, 0), (0, 0), (1, 0)),
    "L": ((-1, 0), (0, 0), (1, -1), (1, 0)),
    "O": ((0, -1), (0, 0), (1, -1), (1, 0)),
    "S": ((-1, 0), (0, -1), (0, 0), (1, -1)),
    "T": ((-1, 0), (0, -1), (0, 0), (1, 0)),
    "Z": ((-1, -1), (0, -1), (0, 0), (1, 0))
}
figure_rotations_I = {0: ((-1, 0), (0, 0), (1, 0), (2, 0)),
                      90: ((1, -1), (1, 0), (1, 1), (1, 2)),
                      180: ((-1, 1), (0, 1), (1, 1), (2, 1)),
                      270: ((0, -1), (0, 0), (0, 1), (0, 2)), }
colors = ("cyan", "blue", "orange", "yellow", "green", "purple", "red")
running = True
field = [[None] * FSIZE[0] for _ in range(FSIZE[1])]

now_pos = [4, 0]
angle = 0
now_color = random.choice(colors)
now_figure = random.choice(list(figures.items()))
next_color = random.choice(colors)
next_figure = random.choice(list(figures.items()))
speedup = False

grav_time = 5
grav_timer = 0

score = 0
high_score = 0


def collide(field, figure, pos):
    for px, py in figure[1]:
        x, y = pos[0] + px, pos[1] + py
        if x < 0 or x >= FSIZE[0] or y >= FSIZE[1]:
            return True
        if y >= 0 and field[y][x] is not None:
            return True


def new_figure():
    global now_figure, now_color, next_color, next_figure, now_pos, angle
    now_figure = next_figure
    now_color = next_color
    next_figure = random.choice(list(figures.items()))
    next_color = random.choice(colors)
    now_pos = [4, 0]
    angle = 0


def rotate_right90(figure, current_angle):
    if figure[0] == "O":
        return figure, current_angle
    current_angle = (current_angle + 90) % 360
    if figure[0] == "I":
        return (figure[0], figure_rotations_I[current_angle]), current_angle
    return (figure[0], tuple((-y, x) for x, y in figure[1])), current_angle


def check_line(field):
    global score
    for iy in range(FSIZE[1]):
        if all(field[iy]):
            score += 10
            field.pop(iy)
            field.insert(0, [None] * FSIZE[0])


def game_over():
    global field, next_color, next_figure, high_score, score, running
    _running = True
    rendered_text = font2.render(f"Press SPACE for restart", True, "white")
    screen.blit(rendered_text, ((WSIZE[0] - rendered_text.get_width()) // 2, 250))
    pg.display.flip()
    while _running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = _running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                _running = False
    high_score = max(high_score, score)
    score = 0
    field = [[None] * FSIZE[0] for _ in range(FSIZE[1])]
    next_color = random.choice(colors)
    next_figure = random.choice(list(figures.items()))
    new_figure()


while running:
    clock.tick(FPS)
    screen.fill("#18181B")
    field_w = FSIZE[0] * TSIZE
    rendered_title = font3.render(f"TETRIS", True, "white")
    rendered_score = font1.render(f"Score: {score}", True, "#FCD34D")
    rendered_high = font1.render(f"High: {high_score}", True, "#FCD34D")
    screen.blit(rendered_title, (field_w + 30, 20))
    screen.blit(rendered_score, (field_w + 10, 390))
    screen.blit(rendered_high, (field_w + 10, 430))
    # update user events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            new_pos = list(now_pos)
            _figure = now_figure
            if event.key == pg.K_RIGHT:
                new_pos[0] += 1
            elif event.key == pg.K_LEFT:
                new_pos[0] -= 1
            elif event.key == pg.K_DOWN:
                new_pos[1] += 1
            elif event.key == pg.K_SPACE:
                speedup = True
            elif event.key == pg.K_UP:
                _figure, angle = rotate_right90(now_figure, angle)
            if not collide(field, _figure, new_pos):
                now_pos = new_pos
                now_figure = _figure
    # draw field
    for y in range(FSIZE[1]):
        for x in range(FSIZE[0]):
            if field[y][x]:
                pg.draw.rect(screen, field[y][x], ((x * TSIZE, y * TSIZE), (TSIZE, TSIZE)))
    # draw current figure
    for point in now_figure[1]:
        pg.draw.rect(screen, now_color,
                     (((now_pos[0] + point[0]) * TSIZE, (now_pos[1] + point[1]) * TSIZE), (TSIZE, TSIZE)))
    # draw next figure
    for point in next_figure[1]:
        pg.draw.rect(screen, next_color,
                     (((FSIZE[0] + point[0] + 3) * TSIZE, (point[1] + 5) * TSIZE), (TSIZE, TSIZE)))
    # draw grid
    for y in range(FSIZE[1] + 1):
        # (156, 163, 175, 150)
        pg.draw.rect(screen, "#3F3F46", ((0, y * TSIZE), (FSIZE[0] * TSIZE, 1)))
    for x in range(FSIZE[0] + 1):
        pg.draw.rect(screen, "#3F3F46", ((x * TSIZE, 0), (1, FSIZE[1] * TSIZE)))
    # update gravity and collide
    if grav_timer <= 0 or speedup:
        if speedup:
            score += 1
        grav_timer = grav_time
        now_pos[1] += 1
        if collide(field, now_figure, now_pos):
            score += 10
            speedup = False
            for px, py in now_figure[1]:
                x, y = now_pos[0] + px, now_pos[1] + py - 1
                field[y][x] = now_color
            check_line(field)
            new_figure()
            if collide(field, now_figure, now_pos):
                game_over()
    else:
        grav_timer -= 1
    pg.display.flip()
