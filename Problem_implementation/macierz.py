from struktury_danych import Graf, Krawedz, Wierzcholek
from wczytanie_mapy import wczytaj_graf_z_pliku
from solution import Machine, RoadClearingProblem

# Nowe funkcjonalności do klasy Wierzcholek
def get_valid_neighbors(vertex, graf, max_snow_level):
    """
    Pobiera sąsiadów danego wierzchołka, którzy mają przejezdne krawędzie.
    """
    return [n for n in vertex.sasiedzi if graf.get_edge(vertex, n).snow_level <= max_snow_level]

Wierzcholek.get_valid_neighbors = get_valid_neighbors

# Generacja macierzy incydencji
def generate_incidence_matrix(graf):
    """
    Generuje macierz incydencji dla danego grafu.
    """
    size = len(graf.wierzcholki)
    matrix = [[0] * size for _ in range(size)]
    for edge in graf.krawedzie:
        start_idx = graf.wierzcholki.index(edge.start)
        end_idx = graf.wierzcholki.index(edge.koniec)
        matrix[start_idx][end_idx] = 1  # Waga może być dodana zamiast 1
    return matrix

Graf.generate_incidence_matrix = generate_incidence_matrix

# Testowanie wprowadzonych zmian
# Wczytaj graf z pliku
road_layout = wczytaj_graf_z_pliku('/mnt/data/rozklad_ulic.txt')

# Przygotuj dane dla RoadClearingProblem
machines = [Machine(speed=10)]
snowfall_forecast = [5, 10, 15]  # Przykładowy opad śniegu
Tmax = 100  # Maksymalny czas pracy maszyn

# Inicjalizacja problemu
problem = RoadClearingProblem(snowfall_forecast, road_layout, machines, Tmax)

# Uruchomienie pętli głównej
danger_per_stage = problem.mainloop()

# Generacja i wyświetlenie macierzy incydencji
incidence_matrix = road_layout.generate_incidence_matrix()

# Generacja macierzy incydencji w formacie tekstowym

def display_incidence_matrix_as_text(matrix, vertices):
    """
    Wyświetla macierz incydencji w formie tekstowej.
    """
    header = "    " + " ".join(f"{str(v):>8}" for v in vertices)
    rows = []
    for i, row in enumerate(matrix):
        row_text = " ".join(f"{val:>8}" for val in row)
        rows.append(f"{str(vertices[i]):>4} {row_text}")
    return "\n".join([header] + rows)

# Uzyskanie tekstowej reprezentacji macierzy incydencji
vertices = road_layout.wierzcholki
text_representation = display_incidence_matrix_as_text(incidence_matrix, vertices)

# Wyświetlenie macierzy w formacie tekstowym
print("Macierz Incydencji (tekstowa):")
print(text_representation)

# Zwracamy poziomy zagrożenia dla każdego etapu
danger_per_stage
