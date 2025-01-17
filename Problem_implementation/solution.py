import math
import copy
import random
import struktury_danych
from typing import List, Union, Set
from funkcje_sasiedztwa_SK import *
from funkcja_sasiedztwa_MK import *
from funkcja_sasiedztwa_PG import *


class Machine:
    def __init__(self, speed=30):
        self.speed = speed  # In Km/h
        self.route = []

    def generate_initial_route(self, road_layout, Tmax, number_of_stages, consider_priority=False):
        """
        Generate an initial route for the machine considering time constraints and optionally road priorities.

        Args:
            road_layout: Graph representing the road network
            Tmax: Maximum time allowed per stage
            number_of_stages: Number of snowfall stages to plan for
            consider_priority: Whether to consider road priorities in route selection
        """
        self.route = []

        current_location = road_layout.baza
        previous_location = None

        for stage_no in range(number_of_stages):
            time_cost = 0
            stage_route = []

            while True:
                neighbors = current_location.sasiedzi
                if not neighbors:
                    break

                # Filter out the previous location if we have other options
                valid_neighbors = [n for n in neighbors if n != previous_location or len(neighbors) == 1]

                if not valid_neighbors:
                    break

                if consider_priority:
                    # Create list of (priority, neighbor, edge) tuples
                    priority_options = []
                    for neighbor in valid_neighbors:
                        edge = road_layout.get_edge(current_location, neighbor)
                        # Add small random factor to break ties
                        adjusted_priority = edge.priorytet + random.random() * 0.1
                        priority_options.append((adjusted_priority, neighbor, edge))

                    # Sort by priority in descending order and select the highest priority option
                    priority_options.sort(reverse=True)
                    next_location = priority_options[0][1]
                    selected_edge = priority_options[0][2]
                else:
                    next_location = random.choice(valid_neighbors)
                    selected_edge = road_layout.get_edge(current_location, next_location)

                # Calculate new time cost
                new_time_cost = time_cost + selected_edge.oblicz_dlugosc() / self.speed

                # Check if adding this edge would exceed time limit
                if new_time_cost >= Tmax:
                    break

                # Add edge to route and update positions
                stage_route.append(selected_edge)
                time_cost = new_time_cost
                previous_location = current_location
                current_location = next_location

                # Safety check - if we're stuck at the base with no valid moves, break
                if current_location == road_layout.baza and len(stage_route) > 0:
                    break

            self.route.append(stage_route)


