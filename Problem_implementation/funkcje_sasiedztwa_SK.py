import heapq
import random


def find_path_to_base(road_layout, start_node, excluded_edge=None):
    """
    Find path to base using A* algorithm, optionally excluding one edge.
    """
    open_set = [(0, start_node, [])]
    closed_set = set()

    while open_set:
        f_score, current, path = heapq.heappop(open_set)

        if current == road_layout.baza:
            return path

        if current in closed_set:
            continue

        closed_set.add(current)

        for neighbor in current.sasiedzi:
            if neighbor in closed_set:
                continue

            edge = road_layout.get_edge(current, neighbor)
            if edge == excluded_edge:
                continue

            new_path = path + [edge]
            # Use edge length and priority in heuristic
            g_score = sum(e.oblicz_dlugosc() for e in new_path)
            h_score = neighbor.get_distance(road_layout.baza)
            f_score = g_score + h_score

            heapq.heappush(open_set, (f_score, neighbor, new_path))

    return None


def fill_remaining_time(road_layout, start_node, remaining_time, machine_speed):
    """
    Fill remaining time with additional edges using a greedy approach.
    """
    additional_route = []
    current_node = start_node
    time_used = 0

    while True:
        # Get valid neighbors (excluding those that would create a dead end)
        valid_neighbors = [n for n in current_node.sasiedzi
                           if len(n.sasiedzi) > 1 or n == road_layout.baza]

        if not valid_neighbors:
            break

        # Choose next edge (randomly or by priority)
        next_node = random.choice(valid_neighbors)
        edge = road_layout.get_edge(current_node, next_node)

        # Check if adding this edge would exceed remaining time
        time_cost = edge.oblicz_dlugosc() / machine_speed
        if time_used + time_cost > remaining_time:
            break

        additional_route.append(edge)
        time_used += time_cost
        current_node = next_node

        # Stop if we've returned to base
        if current_node == road_layout.baza:
            break

    return additional_route


def generate_route_from_least_frequent(road_layout, current_machine, all_machines, Tmax, consider_priority=True):
    """
    Generuje trasę, zaczynając od najmniej uczęszczanej ulicy, następnie tworzy ścieżkę do bazy, odwraca ją i
    ewentualnie dokłada ulice na koniec trasy, aby wypełnić czas. Consider_priority jeszcze nie działa :(
    """

    stage_index = random.randint(1, len(current_machine.route)) - 1

    def calculate_street_frequency(edge):
        frequency = 0
        for machine in all_machines:
            if machine != current_machine:  # Don't count current machine
                if stage_index < len(machine.route):
                    frequency += sum(1 for route_edge in machine.route[stage_index]
                                     if route_edge == edge)

        # If considering priority, adjust frequency score by priority
        if consider_priority:
            # Normalize frequency to 0-1 range and combine with priority
            # Lower frequency and higher priority will give lower score
            freq_score = frequency / (len(all_machines) - 1) if len(all_machines) > 1 else 1
            priority_score = 1 - (edge.priorytet / max(e.priorytet for e in road_layout.krawedzie))
            return (freq_score + priority_score) / 2
        return frequency

    # Calculate frequencies for all edges
    edge_scores = [(calculate_street_frequency(edge), edge) for edge in road_layout.krawedzie]
    edge_scores.sort(key=lambda x: x[0])  # Sort by frequency/score

    # Try edges starting from least frequent until we find one that works
    for _, start_edge in edge_scores:
        # Try both directions of the edge
        for start_node, end_node in [(start_edge.start, start_edge.koniec),
                                     (start_edge.koniec, start_edge.start)]:
            # Find path to base using A*
            path_to_base = find_path_to_base(road_layout, start_node, start_edge)

            if path_to_base:
                # Calculate time cost of path including initial edge
                time_cost = (start_edge.oblicz_dlugosc() +
                             sum(edge.oblicz_dlugosc() for edge in path_to_base)) / current_machine.speed

                if time_cost <= Tmax:
                    # Create initial route with start_edge and path to base
                    route = [start_edge] + path_to_base

                    # Reverse the route
                    route = route[::-1]

                    # Try to fill remaining time
                    remaining_time = Tmax - time_cost
                    if remaining_time > 0:
                        additional_edges = fill_remaining_time(
                            road_layout,
                            route[-1].koniec,  # Start from last position
                            remaining_time,
                            current_machine.speed
                        )
                        route.extend(additional_edges)

                    return route, stage_index

    # If no valid route found, return empty route
    return []

