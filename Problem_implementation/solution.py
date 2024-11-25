import random
import struktury_danych
import wczytanie_mapy
from typing import List, Union


class Machine:
    def __init__(self, speed=1):
        self.speed = speed
        self.route = []

    def generate_initial_route(self, road_layout, Tmax, number_of_stages):
        current_location = road_layout.baza

        for stage_no in range(number_of_stages):
            time_cost = 0
            stage_route = []

            # For each stage of snowfall calculate random route that is allowed by the time constraints
            while True:
                neighbors = current_location.sasiedzi
                next_location = random.choice(neighbors)  # Choose random neighbor as next location
                street = road_layout.get_edge(current_location, next_location)

                time_cost += street.oblicz_dlugosc() / self.speed

                if time_cost >= Tmax:
                    break

                stage_route.append(street)
                current_location = next_location

            self.route.append(stage_route)


class RoadClearingProblem:
    def __init__(self,
                 snowfall_forecast: List[int],
                 road_layout: struktury_danych.Graf,
                 machines: List[Machine],
                 Tmax: Union[int, float]):

        """
        snowfall_forecast - vector containing level of snow that will cover the streets after each time period
        road_layout - graph with road representation for a given city
        machines - list of machines designated for snow removal
        Tmax - max time that machine can spend clearing the streets before next snowfall | time between snowfalls
        danger - goal function to be minimized (our temperature as in simulated annealing)
        """

        self.snowfall_forecast = snowfall_forecast
        self.road_layout = road_layout
        self.solution = road_layout
        self.machines = machines
        self.danger = float("inf")
        self.Tmax = Tmax

    def calculate_danger(self):
        temp_danger = 0
        for street in self.solution.krawedzie:
            temp_danger += street.get_danger_level()

        self.danger = temp_danger

    def get_initial_path(self):
        for machine in self.machines:
            machine.generate_initial_route(self.road_layout, self.Tmax, len(self.snowfall_forecast))

    def find_new_path(self):
        pass

    def clear_streets(self, stage):
        for machine in self.machines:
            stage_route = machine.route[stage]

            for street in stage_route:
                street.snow_level = 0

    def mainloop(self):
        danger_per_stage = []
        for stage in range(len(self.snowfall_forecast)):
            for street in self.solution.krawedzie:
                street.snow_level += self.snowfall_forecast[stage]

            self.clear_streets(stage)
