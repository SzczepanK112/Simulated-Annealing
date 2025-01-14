import math
import copy
import matplotlib.pyplot as plt
import networkx as nx
from geopy.distance import geodesic

import matplotlib.colors as mcolors


class Wierzcholek:  # Obrazuje poczatek/koniec ulicy lub skrzyzowanie ulic
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sasiedzi = []  # Lista sąsiednich wierzcholkow 

    def dodaj_sasiada(self, krawedz):
        if krawedz not in self.sasiedzi:  # Dodaj tylko jeśli nie ma jeszcze takiego sąsiada
            self.sasiedzi.append(krawedz)

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):  # Pozwala porownac identycznosc dwoch wierzcholkow
        if isinstance(other, Wierzcholek):
            return (self.x, self.y) == (other.x, other.y)
        return False

    def __lt__(self, other):
        return self.x + self.y < other.x + other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def get_distance(self, other, true_location=True):

        if true_location:
            coords_self = (self.y, self.x)  # (latitude, longitude) dla bieżącego punktu
            coords_other = (other.y, other.x)  # (latitude, longitude) dla punktu 'other'

            # Oblicz odległość geodezyjną między dwoma punktami
            return geodesic(coords_self, coords_other).meters  # Odległość w metrach

        else:
            return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class Krawedz:  # Obrazuje ulice polaczona przez dwa wierzcholki
    def __init__(self, start, koniec, priorytet=0, pasy=1):
        self.start = start
        self.koniec = koniec
        self.priorytet = priorytet  # priorytet w zakresie 0-100
        self.pasy = pasy  # ilosc pasow
        self.dlugosc = self.oblicz_dlugosc()
        self.snow_level = 0

    def oblicz_dlugosc(self, true_location=True):

        if true_location:
            coords_start = (self.start.y, self.start.x)  # (latitude, longitude) dla startu
            coords_koniec = (self.koniec.y, self.koniec.x)  # (latitude, longitude) dla końca

            # Oblicz odległość geodezyjną (w metrach)
            return geodesic(coords_start, coords_koniec).meters

        else:
            return math.sqrt((self.start.x - self.koniec.x) ** 2 + (self.start.y - self.koniec.y) ** 2)

    def __repr__(self):
        return f"{self.start} -> {self.koniec}"

    def __eq__(self, other):
        # Uznajemy krawędzie za równe, jeśli mają takie same punkty, niezależnie od kierunku
        return (self.start == other.start and self.koniec == other.koniec) or \
               (self.start == other.koniec and self.koniec == other.start)

    def get_danger_level(self):
        return self.snow_level * self.priorytet * self.pasy
    
    def __hash__(self):
        # Hashowanie powinno uwzględniać tylko unikalne krawędzie, niezależnie od kierunku
        return hash((min(self.start, self.koniec), max(self.start, self.koniec)))


