import bisect
import sys
from collections import deque
from random import choice
from time import perf_counter as tpc
from typing import Tuple, Dict, NamedTuple

import pygame

GameSettings = NamedTuple('GameSettings', [('caption', str), ('fps', int), ('fontpath', str), ('fontsize', int)])
SnakeProps = NamedTuple('SnakeProps', [('pos', Tuple[int, int]), ('length', int), ('direction', str), ('speed', int)])

SCORES: Tuple[int, ...] = (150, 300, 500, 750, 1100, 1500, 2000, 2500)
GEOMETRY: Dict[str, int] = dict(width=720, height=480, grid=24, nx=20, ny=20)
MOTIONS: Dict[str, Tuple[int, int]] = dict(right=(1, 0), left=(-1, 0), up=(0, -1), down=(0, 1))
COLORS: Dict[str, int] = dict(snake=0x00cccc, food=0xffff00, bg=0x0, border=0xffffff, info=0x00ff00, warning=0xff0000)
DIRECTIONS: Dict[int, str] = {pygame.K_j: 'left', pygame.K_l: 'right', pygame.K_i: 'up', pygame.K_k: 'down'}
SETTINGS = GameSettings('Snake Game v1.0', 60, 'assets/fonts/RobotWorldItalic.ttf', 25)
SNAKE_PROPS = SnakeProps(pos=(8, 5), length=3, direction=choice(['up', 'down', 'left', 'right']), speed=4)


def convert_color(x: int) -> Tuple[int, int, int]:
    """Convert hex format into tuple format.

    >>> convert_color(0xffffff)
    (255, 255, 255)
    >>> convert_color(0x1c0f11)
    (28, 15, 17)
    >>> convert_color(0xccccffffff)
    (255, 255, 255)
    """
    return (x & 0xff0000) >> 16, (x & 0xff00) >> 8, (x & 0xff)


def pos_to_rect(pos: Tuple[int, int], size: int) -> Tuple[int, int, int, int]:
    """Convert position into rectangle.

    >>> pos_to_rect((1, 2), 24)
    (24, 48, 24, 24)
    >>> pos_to_rect((20, 10), 24)
    (480, 240, 24, 24)
    """
    return pos[0] * size, pos[1] * size, size, size


class Snake:
    """Class for snake controls.

    >>> snake = Snake(pos=(8, 5), length=3, direction='right', speed=4)
    >>> snake.grids[0], snake.grids[1]
    ((8, 5), (7, 5))
    >>> snake.move()
    >>> snake.grids[0]
    (9, 5)
    >>> snake.set_direction('left')
    >>> snake.direction
    'right'
    >>> snake.set_direction('down')
    >>> snake.direction
    'down'
    >>> snake.move()
    >>> snake.grids[0], snake.target
    ((9, 6), (9, 7))
    >>> snake.alive
    True
    """
    __slots__ = ['grids', 'speed', 'direction']

    def __init__(self, pos: Tuple[int, int], length: int, speed: int, direction: str) -> None:
        self.speed: int = speed
        self.direction: str = direction

        motion = MOTIONS[direction]
        if direction in {'left', 'right'}:
            self.grids = deque([(x, pos[1]) for x in range(pos[0], pos[0] - length * motion[0], -motion[0])])
        else:
            self.grids = deque([(pos[0], y) for y in range(pos[1], pos[1] - length * motion[1], -motion[1])])

    def draw(self, screen: pygame.surface.Surface) -> None:
        for grid in self.grids:
            pygame.draw.rect(screen, COLORS['snake'], pos_to_rect(grid, size=GEOMETRY['grid']))

        if not self.alive:
            pygame.draw.rect(screen, COLORS['warning'], pos_to_rect(self.grids[0], size=GEOMETRY['grid']))

    def move(self) -> None:
        x, y = self.target
        if 0 <= x < GEOMETRY['nx'] and 0 <= y < GEOMETRY['ny']:
            self.grids.appendleft((x, y))
            self.grids.pop()
        else:
            self.grids.appendleft(self.grids[0])

    @property
    def target(self) -> Tuple[int, int]:
        motion = MOTIONS[self.direction]
        return self.grids[0][0] + motion[0], self.grids[0][1] + motion[1]

    def eat(self) -> None:
        self.grids.appendleft(self.target)

    def set_direction(self, direction: str) -> None:
        neck_direction = [self.grids[0][i] - self.grids[1][i] for i in range(2)]
        if any(neck_direction[i] + MOTIONS[direction][i] for i in range(2)):
            self.direction = direction

    @property
    def alive(self) -> bool:
        return len(set(self.grids)) == len(self.grids)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(SETTINGS.caption)
        self.ttf = pygame.font.Font(SETTINGS.fontpath, SETTINGS.fontsize)
        self.screen = pygame.display.set_mode((GEOMETRY['width'], GEOMETRY['height']))
        self.snake: Snake = Snake(**SNAKE_PROPS._asdict())
        self.food: Tuple[int, int] = (0, 0)
        self.score: int = 0
        self.reset()

    def reset(self) -> None:
        self.snake, self.score = Snake(**SNAKE_PROPS._asdict()), 0
        self.generate_food()

    def generate_food(self) -> None:
        foods = [(x, y) for x in range(GEOMETRY['nx']) for y in range(GEOMETRY['ny']) if (x, y) not in self.snake.grids
                 and any([x not in (0, GEOMETRY['nx'] - 1), y not in (0, GEOMETRY['ny'] - 1)])]
        self.food = choice(foods)

    def run(self) -> None:
        clock = pygame.time.Clock()
        start_time = tpc()
        bg, border, food, info, warning = [convert_color(COLORS[x]) for x in 'bg border food info warning'.split()]
        boundary_x, boundary_y = GEOMETRY['grid'] * GEOMETRY['nx'], GEOMETRY['height']

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.check_keydown_events(event)

            self.screen.fill(bg)
            pygame.draw.line(self.screen, border, (boundary_x, 0), (boundary_x, boundary_y))
            self.snake.draw(self.screen)
            pygame.draw.rect(self.screen, food, pos_to_rect(self.food, GEOMETRY['grid']))

            if self.snake.alive:
                if tpc() - start_time > 1.0 / self.snake.speed:
                    self.snake.move()
                    start_time = tpc()
            else:
                self.screen.blit(self.ttf.render('game over', True, warning), (130, 200))
                self.screen.blit(self.ttf.render('press \'enter\' to continue', True, warning), (30, 250))

            self.screen.blit(self.ttf.render(f'Scores: {self.score}', True, info), (510, 20))
            self.screen.blit(self.ttf.render(f'Speed: {self.snake.speed}', True, info), (510, 60))

            if self.snake.grids[0] == self.food:
                self.snake.eat()
                self.score += 50
                self.snake.speed = bisect.bisect(SCORES, self.score) + SNAKE_PROPS.speed
                self.generate_food()

            pygame.display.flip()
            clock.tick(SETTINGS.fps)

    def check_keydown_events(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_q:
            sys.exit(0)
        elif event.key in DIRECTIONS:
            self.snake.set_direction(DIRECTIONS[event.key])
        elif event.key == pygame.K_RETURN and not self.snake.alive:
            self.reset()


if __name__ == '__main__':
    Game().run()
