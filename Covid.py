from cmath import inf
import math
import numpy as np
import os
import platform
import random
import time


"""
RULES: 

STATUS: not infected | 0    | ·
        infected     | 1    | I
        vaccinated   | 2    | V
        recovered    | -1   | +
        dead         | -2   | -
        empty        | None |  

CELL GETS INFECTED IF ANY OF HER NEIGHBOURS IS INFECTED
ONCE CELL GETS INFECTED IT SUFFERS AN IMMUNITY PENALTY
CELL HAS A CHANCE OF RECOVERING SPECIFIED BY HER IMMUNITY
CELL DIES AFTER 7 DAYS IF NOT RECOVERED
"""

# TODO написать коментики
# TODO ДОБАВИТЬ ДВИЖЕНИЕ


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


class Cell:
    def __init__(self, empty = False):
        if not empty:
            self.status = 0
            self.infected_iteration = None
            self.immunity = random.uniform(0, 1)


class Field:
    def __init__(self, size, infected_amount):
        self._SIZE = size

        self.isLarge = self._SIZE > 25

        self._MAX_ITERATIONS = 30
        self._DEATH_ITERATIONS = 7
        self._PENALTY = 0.2

        self._L_IMMUNITY_GAIN = 0.01
        self._L_IMMUNITY_V_GAIN = 0.01

        self._U_IMMUNITY_GAIN = 0.4
        self._U_IMMUNITY_V_GAIN = 0.5

        self._MAX_IM_TO_GET_INFECTED = 0.5
        self._VACCINATED_CHANCE = 0.05

        self._SLEEP_TIME = 1
        self.cells = np.round(np.random.rand(self._SIZE, self._SIZE))
        self.cells[self.cells == 0] = None

        for i in range(size):
            tmp = []
            for j in range(size):
                if self.cells:
                    tmp.append(Cell())
                else:
                    tmp.append(Cell(empty = True))
            self.cells.append(tmp)

        self.welcome()
        self.infect_field(infected_amount)

    def start_covid(self):
        for iter in range(self._MAX_ITERATIONS):
            self.print_field(iter)
            self.vaccinate()
            self.spread_the_disease(iter)
            self.recover_cells()
            self.kill_cells(iter)
            if not self.isLarge:
                time.sleep(self._SLEEP_TIME)

    def welcome(self):
        print("\n=======================================================")
        print("Welcome to the COVID game! Get ready to be infected!")
        print("Press any button to start!")
        print("=======================================================")
        input()

    def infect_field(self, amount):
        try:
            for cell in range(amount):
                self.infect_cell()
        except:
            print("\n== WARNING: Everybody's infected! ==\n")
            pass

    def infect_cell(self):
        rand_layer = random.randint(0, self._SIZE - 1)
        rand_cell = random.randint(0, self._SIZE - 1)

        if self.cells[rand_layer][rand_cell].status != 1:
            self.cells[rand_layer][rand_cell].status = 1
            self.cells[rand_layer][rand_cell].infected_iteration = 0

    def vaccinate(self):
        for layer in self.cells:
            for cell in layer:
                if cell.status == 0 or cell.status == -1:
                    chance = random.random()
                    if chance < self._VACCINATED_CHANCE:
                        cell.status = 2
                        cell.immunity += random.uniform(
                            self._L_IMMUNITY_V_GAIN, self._U_IMMUNITY_V_GAIN
                        )

    def spread_the_disease(self, iteration):
        # TODO убрать говнокод
        tmp_cells = self.cells
        statuses = []
        for layer in self.cells:
            tmp = []
            for cell in layer:
                tmp.append(cell.status)
            statuses.append(tmp)

        for i in range(self._SIZE):
            for j in range(self._SIZE):
                cell_neighbors = self.neighbours(np.array(statuses), i, j)

                for status in cell_neighbors:
                    if status == 1 and (
                        tmp_cells[i][j].status == 0
                        or tmp_cells[i][j].status == -1
                        or tmp_cells[i][j].status == 2
                    ):
                        if tmp_cells[i][
                            j
                        ].immunity < self._MAX_IM_TO_GET_INFECTED * math.log(
                            cell_neighbors.tolist().count(1)
                        ):
                            tmp_cells[i][j].status = 1
                            tmp_cells[i][j].immunity -= random.uniform(0, self._PENALTY)
                            tmp_cells[i][j].infected_iteration = iteration

        self.cells = tmp_cells

    def recover_cells(self):
        for layer in self.cells:
            for cell in layer:
                if cell.status == 1:
                    chance = random.random()
                    if cell.immunity > chance:
                        cell.status = -1
                        cell.immunity += random.uniform(
                            self._L_IMMUNITY_GAIN, self._U_IMMUNITY_GAIN
                        )

    def kill_cells(self, iteration):
        for layer in self.cells:
            for cell in layer:
                if cell.status == 1:
                    if iteration - cell.infected_iteration > self._DEATH_ITERATIONS:
                        cell.status = -2

    def SLAAAY(self):
        # This function slays
        print("SLÆAAAAAAAAĀAÀÂÄAAAÆYYYŸ")

    def neighbours(self, x, i, j):
        return x[
            np.ix_(*((z - 1, z, z + 1 - S) for z, S in zip((i, j), x.shape)))
        ].ravel()

    def print_stats(self):
        not_infected = 0
        vaccinated = 0
        infected = 0
        recovered = 0
        dead = 0

        for line in self.cells:
            for cell in line:
                if cell.status == 0:
                    not_infected += 1
                elif cell.status == 1:
                    infected += 1
                elif cell.status == 2:
                    vaccinated += 1
                elif cell.status == -1:
                    recovered += 1
                elif cell.status == -2:
                    dead += 1

        print()
        print(
            BColors.HEADER
            + "NOT INFECTED"
            + BColors.ENDC
            + f"\t{round(not_infected/(self._SIZE ** 2) * 100, 2)}%"
        )
        print(
            BColors.HEADER
            + "VACCINATED"
            + BColors.ENDC
            + f"\t{round(vaccinated/(self._SIZE ** 2) * 100, 2)}%"
        )
        print(
            BColors.HEADER
            + "INFECTED"
            + BColors.ENDC
            + f"\t{round(infected/(self._SIZE ** 2) * 100, 2)}%"
        )
        print(
            BColors.HEADER
            + "RECOVERED"
            + BColors.ENDC
            + f"\t{round(recovered/(self._SIZE ** 2) * 100, 2)}%"
        )
        print(
            BColors.HEADER
            + "DEAD"
            + BColors.ENDC
            + f"\t\t{round(dead/(self._SIZE ** 2) * 100, 2)}%"
        )

    def print_field(self, iter):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

        printedArr = []
        for line in self.cells:
            tmp = []
            for cell in line:
                if cell.status == -2:
                    tmp.append(BColors.ENDC + "-")
                elif cell.status == 1:
                    tmp.append(BColors.FAIL + "☣️")
                elif cell.status == 2:
                    tmp.append(BColors.WARNING + "V")
                elif cell.status == 0:
                    tmp.append(BColors.OKBLUE + "·")
                else:
                    tmp.append(BColors.OKGREEN + "+")

            printedArr.append(tmp)

        print(BColors.HEADER + f"\nITERATION {iter}\n")

        if not self.isLarge:
            print(
                "\n".join(
                    ["\t".join([str(cell) for cell in row]) for row in printedArr]
                )
            )
        self.print_stats()


f = Field(size=10, infected_amount=1)
f.start_covid()