class Graf:  # Obrazuje pelny rozklad ulic/skrzyzowan
    def __init__(self):
        self.wierzcholki = []
        self.krawedzie = []
        self.baza = None  # Punkt początkowy (baza)

    def dodaj_baze(self, x, y):
        # Sprawdzenie, czy wierzchołek o podanych współrzędnych już istnieje
        for wierzcholek in self.wierzcholki:
            if wierzcholek.x == x and wierzcholek.y == y:
                self.baza = wierzcholek  # Ustaw bazę na istniejący wierzchołek
                return
            
        # Jeśli wierzchołek nie istnieje, dodaj nowy jako bazę
        self.baza = Wierzcholek(x, y)
        self.wierzcholki.append(self.baza)

    def dodaj_wierzcholek(self, x, y):
        # Sprawdzanie, czy wierzchołek o tych współrzędnych już istnieje
        for wierzcholek in self.wierzcholki:
            if wierzcholek.x == x and wierzcholek.y == y:
                return wierzcholek  # Zwróć istniejący wierzchołek

        # Jeśli wierzchołek nie istnieje, stwórz nowy
        nowy_wierzcholek = Wierzcholek(x, y)
        self.wierzcholki.append(nowy_wierzcholek)
        return nowy_wierzcholek

    def get_edge(self, point1, point2):
        """
        Znajduje krawędź pomiędzy dwoma wierzchołkami (point1, point2).
        Zwraca krawędź, jeśli istnieje, w przeciwnym przypadku zwraca None.

        Args:
        - point1: krotka (x1, y1) reprezentująca pierwszy wierzchołek
        - point2: krotka (x2, y2) reprezentująca drugi wierzchołek

        Returns:
        - krawedz: Krawędź między wierzchołkami lub None, jeśli krawędź nie istnieje
        """
        # Jeśli point1 i point2 są obiektami Wierzcholek, przekształamy je na krotki
        if isinstance(point1, Wierzcholek):
            point1 = (point1.x, point1.y)
        if isinstance(point2, Wierzcholek):
            point2 = (point2.x, point2.y)

        for krawedz in self.krawedzie:
            # Sprawdzamy, czy punkt1 jest początkiem krawędzi, a punkt2 końcem
            if (krawedz.start.x, krawedz.start.y) == point1 and (krawedz.koniec.x, krawedz.koniec.y) == point2:
                return krawedz

        return None  # Jeśli nie znaleziono krawędzi
    
    def get_edges_from_vertex(self, wierzcholek):
        """
        Zwraca listę krawędzi wychodzących z danego wierzchołka.
        """
        edges = []
        for krawedz in self.krawedzie:
            if krawedz.start == wierzcholek:
                edges.append(krawedz)
        return edges

    def dodaj_krawedz(self, punkt1, punkt2, priorytet, pasy):
        # Dodaje krawędź do grafu między punktami (x1, y1) a (x2, y2), uwzględniając kierunek.

        w1 = self.dodaj_wierzcholek(*punkt1)
        w2 = self.dodaj_wierzcholek(*punkt2)

        krawedz_1 = Krawedz(w1, w2, priorytet, pasy)
        self.krawedzie.append(krawedz_1)

        krawedz_2 = Krawedz(w2, w1, priorytet, pasy)
        self.krawedzie.append(krawedz_2)

        # Powiąż krawędź z wierzchołkami
        w1.dodaj_sasiada(w2)
        w2.dodaj_sasiada(w1)

    def __repr__(self):
        result = "Graf:\n"
        for krawedz in self.krawedzie:
            result += f"  {krawedz}\n"
        return result
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    #-----------------------------------------------------METODY DO RYSOWANIA GRAFU-----------------------------------------------------------------------------------#
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------#

    def rysuj(self, size_x=10, size_y=10, show_coords=True, decimal_places=2, show_labels=True, node_size=600, label_font_size=10, edge_width=4, show_edge_labels=True):
        """
        Rysuje graf

        Parametry:
        - size_x, size_y: rozmiar wykresu.
        - show_coords: czy wyświetlać współrzędne węzłów.
        - decimal_places: do ilu miejsc po przecinku zaokrąglać współrzędne.
        - show_labels: czy wyświetlać etykiety węzłów.
        - node_size: rozmiar węzła.
        - label_font_size: wielkość czcionki etykiet węzłów.
        - edge_width: grubość linii (krawędzi).
        - show_edge_labels: czy wyświetlać tekst (etykiety) na krawędziach.
        """

        G = nx.Graph()

        # Dodaj wierzchołki do NetworkX
        for w in self.wierzcholki:
            G.add_node((w.x, w.y))

        # Przygotuj słownik etykiet krawędzi
        edge_labels = {}
        for k in self.krawedzie:
            G.add_edge((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))
            # Etykieta krawędzi (np. priorytet, snow_level)
            edge_labels[((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))] = f"Pr: {k.priorytet}, SL: {k.snow_level}"

        # Określamy pozycje węzłów (tutaj po prostu współrzędne x,y)
        pos = {(w.x, w.y): (w.x, w.y) for w in self.wierzcholki}

        # Inicjalizacja matplotlib
        plt.figure(figsize=(size_x, size_y))

        # Rysowanie grafu (bez etykiet węzłów)
        # Ustawiamy 'width=edge_width', aby kontrolować grubość linii
        nx.draw(
            G,
            pos,
            with_labels=False,
            node_size=node_size,
            node_color='skyblue',
            edge_color='gray',
            width=edge_width
        )

        # Rysowanie etykiet krawędzi (o ile włączone show_edge_labels)
        if show_edge_labels:
            # Skaluj rozmiar czcionki etykiet krawędzi proporcjonalnie do edge_width
            # Bazowo było font_size=6 przy width=4, więc:
            edge_label_font_size = int(6 * (edge_width / 4))
            nx.draw_networkx_edge_labels(
                G,
                pos,
                edge_labels=edge_labels,
                font_size=edge_label_font_size
            )

        # Jeśli chcemy wyświetlać etykiety węzłów
        if show_labels:
            node_labels = {}
            for i, w in enumerate(self.wierzcholki):
                if show_coords:
                    # Zaokrąglone współrzędne do 'decimal_places'
                    label_x = f"{w.x:.{decimal_places}f}"
                    label_y = f"{w.y:.{decimal_places}f}"
                    node_labels[(w.x, w.y)] = f"({label_x}, {label_y})"
                else:
                    # Nazwy W0, W1, W2... itp.
                    node_labels[(w.x, w.y)] = f"W{i}"

            nx.draw_networkx_labels(
                G,
                pos,
                labels=node_labels,
                font_size=label_font_size,
                font_color='black'
            )

        # Rysowanie bazy (jeśli istnieje)
        if self.baza:
            plt.scatter(
                self.baza.x,
                self.baza.y,
                color='red',
                s=node_size * 1.25,
                label='Baza',
                edgecolors='red',
                facecolors='none',
                zorder=5,
                linewidth=3
            )

        plt.legend()
        plt.show()



    def rysuj_z_rozwiazaniem(self, rozwiazanie: list, size_x=10, size_y=10,show_coords=True, decimal_places=2, show_labels=True,node_size=600, label_font_size=10,
                            edge_width=2, show_edge_labels=True):
        """
        Rysuje graf z zaznaczeniem określonych krawędzi w rozwiązaniu.
        - rozwiazanie: lista list krawędzi (rozwiazanie dla jednej maszyny).
        - size_x, size_y: rozmiar wykresu.
        - show_coords: czy wyświetlać współrzędne węzłów.
        - decimal_places: do ilu miejsc po przecinku zaokrąglać współrzędne.
        - show_labels: czy wyświetlać etykiety węzłów.
        - node_size: rozmiar węzła.
        - label_font_size: wielkość czcionki etykiet węzłów.
        - edge_width: grubość linii krawędzi.
        - show_edge_labels: czy wyświetlać etykiety na krawędziach.
        """
        import matplotlib.pyplot as plt
        import networkx as nx

        # Ustawienia kolorów dla etapów
        kolory_etapow = ['black', 'brown', 'green', 'blue', 'purple', 'red', 'pink', 'orange']
        stage_number = len(rozwiazanie)
        kolory_etapow = kolory_etapow * ((stage_number // len(kolory_etapow)) + 1)

        # Tworzenie grafu NetworkX
        G = nx.DiGraph()

        # Dodawanie wierzchołków
        for w in self.wierzcholki:
            G.add_node((w.x, w.y))

        # Dodawanie krawędzi z etykietami
        edge_labels = {}
        for k in self.krawedzie:
            G.add_edge((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))
            edge_labels[((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))] = f"Pr: {k.priorytet}, SL: {k.snow_level}"

        # Pozycje węzłów
        pos = {(w.x, w.y): (w.x, w.y) for w in self.wierzcholki}

        plt.figure(figsize=(size_x, size_y))

        # Rysowanie podstawowego grafu z ustawioną grubością linii
        nx.draw(
            G, pos,
            with_labels=False,  # etykiety węzłów dodamy później
            node_size=node_size,
            node_color='skyblue',
            edge_color='gray',
            width=edge_width
        )

        # Rysowanie etykiet krawędzi, jeśli włączone
        if show_edge_labels:
            # Skalowanie font_size dla etykiet krawędzi proporcjonalnie do edge_width
            base_edge_font_size = 6  # podstawowy rozmiar czcionki przy width=2
            scaled_font_size = base_edge_font_size * (edge_width / 2)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=scaled_font_size)

        # Rysowanie etykiet węzłów, jeśli włączone
        if show_labels:
            node_labels = {}
            for i, w in enumerate(self.wierzcholki):
                if show_coords:
                    label_x = f"{w.x:.{decimal_places}f}"
                    label_y = f"{w.y:.{decimal_places}f}"
                    node_labels[(w.x, w.y)] = f"({label_x}, {label_y})"
                else:
                    node_labels[(w.x, w.y)] = f"W{i}"
            nx.draw_networkx_labels(
                G, pos,
                labels=node_labels,
                font_size=label_font_size,
                font_color='black'
            )

        # Rysowanie zaznaczenia rozwiązań na drogach
        already_drawn_edges = set()
        for idx, etap in enumerate(rozwiazanie):
            kolor = kolory_etapow[idx % len(kolory_etapow)]
            grubosc = max(edge_width*3 - idx, edge_width/2)  # dynamiczna grubość linii dla etapu
            for krawedz in etap:
                edge_tuple = (krawedz.start.x, krawedz.start.y, krawedz.koniec.x, krawedz.koniec.y)
                reverse_edge_tuple = (krawedz.koniec.x, krawedz.koniec.y, krawedz.start.x, krawedz.start.y)
                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=[((krawedz.start.x, krawedz.start.y), (krawedz.koniec.x, krawedz.koniec.y))],
                    edge_color=kolor,
                    width=grubosc,
                    alpha=0.5,
                    arrows=True,
                    arrowstyle='-|>',
                    arrowsize=14
                )
                already_drawn_edges.add(edge_tuple)
                already_drawn_edges.add(reverse_edge_tuple)

        # Rysowanie bazy (jeśli istnieje)
        if self.baza:
            plt.scatter(
                self.baza.x, self.baza.y,
                color='red', s=750, label='Baza', edgecolors='red',
                facecolors='none', zorder=5, linewidth=3
            )

        plt.legend()
        plt.show()




    def rysuj_dwa_rozwiazania(self, rozwiazanie1: list, rozwiazanie2: list, size_x=10, size_y=10):
        """
        Rysuje dwa grafy obok siebie z dwoma rozwiązaniami.
        - rozwiazanie1, rozwiazanie2: lista list krawędzi (rozwiazanie dla dwóch różnych maszyn).
        """
        # Kolory dla etapów
        kolory_etapow = ['black', 'brown', 'green', 'blue', 'purple', 'red', 'pink', 'orange']

        # Liczba etapów w obu rozwiązaniach
        stage_number1 = len(rozwiazanie1)
        stage_number2 = len(rozwiazanie2)

        # Rozszerzanie listy kolorów, aby była wystarczająco długa
        kolory_etapow1 = kolory_etapow * ((stage_number1 // len(kolory_etapow)) + 1)
        kolory_etapow2 = kolory_etapow * ((stage_number2 // len(kolory_etapow)) + 1)

        # Tworzenie wykresu z dwoma sub-plotami
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(size_x * 2, size_y))  # 1 rząd, 2 kolumny
        
        # Rysowanie grafów
        self.rysuj_graf(ax1, rozwiazanie1, kolory_etapow1)
        self.rysuj_graf(ax2, rozwiazanie2, kolory_etapow2)

        # Wyświetlanie wykresu
        plt.show()

    def rysuj_graf(self, ax, rozwiazanie, kolory_etapow):
        """
        Pomocnicza metoda (dla metody rysuj_dwa_rozwiazania) rysująca jeden graf z rozwiązaniem.
        """
        G = nx.DiGraph()  # Używamy DiGraph, aby obsługiwać kierunkowe krawędzie

        # Dodaj wierzchołki
        for w in self.wierzcholki:
            G.add_node((w.x, w.y))

        # Dodaj krawędzie
        edge_labels = {}
        for k in self.krawedzie:
            G.add_edge((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))
            edge_labels[((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))] = f"Pr: {k.priorytet}, SL: {k.snow_level}"

        # Określamy pozycje wierzchołków
        pos = {(w.x, w.y): (w.x, w.y) for w in self.wierzcholki}

        # Rysowanie grafu (domyślnych krawędzi bez przezroczystości i strzałek)
        nx.draw(
            G, pos, with_labels=True, node_size=600, node_color='skyblue', font_size=10, font_weight='bold',
            edge_color='gray', width=2, ax=ax
        )

        # Rysowanie etykiet krawędzi
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6, ax=ax)

        # Zaznaczenie krawędzi rozwiązania (kolorem w zależności od etapu)
        already_drawn_edges = set()

        num_etapow = len(rozwiazanie)
        for idx, etap in enumerate(rozwiazanie):
            kolor = kolory_etapow[idx % len(kolory_etapow)]  # Używamy modula, aby cyklicznie przechodzić przez kolory
            grubosc = max(10 - idx, 2)  # Minimalna grubość to 1, żeby nie była 0

            for krawedz in etap:
                edge_tuple = (krawedz.start.x, krawedz.start.y, krawedz.koniec.x, krawedz.koniec.y)
                reverse_edge_tuple = (krawedz.koniec.x, krawedz.koniec.y, krawedz.start.x, krawedz.start.y)

                # Narysowanie krawędzi, jeśli nie została jeszcze narysowana w danym kierunku
                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=[((krawedz.start.x, krawedz.start.y), (krawedz.koniec.x, krawedz.koniec.y))],
                    edge_color=kolor, width=grubosc, alpha=0.5, arrows=True, arrowstyle='-|>', arrowsize=14, ax=ax
                )
                already_drawn_edges.add(edge_tuple)
                already_drawn_edges.add(reverse_edge_tuple)

        # Rysowanie punktu początkowego (baza) na czerwono, ale z pustym środkiem
        if self.baza:
            ax.scatter(
                self.baza.x, self.baza.y, color='red', s=750, label='Baza', edgecolors='red', facecolors='none',
                zorder=5, linewidth=3
            )

        # Wyświetlanie grafu z legendą
        ax.legend()

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------#
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------#