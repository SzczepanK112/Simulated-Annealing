import random

def neighbor_based_on_priority(current_solution, road_layout, Tmax, priority_threshold, param2=2):
    """
    Zamienia część trasy maszyny na trasę utworzoną (przede wszystkim) z ulic 
    o priorytecie >= priority_threshold. 
    Jeśli żadna krawędź nie spełnia warunku priorytetu, możemy wybrać losową krawędź,
    by kontynuować trasę.

    Dodatkowo:
    - Gdy dojedziemy do bazy z zapasem czasu, próbujemy go dopełnić dodatkowymi krawędziami.
    - Przechowujemy niewielką listę ostatnio wybranych krawędzi (param2), by nie powtarzać
      dokładnie tych samych krawędzi natychmiast w kółko.
    - Nie modyfikujemy całej trasy, lecz TYLKO JEDEN etap (wylosowany).

    Args:
        current_solution (list): Lista obiektów typu Machine.
        road_layout: Graf (z bazą, krawędziami i metodą get_edges_from_vertex).
        Tmax (float): Maksymalny czas, jaki można przeznaczyć na jeden etap.
        priority_threshold (float): Minimalny priorytet preferowanych krawędzi.
        param2 (int): Ilość ostatnio wybranych krawędzi, których nie powtarzamy.

    Returns:
        list: Zaktualizowana lista maszyn (current_solution).
    """

    if not current_solution:
        print("[Priority] Brak maszyn w current_solution.")
        return current_solution

    # 1. Losowo wybieramy maszynę do modyfikacji
    machine_id = random.randint(0, len(current_solution) - 1)
    machine = current_solution[machine_id]

    # Jeżeli ta maszyna nie ma żadnych etapów, to nic nie zrobimy
    if not machine.route:
        print(f"[Priority] Maszyna {machine_id} nie ma żadnych etapów do modyfikacji.")
        return current_solution

    # 2. Losowo wybieramy etap, który chcemy modyfikować
    etap_id = random.randint(0, len(machine.route) - 1)

    # 3. Przygotowanie do budowy nowej trasy w tym etapie
    time_used = 0.0
    new_route = []
    current_node = road_layout.baza  # Zaczynamy od bazy
    # By ograniczyć zapętlenia, pamiętamy kilka ostatnich krawędzi (lub węzłów):
    recent_edges = []

    while time_used < Tmax:
        all_edges = road_layout.get_edges_from_vertex(current_node)
        if not all_edges:
            # Nie da się jechać dalej
            break

        # Filtrujemy krawędzie wg priorytetu
        valid_edges = [edge for edge in all_edges if edge.priorytet >= priority_threshold
                       and edge not in recent_edges]

        # Jeśli nic nie spełnia priorytetu, rozważamy wszystkie (z wyłączeniem niedawnych powtórzeń)
        if not valid_edges:
            fallback_edges = [e for e in all_edges if e not in recent_edges]
            if fallback_edges:
                next_edge = random.choice(fallback_edges)
            else:
                # Jeśli nawet fallback jest pusty (może param2 = 2 wykluczyło wszystko?)
                next_edge = random.choice(all_edges)
        else:
            # Wybieramy krawędź o najwyższym priorytecie spośród valid_edges
            next_edge = max(valid_edges, key=lambda e: e.priorytet)

        cost = next_edge.dlugosc / machine.speed
        przewidywany_czas = time_used + cost

        if przewidywany_czas > Tmax:
            # Przekraczamy limit etapu
            break

        # Dodajemy krawędź do nowej trasy
        new_route.append(next_edge)
        time_used = przewidywany_czas
        current_node = next_edge.koniec

        # Aktualizujemy listę ostatnich krawędzi
        recent_edges.append(next_edge)
        if len(recent_edges) > param2:
            recent_edges.pop(0)

        # Jeżeli wracamy do bazy, możemy spróbować dopełnić czas (opcjonalne)
        if current_node == road_layout.baza:
            remaining_time = Tmax - time_used
            if remaining_time <= 0:
                break
            # Spróbujemy dołożyć jeszcze jakąś krawędź z bazy
            all_edges_baza = road_layout.get_edges_from_vertex(current_node)
            # Filtrujemy je odrzucając krawędzie z 'recent_edges'
            possible_edges = [e for e in all_edges_baza if e not in recent_edges]
            random.shuffle(possible_edges)  # by wprowadzić losowość

            for candidate_edge in possible_edges:
                cost_candidate = candidate_edge.dlugosc / machine.speed
                if time_used + cost_candidate <= Tmax:
                    new_route.append(candidate_edge)
                    time_used += cost_candidate
                    current_node = candidate_edge.koniec
                    break  # Można dołożyć tylko jedną taką krawędź, by uniknąć pętli
            break  # W każdym razie kończymy

    # Nowa trasa dla wybranego etapu
    old_etap = machine.route[etap_id]
    if new_route and new_route != old_etap:
        machine.route[etap_id] = new_route
        print(f"[Priority] Zaktualizowano etap {etap_id} w maszynie {machine_id}.")
    else:
        print(f"[Priority] Nie wprowadzono skutecznej zmiany dla maszyny {machine_id} (etap {etap_id}).")

    return current_solution


