import pygame
import sys

"""
DUMMY
DUMMY
DUMMY
DUMMY
DUMMY
DUMMY
DUMMY
DUMMY
DUMMY
DONT START
KILLS FAMILIES
DESTROYES LIVES
DUMMY
DUMMY
DUMMY
DUMMY

"""


class Game:
    def __init__(self):
        self.BLACK = (0, 0, 0)
        self.WHITE = (200, 200, 200)
        self.WINDOW_HEIGHT = 400
        self.WINDOW_WIDTH = 400

        global SCREEN, CLOCK
        pygame.init()
        SCREEN = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        CLOCK = pygame.time.Clock()
        SCREEN.fill(self.BLACK)

        while True:
            self.drawGrid()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

    def drawGrid(self):
        blockSize = 20  # Set the size of the grid block
        for x in range(0, self.WINDOW_WIDTH, blockSize):
            for y in range(0, self.WINDOW_HEIGHT, blockSize):
                rect = pygame.Rect(x, y, blockSize, blockSize)
                pygame.draw.rect(SCREEN, self.WHITE, rect, 1)


g = Game()
