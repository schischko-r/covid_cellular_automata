from shutil import move
import numpy as np
import random
import platform
import os
import time


""" 
RULES:

STATUS: not infected | 1    | 
        vaccinated   | 2    | 

        incubation   | 4    |
        infected     | 5    | 

        recovered    | -1   | 
        dead         | -2   | 
        empty        | None |  

ALL CELLS ARE UNVACCINATED AT THE BEGINING
CHANCE OF VACCINATION BEGINS AT 5% AND RAISES BY THE RULE V *= sqrt(G), WHERE G IS GENERATION
VACCINATED CELLS HAVE LOWER CHANCE OF GETTING INFECTED

SOME AMOUNT OF CELLS GET INFECTED DURING 1ST GENERATION
INCUBATION PERIOD LASTS FOR 7 GENERATIONS
DURING THAT TIME CELLS HAVE LOWER CHANCE OF INFECTING OTHERS

ONCE CELL GETS FULLY INFECTED IT HAS 9 ITERATIONS TO RECOVER. 
DURING THAT PERIOD IT HAS A CONSTANT CHANCE OF DYING.

ONCE RECOVERED IT HAS "IMMUNITY" BUT HAS A CHANCE OF GETTING SICK AGAIN

ONCE THE MOVING IS IMPLEMENTED, WE MAY TRY TO RECREATE SOME COMPLEX BEHAVIOUR F.E. SOCIAL DISTANCING
"""
# TODO sort imports


class BColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Field:
    def __init__(self, size, perc_of_filled, perc_of_infected) -> None:
        self._SIZE = size
        self._GENERATION = 1
        self._MAX_ITERATION = 5

        self._POP = np.zeros((self._SIZE, self._SIZE))
        self._DATE_OF_INFECTION = np.zeros((self._SIZE, self._SIZE))

        self._POP[self._POP == 0] = None

        self._SLEEP_TIME = 1

        self.populate_field(perc_of_filled, perc_of_infected)

    def start_covid(self):
        for generation in range(self._MAX_ITERATION):
            self.iterate()

    def populate_field(self, perc_of_filled, perc_of_infected):
        cells_amount = int(round(self._SIZE**2 * perc_of_filled / 100, 0))

        try:
            for cell in range(cells_amount):
                self.populate_cell()
        except:
            print("All cells are filled")

        infected_amount = int(round(cells_amount * perc_of_infected / 100, 0))

        try:
            for cell in range(infected_amount):
                self.infect_cell()
        except:
            print("All cells are infected")

    def populate_cell(self):
        rand_layer = random.randint(0, self._SIZE - 1)
        rand_cell = random.randint(0, self._SIZE - 1)

        if self._POP[rand_layer][rand_cell] == 1:
            self.populate_cell()

        self._POP[rand_layer][rand_cell] = 1

    def infect_cell(self):
        rand_layer = random.randint(0, self._SIZE - 1)
        rand_cell = random.randint(0, self._SIZE - 1)

        if self._POP[rand_layer][rand_cell] == 1:
            self._POP[rand_layer][rand_cell] = 4
            self._DATE_OF_INFECTION[rand_layer][rand_cell] = self._GENERATION

        else:
            self.infect_cell()

    def iterate(self):
        self.print_population()
        self.spread_the_disease()
        self.move_cells()
        self._GENERATION += 1

    def spread_the_disease(self):
        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self._POP[i][j] == 1:
                    if self.neighbours(self._POP, i, j).any() == 4:
                        pass  # TODO CHANCE OF INF FROM INCUBATION

                    if self.neighbours(self._POP, i, j).any() == 5:
                        pass  # TODO CHANCE OF INF FROM INFECTED

    def move_cells(self):
        for i in range(self._SIZE):
            for j in range(self._SIZE):
                movement = random.randint(0, 4)
                # 0 MEANS NO MOVEMENT
                if movement == 1:
                    self.move_up(i, j)
                elif movement == 2:
                    self.move_down(i, j)
                elif movement == 3:
                    self.move_left(i, j)
                else:
                    self.move_right(i, j)

    def move_up(self, i, j):
        self._POP[i][j], self._POP[(i - 1) % self._SIZE][j] = (
            self._POP[(i - 1) % self._SIZE][j],
            self._POP[i][j],
        )
        (
            self._DATE_OF_INFECTION[i][j],
            self._DATE_OF_INFECTION[(i - 1) % self._SIZE][j],
        ) = (
            self._DATE_OF_INFECTION[(i - 1) % self._SIZE][j],
            self._DATE_OF_INFECTION[i][j],
        )

    def move_down(self, i, j):
        self._POP[i][j], self._POP[(i + 1) % self._SIZE][j] = (
            self._POP[(i + 1) % self._SIZE][j],
            self._POP[i][j],
        )
        (
            self._DATE_OF_INFECTION[i][j],
            self._DATE_OF_INFECTION[(i + 1) % self._SIZE][j],
        ) = (
            self._DATE_OF_INFECTION[(i + 1) % self._SIZE][j],
            self._DATE_OF_INFECTION[i][j],
        )

    def move_left(self, i, j):
        self._POP[i][j], self._POP[i][(j - 1) % self._SIZE] = (
            self._POP[i][(j - 1) % self._SIZE],
            self._POP[i][j],
        )
        (
            self._DATE_OF_INFECTION[i][j],
            self._DATE_OF_INFECTION[i][(j - 1) % self._SIZE],
        ) = (
            self._DATE_OF_INFECTION[i][(j - 1) % self._SIZE],
            self._DATE_OF_INFECTION[i][j],
        )

    def move_right(self, i, j):
        self._POP[i][j], self._POP[i][(j + 1) % self._SIZE] = (
            self._POP[i][(j + 1) % self._SIZE],
            self._POP[i][j],
        )
        (
            self._DATE_OF_INFECTION[i][j],
            self._DATE_OF_INFECTION[i][(j + 1) % self._SIZE],
        ) = (
            self._DATE_OF_INFECTION[i][(j + 1) % self._SIZE],
            self._DATE_OF_INFECTION[i][j],
        )

    def neighbours(self, x, i, j):
        return x[
            np.ix_(*((z - 1, z, z + 1 - S) for z, S in zip((i, j), x.shape)))
        ].ravel()

    def print_population(self):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

        print(f"\nGENERATION {self._GENERATION}\n")
        for line in self._POP:
            pretty_line = ""
            for pop in line:
                if np.isnan(pop):
                    pretty_line += " "
                else:
                    pretty_line += str(int(pop))
                pretty_line += "\t"
            print(pretty_line)

        time.sleep(self._SLEEP_TIME)


f = Field(size=10, perc_of_filled=20, perc_of_infected=5)
f.start_covid()
