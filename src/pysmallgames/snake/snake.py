import random
import sys
from collections import deque, namedtuple
from time import perf_counter as pc

import pygame
import yaml

SnakeColor = namedtuple('SnakeColor', 'head mid tail')
SnakeMotion = namedtuple('SnakeMotion', 'right left up down')
SnakeInfo = namedtuple('SnakeInfo', 'direction size speed border score')
GameText = namedtuple('GameText', 'condition content color pos')
DIRECTIONS = {pygame.K_LEFT: 'left', pygame.K_RIGHT: 'right', pygame.K_UP: 'up', pygame.K_DOWN: 'down'}


def pos_to_rect(x: int, y: int, size: int):
    return x * size, y * size, size, size


class Snake:
    COLORS = SnakeColor(head=(120, 255, 60), mid=(140, 200, 60), tail=(80, 120, 70))
    MOTIONS = SnakeMotion(right=(1, 0), left=(-1, 0), up=(0, -1), down=(0, 1))

    def __init__(self, pos: list, length: int, size: int, speed: int, border: list, direction: str):
        motion = self.MOTIONS._asdict().get(direction)
        if direction in {'left', 'right'}:
            self.grids = deque([(x, pos[1]) for x in range(pos[0], pos[0] - length * motion[0], -motion[0])])
        else:
            self.grids = deque([(pos[0], y) for y in range(pos[1], pos[1] - length * motion[1], -motion[1])])
        self.info = SnakeInfo(direction=direction, size=size, speed=speed, border=border, score=0)

    def draw(self, screen: pygame.surface.Surface):
        for i, grid in enumerate(self.grids):
            if i in (0, len(self.grids) - 1):
                color = {0: self.COLORS.head, len(self.grids) - 1: self.COLORS.tail}.get(i)
            else:
                color = self.COLORS.mid
            pygame.draw.rect(screen, color, pos_to_rect(*grid, size=self.info.size))

    def move(self):
        motion = self.MOTIONS._asdict().get(self.info.direction)
        x, y = self.grids[0][0] + motion[0], self.grids[0][1] + motion[1]
        if 0 <= x < self.info.border[0] and 0 <= y <= self.info.border[1]:
            self.grids.appendleft((x, y))
            self.grids.pop()
        else:
            self.grids.appendleft(self.grids[0])

    def change_direction(self, direction: str):
        head_direction = [self.grids[0][i] - self.grids[1][i] for i in range(2)]
        if any(head_direction[i] + self.MOTIONS._asdict().get(direction)[i] for i in range(2)):
            self.info = SnakeInfo(direction, self.info.size, self.info.speed, self.info.border, self.info.score)

    def alive(self):
        return len(set(self.grids)) == len(self.grids)


class Game:
    def __init__(self, config_file: str):
        with open(config_file, encoding='utf-8') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
            self.colors: dict = self.config['colors']

        pygame.init()
        pygame.display.set_caption(self.config['caption'])
        self.ttf = pygame.font.Font(self.config['font']['name'], self.config['font']['size'])
        self.screen = pygame.display.set_mode(self.config['geometry']['win_size'])
        self.snake, self.messages, self.foods, self.food = None, None, [], None
        self.reset()

    def reset(self):
        self.snake = Snake(**self.config['snake_init'])
        self.messages = {
            'score': GameText(lambda: False, f'Scores: {self.snake.info.score}', self.colors['info'], (510, 20)),
            'speed': GameText(lambda: False, f'Speed: {self.snake.info.speed}', self.colors['info'], (510, 60)),
            'game_over': GameText(self.snake.alive, 'Game Over!', self.colors['warning'], (130, 200)),
            'continue': GameText(self.snake.alive, 'Press Enter To Continue', self.colors['warning'], (30, 250))
        }

    def run(self):
        fps = self.config['fps']
        clock = pygame.time.Clock()
        start_time = pc()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.check_keydown_events(event)

            self.screen.fill(self.colors['bg'])
            pygame.draw.line(self.screen, self.colors['border'], **self.config['lines']['score'])
            if self.snake.alive() and pc() - start_time > 1.0 / self.snake.info.speed:
                self.snake.move()
                start_time = pc()

            for k, v in self.messages.items():
                if not v.condition():
                    self.screen.blit(self.ttf.render(v.content, True, v.color), v.pos)

            self.snake.draw(self.screen)
            pygame.display.flip()
            clock.tick(fps)

    def check_keydown_events(self, event):
        if event.key == pygame.K_q:
            sys.exit(0)
        elif event.key in DIRECTIONS:
            self.snake.change_direction(DIRECTIONS[event.key])
        elif event.key == pygame.K_RETURN and not self.snake.alive():
            self.reset()


if __name__ == '__main__':
    game = Game('config.yaml')
    game.run()
