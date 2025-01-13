import osmnx as ox
import networkx as nx
import math

'''
Do poprawy jeszcze lepsze przypisywanie priorytetu do drogi / lub zmienic na poprzednia wersje czyli dany rodzaj drogi to dany priorytet 
'''

from struktury_danych import Graf, Wierzcholek, Krawedz

def oblicz_odleglosc_e(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def oblicz_priorytet(edge_data, x_u, y_u, x_v, y_v, center_x, center_y, max_distance):
    """
    Zwraca priorytet krawędzi, uwzględniając typ drogi oraz jej odległość od centrum.
    
    Parametry:
    - edge_data: słownik atrybutów krawędzi z OSM
    - (x_u, y_u), (x_v, y_v): współrzędne węzłów krawędzi
    - (center_x, center_y): współrzędne środka obszaru
    - max_distance: maksymalna odległość (np. promień), dla której interpolujemy współczynnik
    
    Zwraca: priorytet w zakresie 1-100
    """
    # 1. Bazowy priorytet w zależności od typu drogi
    highway_type = edge_data.get("highway", None)
    if isinstance(highway_type, list):
        highway_type = highway_type[0]

    mapping = {
        "motorway": 80,             ## -> Autostrada, wielopasowa, bezkolizyjna.
        "trunk": 75,                ## -> Droga ekspresowa lub inna bardzo ważna arteria (niższa ranga niż motorway).
        "primary": 70,              ## -> Droga główna (np. droga krajowa).
        "secondary": 60,            ## -> Droga średniej rangi (np. droga wojewódzka).
        "tertiary": 50,             ## -> Droga powiatowa lub lokalna łącząca miejscowości.
        "residential": 40,          ## -> Droga w terenie zabudowanym (osiedlowa).
        "service": 30,              ## -> Droga serwisowa, np. dojazdy do parkingów, stacji benzynowych.
    }
    base_priority = mapping.get(highway_type, 20)

    # 2. Oblicz midpoint krawędzi i dystans do środka
    mid_x = (x_u + x_v) / 2.0
    mid_y = (y_u + y_v) / 2.0
    distance_mid = oblicz_odleglosc_e(mid_x, mid_y, center_x, center_y)

    # 3. Interpolacja współczynnika zależnego od odległości
    max_coeff = 1.5
    min_coeff = 0.5
    # Jeśli odległość większa lub równa max_distance, ustawiamy minimalny współczynnik
    if distance_mid >= max_distance:
        factor = min_coeff
    else:
        # Interpolacja liniowa: bliżej środka → współczynnik bliżej max_coeff, dalej → bliżej min_coeff
        factor = max_coeff - ((max_coeff - min_coeff) * (distance_mid / max_distance))

    # 4. Oblicz końcowy priorytet i przytnij do zakresu 1-100
    final_priority = base_priority * factor
    if final_priority < 1:
        final_priority = 1
    elif final_priority > 100:
        final_priority = 100

    return int(final_priority)


def oblicz_pasy(edge_data):
    """
    Funkcja pobierająca liczbę pasów z atrybutu 'lanes' w OSM.
    Jeśli brak danych, zwraca 1.
    """
    lanes = edge_data.get("lanes", 1)
    if isinstance(lanes, list):
        lanes = lanes[0]  # czasem jest listą

    try:
        return int(lanes)
    except (ValueError, TypeError):
        return 1


def pobierz_graf_osm_z_punktu(center_point, dist=500, dist_type="bbox", network_type="drive", drogi_glowne=False, custom_drogi=None):
    """
    Pobiera wycinek mapy z OSM wokół zadanego punktu (center_point)
    w promieniu dist (w metrach) i tworzy obiekt klasy 'Graf'.

    Parametry:
    - center_point: (lat, lon) - punkt środka.
    - dist: promień w metrach (lub połowa boku, jeśli dist_type='bbox').
    - dist_type: 'bbox', 'circle' lub 'network' (rodzaj bufora).
    - network_type: 'drive', 'walk', 'bike' itp.
    - drogi_glowne: bool, jeśli True -> pobieramy tylko główne kategorie dróg.
    - custom_drogi: lista stringów, np. ["motorway", "primary", "secondary"], jeśli chcesz sam zdefiniować filter.

    Zwraca: obiekt klasy 'Graf'
    """

    # Ustalenie, czy budujemy custom_filter
    #    - jeśli drogi_glowne=True, bierzemy z góry ustalony zestaw najważniejszych dróg
    #    - jeśli custom_drogi jest podane, budujemy filtr z tej listy
    #    - w przeciwnym razie None (OSMnx pobierze wg domyślnego 'network_type')

    if custom_drogi and isinstance(custom_drogi, list) and len(custom_drogi) > 0:
        # Zbuduj wyrażenie np.: '["highway"~"motorway|primary|secondary"]'
        filter_str = "|".join(custom_drogi)
        custom_filter = f'["highway"~"{filter_str}"]'
    elif drogi_glowne:
        # Przykład: motorway, primary, secondary, trunk, tertiary
        custom_filter = '["highway"~"motorway|trunk|primary|secondary|trunk|tertiary"]'
    else:
        # Bez filtra
        custom_filter = None

    G_osm = ox.graph_from_point(
        center_point,
        dist=dist,
        dist_type=dist_type,
        network_type=network_type,
        custom_filter=custom_filter
    )

    graf = Graf()

    # dodanie bazy
    if len(G_osm.nodes) > 0:
        pierwszy_wezel_id = list(G_osm.nodes)[0]
        x_baza = G_osm.nodes[pierwszy_wezel_id]["x"]
        y_baza = G_osm.nodes[pierwszy_wezel_id]["y"]
        graf.dodaj_baze(x_baza, y_baza)


    center_lat, center_lon = center_point
    max_distance = dist
    for u, v, key, data in G_osm.edges(keys=True, data=True):
        x_u = G_osm.nodes[u]["x"]
        y_u = G_osm.nodes[u]["y"]
        x_v = G_osm.nodes[v]["x"]
        y_v = G_osm.nodes[v]["y"]

        priorytet = oblicz_priorytet(data, x_u, y_u, x_v, y_v, center_lon, center_lat, max_distance)
        pasy = oblicz_pasy(data)

        graf.dodaj_krawedz((x_u, y_u), (x_v, y_v), priorytet, pasy)

    return graf