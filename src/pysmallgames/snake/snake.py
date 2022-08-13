import bisect
import random
import sys
from collections import deque
from time import perf_counter as pc

import pygame

SNAKE_INIT = dict(pos=(8, 5), length=5, speed=4, direction='right', score=0)
COLORS = dict(snake=0xff00ff, food=0xffff00, bg=0x0, border=0xffffff, info=0xff0000, warning=0xffff00)
MOTIONS = dict(right=(1, 0), left=(-1, 0), up=(0, -1), down=(0, 1))
GEOMETRY = dict(width=720, height=480, grid=24, nx=20, ny=20)
SETTINGS = dict(caption='Snake Game v1.0', fps=60, font_name='assets/fonts/RobotWorldItalic.ttf', font_size=25)
DIRECTIONS = {pygame.K_j: 'left', pygame.K_l: 'right', pygame.K_i: 'up', pygame.K_k: 'down'}
SCORES = (150, 300, 500, 750, 1100, 1500, 2000, 2500)


def pos_to_rect(x: int, y: int, size: int):
    return x * size, y * size, size, size


class Snake:
    def __init__(self, pos: list, length: int, speed: int, direction: str, score: int):
        motion = MOTIONS[direction]
        if direction in {'left', 'right'}:
            self.grids = deque([(x, pos[1]) for x in range(pos[0], pos[0] - length * motion[0], -motion[0])])
        else:
            self.grids = deque([(pos[0], y) for y in range(pos[1], pos[1] - length * motion[1], -motion[1])])
        self.prop = dict(pos=pos, length=length, speed=speed, direction=direction, score=score)

    def draw(self, screen: pygame.surface.Surface):
        for grid in self.grids:
            pygame.draw.rect(screen, COLORS['snake'], pos_to_rect(*grid, size=GEOMETRY['grid']))

    def move(self):
        motion = MOTIONS[self.prop['direction']]
        x, y = self.grids[0][0] + motion[0], self.grids[0][1] + motion[1]
        if 0 <= x < GEOMETRY['nx'] and 0 <= y < GEOMETRY['ny']:
            self.grids.appendleft((x, y))
            self.grids.pop()
        else:
            self.grids.appendleft(self.grids[0])

    def eat(self):
        motion = MOTIONS[self.prop['direction']]
        self.grids.appendleft((self.grids[0] + motion[0], self.grids[0][1] + motion[1]))
        self.prop['score'] = self.prop['score'] + 50
        self.prop['speed'] = bisect.bisect(SCORES, self.prop['score']) + SNAKE_INIT['speed']

    def change_direction(self, direction: str):
        head_direction = [self.grids[0][i] - self.grids[1][i] for i in range(2)]
        if any(head_direction[i] + MOTIONS[direction][i] for i in range(2)):
            self.prop['direction'] = direction

    def alive(self):
        return len(set(self.grids)) == len(self.grids)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(SETTINGS['caption'])
        self.ttf = pygame.font.Font(SETTINGS['font_name'], SETTINGS['font_size'])
        self.screen = pygame.display.set_mode((GEOMETRY['width'], GEOMETRY['height']))
        self.snake, self.messages, self.food = None, None, None
        self.reset()

    def reset(self):
        self.snake = Snake(**SNAKE_INIT)
        self.generate_food()

    def generate_food(self):
        foods = [(x, y) for x in range(GEOMETRY['nx']) for y in range(GEOMETRY['ny']) if (x, y) not in self.snake.grids]
        self.food = random.choice(foods)

    def run(self):
        clock = pygame.time.Clock()
        start_time = pc()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.check_keydown_events(event)

            self.screen.fill(COLORS['bg'])
            pygame.draw.line(self.screen, COLORS['border'], (480, 0), (480, 480))
            self.snake.draw(self.screen)
            pygame.draw.rect(self.screen, COLORS['food'], pos_to_rect(*self.food, GEOMETRY['grid']))

            if self.snake.alive():
                if pc() - start_time > 1.0 / self.snake.prop['speed']:
                    self.snake.move()
                    start_time = pc()
            else:
                self.screen.blit(self.ttf.render('game over', True, COLORS['warning']), (130, 200))
                self.screen.blit(self.ttf.render('press \'enter\' to continue', True, COLORS['warning']), (30, 250))

            self.screen.blit(self.ttf.render(f'Scores: {self.snake.prop["score"]}', True, COLORS['info']), (510, 20))
            self.screen.blit(self.ttf.render(f'Speed: {self.snake.prop["speed"]}', True, COLORS['info']), (510, 60))

            if self.snake.grids[0] == self.food:
                self.snake.eat()
                self.generate_food()

            pygame.display.flip()
            clock.tick(SETTINGS['fps'])

    def check_keydown_events(self, event):
        if event.key == pygame.K_q:
            sys.exit(0)
        elif event.key in DIRECTIONS:
            self.snake.change_direction(DIRECTIONS[event.key])
        elif event.key == pygame.K_RETURN and not self.snake.alive():
            self.reset()


if __name__ == '__main__':
    Game().run()
