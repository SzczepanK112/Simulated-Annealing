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
        return temp_danger

    def get_initial_path(self):
        for machine in self.machines:
            machine.generate_initial_route(self.road_layout, self.Tmax, len(self.snowfall_forecast))

    def find_new_path(self):
        """
        Generuje nowe trasy dla każdej maszyny w sposób zgodny z ograniczeniami.
        """
        for machine in self.machines:
            new_route = []  # Nowa trasa dla danej maszyny
            for stage_no in range(len(self.snowfall_forecast)):
                current_location = self.road_layout.baza
                time_cost = 0
                stage_route = []

                while True:
                    # Wybór sąsiadów dostępnych na trasie
                    neighbors = current_location.sasiedzi
                    valid_neighbors = [
                        n for n in neighbors 
                        if self.road_layout.get_edge(current_location, n).snow_level <= 10  # Przejezdność
                    ]

                    if not valid_neighbors:
                        break  # Brak dostępnych sąsiadów

                    # Wybór kolejnego wierzchołka
                    next_location = random.choice(valid_neighbors)
                    street = self.road_layout.get_edge(current_location, next_location)

                    time_cost += street.dlugosc / machine.speed
                    if time_cost >= self.Tmax:  # Sprawdzenie ograniczenia czasu
                        break

                    stage_route.append(street)
                    current_location = next_location

                new_route.append(stage_route)
            machine.route = new_route

    def sprawdz_dopuszczalnosc(self, trasa, Tmax, speed) -> bool:
        """
        Sprawdza, czy trasa spełnia wszystkie ograniczenia (czas, przejezdność, priorytety).

        Args:
        - trasa: lista obiektów Krawedz
        - Tmax: maksymalny czas trasy
        - speed: prędkość maszyny

        Returns:
        - True, jeśli trasa jest dopuszczalna, False w przeciwnym razie.
        """
        czas_trasy = sum(street.dlugosc / speed for street in trasa)
        przejezdnosc = all(street.snow_level <= 10 for street in trasa)
        priorytety = all(street.priorytet >= 50 for street in trasa)  # Przykładowe ograniczenie
        return czas_trasy <= Tmax and przejezdnosc and priorytety

    def clear_streets(self, stage):
        """
        Odśnieża ulice zgodnie z trasami maszyn w danym etapie.
        """
        for machine in self.machines:
            if stage < len(machine.route):  # Sprawdzamy, czy maszyna ma trasę na danym etapie
                stage_route = machine.route[stage]
                for street in stage_route:
                    street.snow_level = 0

    def mainloop(self):
        danger_per_stage = []

        for stage in range(len(self.snowfall_forecast)):
            # Aktualizacja poziomu śniegu na ulicach
            for street in self.solution.krawedzie:
                street.snow_level += self.snowfall_forecast[stage]

            # Sprawdzenie poprawności tras i regeneracja tras w razie potrzeby
            for machine in self.machines:
                for stage_route in machine.route:
                    if not self.sprawdz_dopuszczalnosc(stage_route, self.Tmax, machine.speed):
                        self.find_new_path()  # Znalezienie nowej trasy, jeśli obecna jest niedopuszczalna
                        break

            # Odśnieżanie ulic
            self.clear_streets(stage)

            # Obliczanie poziomu zagrożenia po odśnieżaniu
            stage_danger = self.calculate_danger()
            danger_per_stage.append(stage_danger)

        return danger_per_stage

