from IPython.display import clear_output
from plotly.subplots import make_subplots
import enum
import numpy as np
import os, platform
import plotly
import plotly.graph_objects as go
import random
import time
import math


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


class Field:
    def __init__(self, size, perc_of_filled, perc_of_infected) -> None:
        self._SIZE = size
        self._GENERATION = 1
        self._MAX_ITERATION = 500
        self._SLEEP_TIME = 0.1

        self._VACCINATION_BASE_ATTRACTIVENESS = 5e-3
        self._VACCINATION_ATTRACTIVENESS = 1e-4

        self._L_INIT_IMMUNITY = 0.2
        self._U_INIT_IMMUNITY = 0.8

        self._L_INF_FROM_INCUBATED_CHANCE = 0.2
        self._U_INF_FROM_INCUBATED_CHANCE = 0.4

        self._L_INF_FROM_SICK_CHANCE = 0.4
        self._U_INF_FROM_SICK_CHANCE = 0.8

        self._L_INC_DURATION = 3
        self._U_INC_DURATION = 9

        self._L_INF_DURATION = 0
        self._U_INF_DURATION = 14

        self._SICKNESS_PENALTY = 0.5
        self._CURE_IMMUNITY = 0.2
        self._VACC_IMMUNITY = 0.3

        self._CLEANING_TIME = 3

        self._DEATHS = 1

        self.init_pops(perc_of_filled, perc_of_infected)

    def init_pops(self, perc_of_filled, perc_of_infected):
        self._POP = [[None for y in range(self._SIZE)] for x in range(self._SIZE)]

        cells_amount = int(round(self._SIZE**2 * perc_of_filled / 100, 0))
        for cell in range(cells_amount):
            self.populate_cell()

        populated = []
        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self._POP[i][j] != None:
                    populated.append((i, j))

        infected_amount = int(round(cells_amount * perc_of_infected / 100, 0))
        infected = random.sample(populated, k=infected_amount)
        for cell in infected:
            self.incubate_cell(cell[0], cell[1])

    def start_covid(self):
        for self._GENERATION in range(1, self._MAX_ITERATION + 1):
            if self._SIZE > 15:
                self.plot_population()
            else:
                self.print_population()

            self.random_movement_behaviour()
            self.vaccinate()
            self.spread_the_disease()
            self.turn_inc_into_inf()
            self.cure_cells()
            self.kill_dying_cells()
            self.clean_field()
            time.sleep(self._SLEEP_TIME)

    def populate_cell(self):
        rand_layer = random.randint(0, self._SIZE - 1)
        rand_cell = random.randint(0, self._SIZE - 1)

        if not self._POP[rand_layer][rand_cell]:
            self._POP[rand_layer][rand_cell] = [
                CellStatus.not_infected.value,
                random.uniform(self._L_INIT_IMMUNITY, self._U_INIT_IMMUNITY),
                CellBehaviour.random.value,
                None,
                None,
                None,
                [],
                [],
                [],
                None,
            ]
        else:
            self.populate_cell()

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
        return self._POP[i][j][1] + sum(self._POP[i][j][7]) - sum(self._POP[i][j][6])

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

    def random_movement_behaviour(self):
        self.update_statuses()
        for i in range(self._SIZE):
            for j in range(self._SIZE):
                if self.statuses[i][j] and self.statuses[i][j] != CellStatus.dead.value:
                    self.choose_direction_randomly(i, j)

    def choose_direction_randomly(self, i, j):
        movement = random.randint(0, 4)
        if movement == 0:
            pass
        elif movement == 1 and not self._POP[(i - 1) % self._SIZE][j]:
            self.move_up(i, j)
        elif movement == 2 and not self._POP[(i + 1) % self._SIZE][j]:
            self.move_down(i, j)
        elif movement == 3 and not self._POP[i][(j - 1) % self._SIZE]:
            self.move_left(i, j)
        elif movement == 4 and not self._POP[i][(j + 1) % self._SIZE]:
            self.move_right(i, j)
        else:
            self.choose_direction_randomly(i, j)

    def move_up(self, i, j):
        self._POP[i][j], self._POP[(i - 1) % self._SIZE][j] = (
            self._POP[(i - 1) % self._SIZE][j],
            self._POP[i][j],
        )

    def move_down(self, i, j):
        self._POP[i][j], self._POP[(i + 1) % self._SIZE][j] = (
            self._POP[(i + 1) % self._SIZE][j],
            self._POP[i][j],
        )

    def move_left(self, i, j):
        self._POP[i][j], self._POP[i][(j - 1) % self._SIZE] = (
            self._POP[i][(j - 1) % self._SIZE],
            self._POP[i][j],
        )

    def move_right(self, i, j):
        self._POP[i][j], self._POP[i][(j + 1) % self._SIZE] = (
            self._POP[i][(j + 1) % self._SIZE],
            self._POP[i][j],
        )

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

    def print_population(self):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

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

    def plot_population(self):
        clear_output()
        statuses = []
        immunities = []

        for layer in self._POP:
            tmp_st = []
            tmp_im = []

            for pop in layer:
                if pop:
                    tmp_st.append(pop[0])
                    tmp_im.append(pop[1])
                else:
                    tmp_st.append(CellStatus.empty.value)
                    tmp_im.append(CellStatus.empty.value)

            statuses.append(tmp_st)
            immunities.append(tmp_im)

        if self._GENERATION == 1:
            self.fig = make_subplots(
                rows=1, cols=2, subplot_titles=("Cells", "Immunity")
            )
            self.fig.add_trace(
                go.Heatmap(
                    z=statuses,
                    type="heatmap",
                    colorscale=plotly.colors.sequential.Bluered,
                    showlegend=False,
                ),
                row=1,
                col=1,
            )
            self.fig.add_trace(
                go.Heatmap(
                    z=immunities,
                    type="heatmap",
                    colorscale=plotly.colors.sequential.Bluered,
                    showlegend=False,
                ),
                row=1,
                col=2,
            )

        self.fig.update_layout(
            title_text=f"GENERATION {self._GENERATION}", height=400, width=800
        )
        with self.fig.batch_update():
            self.fig.data[0].z = statuses
            self.fig.data[1].z = immunities

        self.fig.show("notebook")


f = Field(size=14, perc_of_filled=20, perc_of_infected=30)
f.start_covid()