class RoadClearingProblem:
    def __init__(self,
                 snowfall_forecast: List[int],
                 road_layout: struktury_danych.Graf,
                 machines: List[Machine],
                 Tmax: Union[int, float]):

        self.snowfall_forecast = snowfall_forecast
        self.road_layout = road_layout
        self.machines = machines
        self.danger = float("inf")
        self.Tmax = Tmax  # In hours

        self.get_initial_path()

        rozw = [machine.route for machine in self.machines]

        for route in rozw:
            print(route, '\n')

    def get_initial_path(self):
        for machine in self.machines:
            machine.generate_initial_route(self.road_layout, self.Tmax, len(self.snowfall_forecast))

    # -----------------------------------------------------------------------------------------------------------#
    # -------------------------------------------WERSJA V2-------------------------------------------------------#
    # -----------------------------------------------------------------------------------------------------------#
    def simulated_annealing_2(self, initial_temperature, cooling_rate, max_iterations, choose_neighbour_function=[4]):
        # Oblicz początkowe zagrożenie na podstawie obecnego - poczatkowego rozwiązania
        current_danger = self.simulate_danger_2()
        best_danger = current_danger

        temperature = initial_temperature
        actual_solution = copy.deepcopy(self.machines)  # aktualne rozwiazanie
        best_solution = copy.deepcopy(self.machines)

        for iteration in range(max_iterations):
            print("\n")
            print("-----ITERACJA ", iteration, "-------")

            # Generowanie sąsiedniego rozwiązania
            self.generate_neighbor_2(temperature, choose_neighbour_function)

            # Symulacja nowego rozwiązania i obliczenie zagrożenia
            new_danger = self.simulate_danger_2()

            print("NEW DANGER -> ", new_danger)

            # Oblicz różnicę zagrożenia
            delta_danger = new_danger - current_danger
            print("Roznica zagrozenia: ", delta_danger)

            # Akceptacja rozwiązania na podstawie funkcji Boltzmanna
            if delta_danger < 0 or random.random() < math.exp(-delta_danger / temperature):
                actual_solution = copy.deepcopy(self.machines)
                current_danger = new_danger

                # Aktualizacja najlepszego rozwiązania
                if new_danger < best_danger:
                    best_solution = copy.deepcopy(actual_solution)
                    best_danger = new_danger

            else:
                # w innym wypadku wracamy do rozwiazania aktualnego
                self.machines = actual_solution

                # Schładzanie temperatury
            temperature *= cooling_rate

            # Warunek zakończenia
            if temperature < 1e-3:
                print("Zakończenie przez za niską temperature!")
                break

        self.machines = best_solution
        return best_solution, best_danger

    def simulate_danger_2(self):
        """
        Symuluje zagrożenie dla podanego rozwiązania, przechodząc przez wszystkie etapy opadów śniegu.
        Najpierw przypisuje odpowiedni poziom sniegu ulicom w danym etapie i nastepnie wyznaczna odpowiedni poziom
        niebezpieczenstwa i zwraca jego sume dla wszystkich etapów.
        Cała symulacja działa na kopii rozkladu ulic, przez co nie narusza jego orygnalnej postaci.
        :return: Całkowity poziom zagrożenia.
        """
        graf_start = copy.deepcopy(self.road_layout)  # Dzialanie na kopii w celu zachowania oryginalnej postaci
        total_danger = 0

        for etap in range(len(self.snowfall_forecast)):
            # Lista odsnieżonych krawędzi przez wszystkie maszyny w danym etapie
            ulice_clear = []
            for m in self.machines:
                for street in m.route[etap]:
                    if street not in ulice_clear:
                        ulice_clear.append(street)

            for street in graf_start.krawedzie:
                if street in ulice_clear:  # Sprawdzamy, czy krawędź została odsnieżona
                    street.snow_level = 0  # Ulica została odsnieżona
                else:
                    street.snow_level += self.snowfall_forecast[
                        etap]  # Dodajemy śnieg na ulicach, które nie zostały odsnieżone

            # obliczenie niebezpieczenstwa w danym etapie
            stage_level = sum(street.get_danger_level() for street in graf_start.krawedzie)
            total_danger += stage_level

        return total_danger

    def generate_neighbor_2(self, actual_temperature, choose_neighbour_function):
        """
        Generuje nowe rozwiazanie poprzez uzycie konkretnych funkcji sasiedztwa
        """
        graf_komp = len(self.road_layout.krawedzie) # ilość krawedzi/dróg w grafie - opis skomplikowania
 
        # Parametry dla funkcja_sasiedztwa_MK - dostosowanie do skomplikowania grafu
        glebokosc_poszukiwan = 6
        param2 = 4

        if graf_komp > 200:
            glebokosc_poszukiwan = 12
            param2 = 8

        actual_temp = actual_temperature # Wartosc temperatury w danej iteracji

        # Wybrane funkcje sasiedztwa do zrealizowania algorytmu (parametr - choose_neighbour_function - domyslnie choose_neighbour_function=[4] - uzycie wszystkich funkcji)
        f_using = choose_neighbour_function

        # Zaznaczenie jednej z opcji (konkretna f_sasiedztwa lub wszystkie)
        if len(f_using) == 1:
            
            # Opcja - wszystkie f_sasiedztwa - NAJLEPSZA OPCJA - najbardziej rozbudowana
            if f_using[0] == 4:
                # --- Etap I ---
                '''
                W początkowych iteracjach nasze rozwiązanie może radykalniej się zmieniać
                '''
                if actual_temp > 1:
                    param_choose = random.randint(0, 100) # losujemy wartosc parametru

                    if param_choose < 65:
                        # Wprowadzamy bardziej radykalne zmiany
                        glebokosc_poszukiwan =  int(glebokosc_poszukiwan*1.5)# zwieksza ewentualna roznorodnosc trasy w f_sasiad_0
                        choose_f = random.choice([0, 2, 3])

                    else:
                        glebokosc_poszukiwan =  glebokosc_poszukiwan*0.5# mniejsza roznorodnosc trasy w f_sasiad_0
                        param2 = int(param2*1.5)
                        choose_f = random.choice([0, 1])


                # --- Etap II ---
                '''
                W kolejnym etapie będziemy losowo wybierać funkcję sąsiedztwa
                '''
                if 0.01 < actual_temp <= 1:
                    glebokosc_poszukiwan = random.randint(int(glebokosc_poszukiwan*0.5), int(glebokosc_poszukiwan*2))
                    param2 = random.randint(int(param2*0.5), int(param2*2))
                    choose_f = random.choice([0, 1, 2, 3])

                # --- Etap III ---
                '''
                W ostatnim etapie będziemy starać się 'doszlifować/ulepszyć' nasze rozwiązanie, używając mniej radykalnych zmian
                '''
                if actual_temp <= 0.01:
                    param_choose = random.randint(0, 100) # losujemy wartosc parametru

                    if param_choose < 65:
                        # Wprowadzamy mniej radykalne zmiany
                        glebokosc_poszukiwan = int(glebokosc_poszukiwan*0.5)# mniejsza roznorodnosc trasy w f_sasiad_0
                        param2 = int(param2*1.5)
                        choose_f = random.choice([0, 1])

                    else:
                        glebokosc_poszukiwan = int(glebokosc_poszukiwan*1.5)# zwieksza ewentualna roznorodnosc trasy w f_sasiad_0
                        choose_f = random.choice([0, 2, 3])

            elif f_using[0] in [0, 1, 2, 3]:
                choose_f = f_using[0]

            else:
                print(
                    '''Brak podanej funkcji sasiedztwa!
                    Dostepne:
                    0, 1, 2, 3 -> konkretne funkcje sasiedztwa
                    4 -> uzycie wszystkich funkcji sasiedztwa jednoczesnie

                    Format wprowadzenia danych: 
                    Dla jednego wyboru -> np. [2]
                    Dla kilku wyborow -> np. [0, 2]
                    '''
                )

        else:
            f_codes = [0, 1, 2, 3]
            if all(elem in f_codes for elem in f_using):
                choose_f = random.choice(f_using)

            else:
                print(
                    '''Brak podanej funkcji sasiedztwa!
                    Dostepne:
                    0, 1, 2, 3 -> konkretne funkcje sasiedztwa
                    4 -> uzycie wszystkich funkcji sasiedztwa jednoczesnie

                    Format wprowadzenia danych: 
                    Dla jednego wyboru -> np. [2]
                    Dla kilku wyborow -> np. [0, 2]
                    '''
                )
        print(choose_f)
        # --- Używane funkcje_sąsiedztwa ---

        if choose_f == 0:
            f_sasiad_1(self.machines, glebokosc_poszukiwan, self.road_layout, self.Tmax)
            '''
            Modyfikuje istniejącą trasę maszyny omijając jeden wierzchołek, zalezna od paramtru 'glebokosc_poszukiwan' 
            (im większy parametr tym bardziej nowe/zróżnicowane rozwiązanie otrzymamy)
            '''

        elif choose_f == 1:
            f_sasiad_2(self.machines, self.road_layout, self.Tmax, param2)
            '''
            Rekonstruuje trase od losowo wybranego etapu, możliwość otrzymania duzych zmian przy wylosowaniu wczesnych etapów
            '''

        elif choose_f == 2:
            generate_route_from_least_frequent(self.machines, self.road_layout, self.Tmax)
            '''
            Generuje trasę z bazy do najmniej uczęszczanej ulicy i/ewentualnie dokłada ulice na koniec trasy, aby wypełnić czas.
            Możliwość wprowadzenia większych zmian.
            '''

        elif choose_f == 3:
            change_path(self.machines, self.road_layout, self.Tmax)
            '''
            Modyfikuje trasę maszyny, usuwając jedną krawędź i zastępując ją nową trasą naprawioną algorytmem A*.
            Przenosi krawędzie do następnego etapu, jeśli Tmax zostanie przekroczone.
            '''


