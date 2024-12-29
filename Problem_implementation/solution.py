import math
import copy
import struktury_danych
from typing import List, Union, Set
from funkcje_sasiedztwa_SK import *

class Machine:
    def __init__(self, speed=1):
        self.speed = speed
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

        for stage_no in range(number_of_stages):
            current_location = road_layout.baza
            previous_location = None
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
        self.solution = road_layout
        self.machines = machines
        self.danger = float("inf")
        self.Tmax = Tmax

        self.get_initial_path()

    def simulated_annealing(self, initial_temperature: float, cooling_rate: float, max_iterations: int):

        current_solution = copy.deepcopy(self.machines)  # Kopia aktualnych maszyn i ich tras
        best_solution = copy.deepcopy(current_solution)

        # Oblicz początkowe zagrożenie na podstawie obecnego rozwiązania
        current_danger = self.simulate_danger(current_solution)
        best_danger = current_danger
        temperature = initial_temperature

        for iteration in range(max_iterations):
            # # Generowanie sąsiedniego rozwiązania
            new_solution = None

            while new_solution is None:
                new_solution = self.generate_neighbor(current_solution)

            # Symulacja nowego rozwiązania i obliczenie zagrożenia
            new_danger = self.simulate_danger(new_solution)

            # Oblicz różnicę zagrożenia
            delta_danger = new_danger - current_danger
            print(delta_danger)

            # Akceptacja rozwiązania na podstawie funkcji Boltzmanna
            if delta_danger < 0 or random.random() < math.exp(-delta_danger / temperature):
                current_solution = new_solution
                current_danger = new_danger

                # Aktualizacja najlepszego rozwiązania
                if new_danger < best_danger:
                    best_solution = copy.deepcopy(new_solution)
                    best_danger = new_danger

            # Schładzanie temperatury
            temperature *= cooling_rate

            # Warunek zakończenia
            if temperature < 1e-3:
                break

        return best_solution, best_danger

    def generate_neighbor(self, current_solution):
        x = random.randint(0, 100)
        new_solution = current_solution.copy()
        machine_to_modify = random.choice(new_solution)

        if x < 60:
            self.change_path(machine_to_modify)  # Modyfikacja trasy jednej maszyny

        elif x < 75:
            machine_to_modify.generate_initial_route(self.road_layout,
                                                     self.Tmax,
                                                     len(self.snowfall_forecast),
                                                     consider_priority=False)

        elif x < 85:
            machine_to_modify.generate_initial_route(self.road_layout,
                                                     self.Tmax,
                                                     len(self.snowfall_forecast),
                                                     consider_priority=False)

        else:
            new_path, stage_index = generate_route_from_least_frequent(self.road_layout,
                                                                       machine_to_modify,
                                                                       self.machines,
                                                                       self.Tmax)
            if new_path is not None:
                if len(new_path) > 2:
                    machine_to_modify.route[stage_index] = new_path

        # Inna definicja sąsiedztwa -> stwórz trasę od nowa?
        # -> Usuń trasę od wierzchołka i generuj trasę od tego punktu od nowa?
        # -> Znajdź ulice występującą najrzadziej (można uwzględnić priorytet) w trasach innych maszyn,
        # zacznij od niego i twórz trasę do bazy, odwróć trasę i ewentualnie wygeneruj coś na koniec, aby wypełnić czas
        # -> Generowanie trasy w oparciu o priorytet
        # -> Dynamiczna definicja sąsiedztwa zależna od numeru iteracji
        # -> Zmiana prawdopodobieństwa wykonania operatora sąsiedztwa z czasem
        # -> Użycie wszystkich operatorów i wybranie najlepszego
        return new_solution

    def get_initial_path(self):
        for machine in self.machines:
            machine.generate_initial_route(self.road_layout, self.Tmax, len(self.snowfall_forecast))

    def change_path(self, machine: Machine):
        """
        Modyfikuje trasę maszyny, usuwając jedną krawędź i zastępując ją nową trasą naprawioną algorytmem A*.
        Przenosi krawędzie do następnego etapu, jeśli Tmax zostanie przekroczone.
        """

        machine_copy = copy.deepcopy(machine)
        new_route = machine_copy.route

        segment_idx = random.choice(range(len(new_route)))
        edge_for_deletion_idx = random.choice(range(len(new_route[segment_idx])))
        edge_for_deletion = new_route[segment_idx][edge_for_deletion_idx]

        self.road_layout.krawedzie.remove(edge_for_deletion)
        edge_for_deletion.start.sasiedzi.remove(edge_for_deletion.koniec)
        edge_for_deletion.koniec.sasiedzi.remove(edge_for_deletion.start)

        repaired_path = self.repair_path_A_star(edge_for_deletion, self.road_layout)

        if repaired_path is not None:
            # Replace the deleted edge with the repaired path
            new_route[segment_idx][edge_for_deletion_idx:edge_for_deletion_idx + 1] = repaired_path

            # Check and adjust route to respect Tmax
            while True:
                time = 0
                edges_to_move = []

                # Calculate total time for the current segment
                for edge in new_route[segment_idx]:
                    time += edge.dlugosc / machine.speed

                    # If time exceeds Tmax, prepare to move edges to the next segment
                    if time > self.Tmax:
                        # Start removing edges from the end of the segment
                        edges_to_move.append(edge)

                # If no edges need to be moved, break the loop
                if not edges_to_move:
                    break

                # Move excess edges to the next segment
                if segment_idx < len(new_route) - 1:
                    for edge in reversed(edges_to_move):
                        new_route[segment_idx].remove(edge)
                        new_route[segment_idx + 1].insert(0, edge)
                else:
                    # If it's the last segment, just remove the excess edges
                    for edge in edges_to_move:
                        new_route[segment_idx].remove(edge)

        # Restore the original edge and neighborhood relationships
        self.road_layout.krawedzie.append(edge_for_deletion)
        edge_for_deletion.start.dodaj_sasiada(edge_for_deletion.koniec)
        edge_for_deletion.koniec.dodaj_sasiada(edge_for_deletion.start)

        return

    @staticmethod
    def repair_path_A_star(removed_edge, graph):

        open_set = []
        heapq.heappush(open_set, (0, removed_edge.start))
        came_from = {}  # Przechowuje ścieżkę
        g_score = {node: float('inf') for node in graph.wierzcholki}
        g_score[removed_edge.start] = 0

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == removed_edge.koniec:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(removed_edge.start)

                path = path[::-1]
                path_as_edges = []

                for i in range(len(path) - 1):
                    path_as_edges.append(graph.get_edge(path[i], path[i + 1]))

                return path_as_edges

            for neighbor in current.sasiedzi:

                removed_edge_cost = 0

                if current == removed_edge.koniec and neighbor == removed_edge.start or \
                        current == removed_edge.start and neighbor == removed_edge.koniec:
                    removed_edge_cost = float('inf')

                tentative_g_score = g_score[current] + current.get_distance(neighbor) + removed_edge_cost
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + removed_edge.koniec.get_distance(neighbor) \
                              * graph.get_edge(current, neighbor).priorytet

                    heapq.heappush(open_set, (f_score, neighbor))

        return None  # Jeśli ścieżka nie istnieje

    def clear_streets(self, stage):
        """
        Odśnieża ulice zgodnie z trasami maszyn w danym etapie.
        """
        for machine in self.machines:
            if stage < len(machine.route):  # Sprawdzamy, czy maszyna ma trasę na danym etapie
                stage_route = machine.route[stage]
                for street in stage_route:
                    street.snow_level = 0

    def simulate_danger(self, machines: List[Machine]) -> float:
        """
        Symuluje zagrożenie dla podanego rozwiązania, przechodząc przez wszystkie etapy opadów śniegu.
        :param machines: Lista maszyn z trasami do symulacji.
        :return: Całkowity poziom zagrożenia.
        """
        # Skopiuj bieżący układ dróg, aby nie modyfikować stanu
        simulated_solution = copy.deepcopy(self.solution)
        total_danger = 0

        for stage in range(len(self.snowfall_forecast)):
            # Aktualizacja poziomu śniegu
            for street in simulated_solution.krawedzie:
                street.snow_level += self.snowfall_forecast[stage]

            # Odśnieżanie zgodnie z trasami maszyn
            for machine in machines:
                if stage < len(machine.route):  # Sprawdź, czy maszyna ma trasę dla bieżącego etapu
                    try:
                        for street in machine.route[stage]:
                            street.snow_level = 0  # Usunięcie śniegu

                    except TypeError:
                        print(machine.route)

            # Obliczenie zagrożenia po etapie
            stage_danger = sum(street.get_danger_level() for street in simulated_solution.krawedzie)
            total_danger += stage_danger

        return total_danger

