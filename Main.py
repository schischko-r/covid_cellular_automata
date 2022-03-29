from re import X
from matplotlib.pyplot import ylim
import pygame
import sys
import math

from Field import Field, CellStatus, CellBehaviour


class Game:
    def __init__(self, size, perc_of_filled, perc_of_infected, window_width):
        # Colors
        self.GUNMETAL = (34, 56, 67)
        self.CULTURED = (239, 241, 243)
        self.LIGHT_GRAY = (219, 211, 216)
        self.TUMBLE_WEED = (216, 180, 160)
        self.TERRA_COTTA = (215, 122, 97)
        self.BLACK_CORAL = (94, 101, 114)
        self.PURE_CERULEAN = (144, 194, 231)
        self.GREEN_SHEEN = (112, 169, 161)
        self.TEAL_BLUE = (64, 121, 140)
        self.AUBURN = (158, 42, 43)
        self.ROSEWOOD = (84, 11, 14)

        self._SLEEP_TIME = 0.01

        self.field = Field(
            size=size,
            perc_of_filled=perc_of_filled,
            perc_of_infected=perc_of_infected,
            sleep_time=self._SLEEP_TIME,
        )
        self.blockSize = math.floor(window_width / self.field._SIZE)

        self.WINDOW_HEIGHT = self.blockSize * self.field._SIZE
        self.WINDOW_WIDTH = self.blockSize * self.field._SIZE

        global SCREEN, CLOCK
        pygame.init()
        SCREEN = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        CLOCK = pygame.time.Clock()

        self.start()

        while True:
            self.drawGrid()
            self.iterate()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    self.stop()
                    pos = pygame.mouse.get_pos()
                    i, j = self.get_field_indexes(pos[0], pos[1])
                    self.print_info(i, j)
                    self.highlight_home_and_job(i, j)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.running:
                            self.stop()
                        else:
                            self.start()

            pygame.display.update()

    def start(self):
        self.running = True
        self.highlighting = False
        self.field.clear()

    def stop(self):
        self.running = False
        self.highlighting = False

    def iterate(self):
        if self.running:
            self.field.iterate_covid()

    def drawGrid(self):
        SCREEN.fill(self.GUNMETAL)
        for x in range(0, self.WINDOW_WIDTH, self.blockSize):
            for y in range(0, self.WINDOW_HEIGHT, self.blockSize):
                i, j = self.get_field_indexes(x, y)

                rect = pygame.Rect(x, y, self.blockSize, self.blockSize)
                if self.field._POP[i][j]:
                    if self.field._POP[i][j][0] == CellStatus.not_infected.value:
                        pygame.draw.rect(SCREEN, self.CULTURED, rect)

                    elif self.field._POP[i][j][0] == CellStatus.incubation.value:
                        pygame.draw.rect(SCREEN, self.TUMBLE_WEED, rect)

                    elif self.field._POP[i][j][0] == CellStatus.infected.value:
                        pygame.draw.rect(SCREEN, self.TERRA_COTTA, rect)

                    elif self.field._POP[i][j][0] == CellStatus.dead.value:
                        pygame.draw.rect(SCREEN, self.BLACK_CORAL, rect)

                    elif self.field._POP[i][j][0] == CellStatus.vaccinated.value:
                        pygame.draw.rect(SCREEN, self.PURE_CERULEAN, rect)

                    elif self.field._POP[i][j][0] == CellStatus.recovered.value:
                        pygame.draw.rect(SCREEN, self.GREEN_SHEEN, rect)
                else:
                    pygame.draw.rect(SCREEN, self.TEAL_BLUE, rect, 1)

        if self.highlighting:
            if self.field._POP[self.highlighted_i][self.highlighted_j]:
                x, y = self.get_block_coordinates(
                    self.field._POP[self.highlighted_i][self.highlighted_j][10][0],
                    self.field._POP[self.highlighted_i][self.highlighted_j][10][1],
                )
                rect = pygame.Rect(x, y, self.blockSize, self.blockSize)
                pygame.draw.rect(SCREEN, self.AUBURN, rect, 0)

                x, y = self.get_block_coordinates(
                    self.field._POP[self.highlighted_i][self.highlighted_j][11][0],
                    self.field._POP[self.highlighted_i][self.highlighted_j][11][1],
                )
                rect = pygame.Rect(x, y, self.blockSize, self.blockSize)
                pygame.draw.rect(SCREEN, self.ROSEWOOD, rect, 0)

    def get_field_indexes(self, x, y):
        i = int(x / self.blockSize)
        j = int(y / self.blockSize)
        return i, j

    def get_block_coordinates(self, i, j):
        x = int(i * self.blockSize)
        y = int(j * self.blockSize)
        return x, y

    def highlight_home_and_job(self, i, j):
        self.highlighting = True
        self.highlighted_i = i
        self.highlighted_j = j

    def print_info(self, i, j):
        self.field.clear()
        print(f"== CELL {i}, {j} ==")
        if self.field._POP[i][j]:
            print(f"AGE: {self.field._POP[i][j][12]}")
            print(f"STATUS: {CellStatus(self.field._POP[i][j][0]).name}")
            print(f"== BASE IMMUNITY: {self.field._POP[i][j][1]}")
            print(f"== PENALTIES: {sum(self.field._POP[i][j][6])}")
            print(f"== REWARDS: {sum(self.field._POP[i][j][7])}")
            print(f"CALC IMMUNITY: {self.field.calc_immunity(i,j)}")
            print(f"DATE OF INFECTION: {self.field._POP[i][j][3]}")
            print(f"INCUBATION DURATION: {self.field._POP[i][j][4]}")
            print(f"INFECTION DURATION: {self.field._POP[i][j][5]}")

            print("========= DEBUG =========")
            print(f"BEHAVIOUR: {CellBehaviour(self.field._POP[i][j][2][0]).name}")
            print(f"PATH LENGTH: {len(self.field._POP[i][j][2][1])}")
            print(f"PATH: {self.field._POP[i][j][2][1]}")
            print(f"RACHED: {self.field._POP[i][j][2][2]}")
            print(f"HOUSE: {self.field._POP[i][j][10]}")
            print(f"JOB: {self.field._POP[i][j][11]}")
            print(f"DATE OF DEATH: {self.field._POP[i][j][9]}")

        else:
            print("TYPE: EMPTY")


g = Game(size=25, perc_of_filled=20, perc_of_infected=20, window_width=600)
