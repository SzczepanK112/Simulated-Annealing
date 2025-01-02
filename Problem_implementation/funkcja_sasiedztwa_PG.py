import random

def neighbor_based_on_priority(current_solution, road_layout, Tmax, priority_threshold):
    """
    Zamienia fragment trasy maszyny na trasę utworzoną z ulic o wyższym priorytecie.
    
    Args:
        current_solution: Lista obecnych tras maszyn.
        road_layout: Graf reprezentujący sieć ulic.
        Tmax: Maksymalny czas dla jednego etapu.
        priority_threshold: Minimalny priorytet ulic w nowej trasie.
    
    Returns:
        Nowe rozwiązanie tras.
    """
    # Wybierz losowo maszynę do modyfikacji
    machine_id = random.randint(0, len(current_solution) - 1)
    machine = current_solution[machine_id]
    etap_id = random.randint(0, len(machine.route) - 1)

    # Utwórz nową trasę
    new_route = []
    time_used = 0
    current_node = road_layout.baza  # Startujemy z bazy

    while time_used < Tmax:
        # Pobierz sąsiadów z priorytetem powyżej progu
        valid_edges = [edge for edge in road_layout.get_edges_from_vertex(current_node)
                       if edge.priorytet >= priority_threshold]

        if not valid_edges:
            break

        # Wybierz krawędź o najwyższym priorytecie
        next_edge = max(valid_edges, key=lambda edge: edge.priorytet)
        new_route.append(next_edge)
        time_used += next_edge.dlugosc / machine.speed
        current_node = next_edge.koniec

        # Zakończ, jeśli wrócimy do bazy
        if current_node == road_layout.baza:
            break

    if new_route:
        machine.route[etap_id] = new_route

    return current_solution


def neighbor_from_least_used_edge(current_solution, road_layout, Tmax):
    """
    Tworzy nową trasę dla jednej maszyny, zaczynając od najmniej używanej ulicy.
    
    Args:
        current_solution: Lista obecnych tras maszyn.
        road_layout: Graf reprezentujący sieć ulic.
        Tmax: Maksymalny czas dla jednego etapu.
    
    Returns:
        Nowe rozwiązanie tras.
    """
    # Zlicz użycia każdej krawędzi
    edge_usage = {edge: 0 for edge in road_layout.krawedzie}

    for machine in current_solution:
        for stage in machine.route:
            for edge in stage:
                edge_usage[edge] += 1

    # Znajdź najmniej używaną krawędź
    least_used_edge = min(edge_usage, key=edge_usage.get)

    # Rozpocznij trasę od najmniej używanej krawędzi
    new_route = []
    time_used = least_used_edge.dlugosc / current_solution[0].speed
    new_route.append(least_used_edge)
    current_node = least_used_edge.koniec

    while time_used < Tmax:
        # Znajdź sąsiadów aktualnego wierzchołka
        neighbors = road_layout.get_edges_from_vertex(current_node)
        if not neighbors:
            break

        # Wybierz losowego sąsiada
        next_edge = random.choice(neighbors)
        time_used += next_edge.dlugosc / current_solution[0].speed
        new_route.append(next_edge)
        current_node = next_edge.koniec

        # Przerwij, jeśli wrócimy do bazy
        if current_node == road_layout.baza:
            break

    # Zaktualizuj trasę jednej maszyny
    machine_to_update = random.choice(current_solution)
    machine_to_update.route[random.randint(0, len(machine_to_update.route) - 1)] = new_route

    return current_solution
