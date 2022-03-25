import enum
import math
import numpy as np
import os, platform
import random
import time
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


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


class CellStatus(enum.Enum):
    not_infected = 1
    vaccinated = 2
    incubation = 4
    infected = 5
    recovered = -1
    dead = -2
    empty = None


class CellBehaviour(enum.Enum):
    random = 0
    heading_home = 1
    heading_to_work = 2


class Field:
    def __init__(self, size, perc_of_filled, perc_of_infected, sleep_time) -> None:
        self._SIZE = size
        self._GENERATION = 1
        self._MAX_ITERATION = 500
        self._SLEEP_TIME = sleep_time

        self._MIN_FAMILY_SIZE = 1
        self._MAX_FAMILY_SIZE = 8

        self._MIN_AGE = 5
        self._MAX_AGE = 90

        self._VACCINATION_BASE_ATTRACTIVENESS = 5e-3
        self._VACCINATION_ATTRACTIVENESS = 1e-4

        self._L_INIT_IMMUNITY = 0.2
        self._U_INIT_IMMUNITY = 0.5

        self._L_INF_FROM_INCUBATED_CHANCE = 0.4
        self._U_INF_FROM_INCUBATED_CHANCE = 0.6

        self._L_INF_FROM_SICK_CHANCE = 0.6
        self._U_INF_FROM_SICK_CHANCE = 0.95

        self._L_INC_DURATION = 3
        self._U_INC_DURATION = 9

        self._L_INF_DURATION = 0
        self._U_INF_DURATION = 14

        self._SICKNESS_PENALTY = 0.2
        self._CURE_IMMUNITY = 0.2
        self._VACC_IMMUNITY = 0.3

        self._CLEANING_TIME = 3

        self._DEATHS = 1

        self._CHANGING_BEHAVIOUR_LIKENESS = 0.1

        self.init_pops(perc_of_filled, perc_of_infected)

    def init_pops(self, perc_of_filled, perc_of_infected):
        self._POP = [[None for y in range(self._SIZE)] for x in range(self._SIZE)]
        self.family_houses = []
        self.jobs = []

        cells_amount = int(round(self._SIZE**2 * perc_of_filled / 100, 0))
        families = math.floor(
            cells_amount / random.randint(self._MIN_FAMILY_SIZE, self._MAX_FAMILY_SIZE)
        )

        for family in range(families):
            self.family_houses.append(
                (random.randint(0, self._SIZE - 1), random.randint(0, self._SIZE - 1))
            )
            self.jobs.append(
                (random.randint(0, self._SIZE - 1), random.randint(0, self._SIZE - 1))
            )

            for cell in range(math.floor(cells_amount / families)):
                self.populate_cell(family)

        populated = []
        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self._POP[i][j] != None:
                    populated.append((i, j))

        infected_amount = int(round(cells_amount * perc_of_infected / 100, 0))
        infected = random.sample(populated, k=infected_amount)
        for cell in infected:
            self.incubate_cell(cell[0], cell[1])

    def iterate_covid(self):
        self._GENERATION += 1
        # if self._SIZE > 15:
        #     self.plot_population()
        # else:
        #     self.print_population()

        self.movement_behaviour()
        self.vaccinate()
        self.spread_the_disease()
        self.turn_inc_into_inf()
        self.cure_cells()
        self.kill_dying_cells()
        self.clean_field()
        time.sleep(self._SLEEP_TIME)

    def populate_cell(self, family_id):
        rand_layer = random.randint(0, self._SIZE - 1)
        rand_cell = random.randint(0, self._SIZE - 1)

        if not self._POP[rand_layer][rand_cell]:
            self._POP[rand_layer][rand_cell] = [
                CellStatus.not_infected.value,  # STATUS
                random.uniform(
                    self._L_INIT_IMMUNITY, self._U_INIT_IMMUNITY
                ),  # IMMUNITY
                [CellBehaviour.random.value, [], False],  # BEHAVIOUR
                None,  # DATE OF INFECTION
                None,  # INCUBATION DURATION
                None,  # INFECTION DURATION
                [],  # PENALTIES
                [],  # REWARDS
                family_id,  # FAMILY
                None,  # DATE OF DEATH
                self.family_houses[family_id],  # HOUSE
                self.jobs[family_id],  # WORK
                random.randint(self._MIN_AGE, self._MAX_AGE),  # AGE
            ]
        else:
            self.populate_cell(family_id)

    def incubate_cell(self, i, j):
        if self._POP[i][j]:
            self._POP[i][j][0] = CellStatus.incubation.value
            self._POP[i][j][3] = self._GENERATION
            self._POP[i][j][4] = math.floor(
                self._L_INC_DURATION
                + (self._U_INC_DURATION - self._L_INC_DURATION)
                * math.cos(math.pi * self.calc_immunity(i, j) / 2)
            )
            self._POP[i][j][5] = math.floor(
                self._L_INF_DURATION
                + (self._U_INF_DURATION - self._L_INF_DURATION)
                * math.cos(math.pi * self.calc_immunity(i, j) / 2)
            )
            self._POP[i][j][6].append(self._SICKNESS_PENALTY)

    def infect_cell(self, i, j):
        if self._POP[i][j]:
            self._POP[i][j][0] = CellStatus.incubation.value
            self._POP[i][j][3] = self._GENERATION
            self._POP[i][j][4] = math.floor(
                self._L_INC_DURATION
                + (self._U_INC_DURATION - self._L_INC_DURATION)
                * math.cos(math.pi * self.calc_immunity(i, j) / 2)
            )
            self._POP[i][j][5] = math.floor(
                self._L_INF_DURATION
                + (self._U_INF_DURATION - self._L_INF_DURATION)
                * math.cos(math.pi * self.calc_immunity(i, j) / 2)
            )

    def kill_cell(self, i, j):
        if self._POP[i][j]:
            self._POP[i][j][0] = CellStatus.dead.value
            self._POP[i][j][9] = self._GENERATION
            self._DEATHS += 1

    def vaccinate_cell(self, i, j):
        if self._POP[i][j]:
            self._POP[i][j][0] = CellStatus.vaccinated.value
            self._POP[i][j][7].append(self._VACC_IMMUNITY)

    def calc_immunity(self, i, j):
        return (
            self._POP[i][j][1]
            * (2.5 / math.sqrt(2 * math.pi))
            * math.exp(-((2 * self._POP[i][j][12] - 1) ** 2))
            + sum(self._POP[i][j][7])
            - sum(self._POP[i][j][6])
        )

    def vaccinate(self):
        self.update_statuses()

        self._VACCINATION_ATTRACTIVENESS = (
            self._VACCINATION_BASE_ATTRACTIVENESS * self._DEATHS
        )

        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self.statuses[i][j] and (
                    self.statuses[i][j] == CellStatus.not_infected.value
                    or self.statuses[i][j] == CellStatus.recovered.value
                ):
                    chance = random.random()
                    if self._VACCINATION_ATTRACTIVENESS > chance:
                        self.vaccinate_cell(i, j)

    def turn_inc_into_inf(self):
        self.update_statuses()
        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self.statuses[i][j] and (
                    self.statuses[i][j] == CellStatus.incubation.value
                ):
                    if self._GENERATION - self._POP[i][j][3] > self._POP[i][j][4]:
                        self._POP[i][j][0] = CellStatus.infected.value
                    else:
                        self._POP[i][j][1] -= sum(self._POP[i][j][6]) / (
                            self._GENERATION + 1 - self._POP[i][j][3]
                        )

    def cure_cells(self):
        self.update_statuses()
        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self.statuses[i][j] and (
                    self.statuses[i][j] == CellStatus.infected.value
                ):
                    if (
                        self._GENERATION - self._POP[i][j][3] - self._POP[i][j][4]
                        > self._POP[i][j][5]
                    ):
                        self._POP[i][j][0] = CellStatus.recovered.value
                        self._POP[i][j][7].append(self._CURE_IMMUNITY)
                    else:
                        self._POP[i][j][1] += sum(self._POP[i][j][6]) / (
                            self._GENERATION
                            - self._POP[i][j][3]
                            - self._POP[i][j][4]
                            + 1
                        )

    def kill_dying_cells(self):
        self.update_statuses()
        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if (
                    self.statuses[i][j]
                    and self.statuses[i][j] == CellStatus.infected.value
                ):
                    chance_of_dying = (
                        math.cos(math.pi * self.calc_immunity(i, j) / 2) ** 5
                    )
                    if chance_of_dying > 0:
                        chance = random.random()
                        if chance < chance_of_dying:
                            self.kill_cell(i, j)
                    if self._POP[i][j][1] < 0:
                        self.kill_cell(i, j)

    def clean_field(self):
        self.update_statuses()
        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self.statuses[i][j] and self.statuses[i][j] == CellStatus.dead.value:
                    if self._GENERATION - self._POP[i][j][9] > self._CLEANING_TIME:
                        self._POP[i][j] = None

    def spread_the_disease(self):
        self.update_statuses()

        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self.statuses[i][j] and (
                    self.statuses[i][j] != CellStatus.incubation.value
                    or self.statuses[i][j] != CellStatus.infected.value
                    or self.statuses[i][j] != CellStatus.dead.value
                ):
                    if self.neighbours(np.array(self.statuses), i, j).any() == 4:
                        incubated_neighbours = (
                            self.neighbours(np.array(self.statuses), i, j)
                            .tolist()
                            .count(4)
                        )
                        sickness_neighbours_chance = (
                            self._L_INF_FROM_INCUBATED_CHANCE
                            + (
                                self._U_INF_FROM_INCUBATED_CHANCE
                                - self._L_INF_FROM_INCUBATED_CHANCE
                            )
                            * incubated_neighbours
                            / 8
                        )
                        sickness_chance = sickness_neighbours_chance * math.sin(
                            math.pi * self.calc_immunity(i, j) / 2
                        )
                        chance = random.random()
                        if sickness_chance > chance:
                            self.incubate_cell(i, j)

                    if self.neighbours(np.array(self.statuses), i, j).any() == 5:
                        incubated_neighbours = (
                            self.neighbours(np.array(self.statuses), i, j)
                            .tolist()
                            .count(5)
                        )
                        sickness_neighbours_chance = (
                            self._L_INF_FROM_SICK_CHANCE
                            + (
                                self._U_INF_FROM_SICK_CHANCE
                                - self._L_INF_FROM_SICK_CHANCE
                            )
                            * incubated_neighbours
                            / 8
                        ) / self._POP[i][j][0]
                        sickness_chance = sickness_neighbours_chance * math.cos(
                            math.pi * self.calc_immunity(i, j) / 2
                        )
                        chance = random.random()
                        if sickness_chance > chance:
                            self.incubate_cell(i, j)

    def movement_behaviour(self):
        self.update_statuses()
        self.update_behaviour()

        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self.statuses[i][j] and self.statuses[i][j] != CellStatus.dead.value:
                    if self._POP[i][j][2][0] == CellBehaviour.random.value:
                        self.choose_direction_randomly(i, j)
                    elif self._POP[i][j][2][0] == CellBehaviour.heading_home.value:
                        self.find_path_home(i, j)
                    elif self._POP[i][j][2][0] == CellBehaviour.heading_to_work.value:
                        self.find_path_to_job(i, j)

    def update_behaviour(self):
        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self.statuses[i][j]:
                    if self._POP[i][j][2][0] == CellBehaviour.random.value:
                        chance = random.random()
                        if chance < self._CHANGING_BEHAVIOUR_LIKENESS:
                            self._POP[i][j][2][0] = random.choice(
                                list(CellBehaviour)
                            ).value
                    if (
                        self._POP[i][j][2][0] == CellBehaviour.heading_home.value
                        or self._POP[i][j][2][0] == CellBehaviour.heading_to_work.value
                    ):
                        if len(self._POP[i][j][2][1]) <= 2:
                            self._POP[i][j][2][2] = True

                    if self._POP[i][j][2][2]:
                        a = []
                        for e in CellBehaviour:
                            a.append(e.value)
                        a.remove(self._POP[i][j][2][0])
                        self._POP[i][j][2][0] = random.choice(a)

                        self._POP[i][j][2][2] = False

    def choose_direction_randomly(self, i, j):
        movement = random.randint(0, 4)
        if movement == 0:
            pass
        elif movement == 1 and not self._POP[(i - 1) % self._SIZE][j]:
            self.move_to_cell((i, j), ((i - 1) % self._SIZE, j))
        elif movement == 2 and not self._POP[(i + 1) % self._SIZE][j]:
            self.move_to_cell((i, j), ((i + 1) % self._SIZE, j))
        elif movement == 3 and not self._POP[i][(j - 1) % self._SIZE]:
            self.move_to_cell((i, j), (i, (j - 1) % self._SIZE))
        elif movement == 4 and not self._POP[i][(j + 1) % self._SIZE]:
            self.move_to_cell((i, j), (i, (j + 1) % self._SIZE))
        else:
            self.choose_direction_randomly(i, j)

    def find_path_home(self, i, j):
        self.update_statuses()
        grid = Grid(matrix=self.pathfinging_matrix)
        start = grid.node(i, j)

        end_i = list(self._POP[i][j][10])[0]
        end_j = list(self._POP[i][j][10])[1]

        end = grid.node(end_i, end_j)

        finder = AStarFinder(
            diagonal_movement=DiagonalMovement.always, max_runs=self._SIZE**2
        )

        path, runs = finder.find_path(start, end, grid)
        self._POP[i][j][2][1] = path

        self.procede_acc_to_path(i, j)

    def find_path_to_job(self, i, j):
        self.update_statuses()
        grid = Grid(matrix=self.pathfinging_matrix)
        start = grid.node(i, j)

        end_i = list(self._POP[i][j][11])[0]
        end_j = list(self._POP[i][j][11])[1]

        end = grid.node(end_i, end_j)

        finder = AStarFinder(
            diagonal_movement=DiagonalMovement.always, max_runs=self._SIZE**2
        )

        path, runs = finder.find_path(start, end, grid)
        self._POP[i][j][2][1] = path
        self.procede_acc_to_path(i, j)

    def procede_acc_to_path(self, i, j):
        if (
            len(self._POP[i][j][2][1]) != 0
            and not self._POP[i][j][2][2]
            and len(self._POP[i][j][2][1]) > 1
        ):
            self.move_to_cell((i, j), self._POP[i][j][2][1][1])

    def move_to_cell(self, start, end):
        self.update_statuses()
        if self._POP[end[0]][end[1]] == None:
            self._POP[end[0]][end[1]] = self._POP[start[0]][start[1]]
            self._POP[start[0]][start[1]] = None

    def neighbours(self, x, i, j):
        return x[
            np.ix_(*((z - 1, z, z + 1 - S) for z, S in zip((i, j), x.shape)))
        ].ravel()

    def update_statuses(self):
        self.statuses = []

        for layer in self._POP:
            tmp_st = []

            for pop in layer:
                if pop:
                    tmp_st.append(pop[0])
                else:
                    tmp_st.append(CellStatus.empty.value)

            self.statuses.append(tmp_st)

        self.pathfinging_matrix = []
        for layer in self.statuses:
            tmp = []
            for cell in layer:
                tmp.append(0 if cell != None else 1)
            self.pathfinging_matrix.append(tmp)

    def clear(self):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    def print_population(self):
        self.clear()
        print(f"== GENERATION {self._GENERATION} ==\n")

        self.update_statuses()

        for layer in self.statuses:
            pretty_line = ""
            for pop in layer:
                if not pop:
                    pretty_line += "  |"
                else:
                    if pop == CellStatus.not_infected.value:
                        pretty_line += "🚶|"
                    if pop == CellStatus.vaccinated.value:
                        pretty_line += "💉|"
                    if pop == CellStatus.incubation.value:
                        pretty_line += "❓|"
                    if pop == CellStatus.infected.value:
                        pretty_line += "🆘|"
                    if pop == CellStatus.recovered.value:
                        pretty_line += "🍀|"
                    if pop == CellStatus.dead.value:
                        pretty_line += "💀|"
            print(pretty_line)
            print("-" * self._SIZE * 3)