def neighbor_from_least_used_edge(current_solution, road_layout, Tmax, param2=2):
    """
    Tworzy nową trasę (w jednym etapie) dla losowo wybranej maszyny,
    zaczynając od najmniej używanej krawędzi w current_solution.
    Następnie dodaje kolejne krawędzie, dopóki nie przekroczymy Tmax 
    lub nie natrafimy na sytuację bez wyjścia.

    Dodatkowo:
    - Używamy param2, by unikać natychmiastowego powtarzania niedawno wybranych krawędzi.
    - Jeżeli wrócimy do bazy wcześniej, próbujemy dopełnić czas dodając jakąś dodatkową krawędź.
    - Modyfikujemy tylko JEDEN etap (wylosowany).

    Args:
        current_solution (list): Lista obiektów typu Machine.
        road_layout: Graf (z bazą, krawędziami i metodą get_edges_from_vertex).
        Tmax (float): Maksymalny czas na jeden etap.
        param2 (int): Liczba ostatnich krawędzi, których nie chcemy powtarzać natychmiast.

    Returns:
        list: Zaktualizowana lista maszyn (current_solution).
    """

    if not current_solution:
        print("[LeastUsed] Brak maszyn w current_solution.")
        return current_solution

    # Zlicz użycia każdej krawędzi
    edge_usage = {edge: 0 for edge in road_layout.krawedzie}
    for machine in current_solution:
        for stage in machine.route:
            for edge in stage:
                edge_usage[edge] += 1

    # Znajdź najmniej używaną krawędź
    least_used_edge = min(edge_usage, key=edge_usage.get)
    print(f"[LeastUsed] Najrzadziej używana krawędź: {least_used_edge}, liczba użyć: {edge_usage[least_used_edge]}.")

    # Wybierz losowo maszynę do modyfikacji
    machine_to_update = random.choice(current_solution)
    if not machine_to_update.route:
        print("[LeastUsed] Wybrana maszyna nie ma etapów. Brak zmian.")
        return current_solution

    etap_id = random.randint(0, len(machine_to_update.route) - 1)

    cost_first = least_used_edge.dlugosc / machine_to_update.speed
    if cost_first > Tmax:
        # Nie zmieścimy się nawet z jedną krawędzią
        print("[LeastUsed] Najrzadziej używana krawędź jest za długa na pojedynczy etap. Brak zmian.")
        return current_solution

    # Budujemy trasę w tym etapie, startując od least_used_edge
    new_route = [least_used_edge]
    time_used = cost_first
    current_node = least_used_edge.koniec

    recent_edges = [least_used_edge]  # by unikać natychmiastowego powtarzania
    while time_used < Tmax:
        all_edges = road_layout.get_edges_from_vertex(current_node)
        if not all_edges:
            # Nie ma jak jechać dalej
            break

        # Filtrowanie krawędzi, by nie wybierać tych z recent_edges
        valid_edges = [edge for edge in all_edges if edge not in recent_edges]

        if not valid_edges:
            # Jeśli wszystko jest w recent_edges
            valid_edges = all_edges  # Bierzemy cokolwiek

        next_edge = random.choice(valid_edges)
        cost_next = next_edge.dlugosc / machine_to_update.speed
        if time_used + cost_next > Tmax:
            break

        new_route.append(next_edge)
        time_used += cost_next
        current_node = next_edge.koniec

        recent_edges.append(next_edge)
        if len(recent_edges) > param2:
            recent_edges.pop(0)

        # Jeśli dotarliśmy do bazy, spróbujmy wypełnić resztę czasu maksymalnie jedną krawędzią
        if current_node == road_layout.baza:
            remaining = Tmax - time_used
            if remaining > 0:
                more_edges = road_layout.get_edges_from_vertex(current_node)
                # Odfiltruj niedawne
                candidate_edges = [e for e in more_edges if e not in recent_edges]
                random.shuffle(candidate_edges)
                for cand in candidate_edges:
                    cost_cand = cand.dlugosc / machine_to_update.speed
                    if time_used + cost_cand <= Tmax:
                        new_route.append(cand)
                        time_used += cost_cand
                        current_node = cand.koniec
                        break
            break

    # Sprawdź, czy faktycznie mamy jakąś nową trasę różną od starej
    old_route = machine_to_update.route[etap_id]
    if new_route and new_route != old_route:
        machine_to_update.route[etap_id] = new_route
        print(f"[LeastUsed] Zaktualizowano etap {etap_id} w maszynie.")
    else:
        print("[LeastUsed] Nie wprowadzono zmian (trasa taka sama lub pusta).")

    return current_solution