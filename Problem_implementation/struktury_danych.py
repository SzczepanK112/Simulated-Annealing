import math
import copy
import matplotlib.pyplot as plt
import networkx as nx
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
    
    def __hash__(self):
        return hash((self.x, self.y))

    def get_distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class Krawedz:  # Obrazuje ulice polaczona przez dwa wierzcholki
    def __init__(self, start, koniec, priorytet=0, pasy=1):
        self.start = start
        self.koniec = koniec
        self.priorytet = priorytet  # priorytet w zakresie 0-100
        self.pasy = pasy  # ilosc pasow
        self.dlugosc = self.oblicz_dlugosc()
        self.snow_level = 0

    def oblicz_dlugosc(self):
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

    def rysuj(self, size_x=10, size_y=10):
        G = nx.Graph()

        # Dodaj wierzchołki
        for w in self.wierzcholki:
            G.add_node((w.x, w.y))

        # Dodaj krawędzie
        edge_labels = {}  # Słownik do przechowywania etykiet krawędzi
        for k in self.krawedzie:
            G.add_edge((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))
            # Etykiety z priorytetem i liczbą pasów
            edge_labels[((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))] = f"Pr: {k.priorytet}, SL: {k.snow_level}"

        # Określamy pozycje wierzchołków
        pos = {(w.x, w.y): (w.x, w.y) for w in self.wierzcholki}

        # Zwiększenie rozmiar obrazu
        plt.figure(figsize=(size_x, size_y))

        # Rysowanie grafu
        nx.draw(G, pos, with_labels=True, node_size=600, node_color='skyblue', font_size=10, font_weight='bold',
                edge_color='gray', width=4)

        # Rysowanie etykiet krawędzi
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

        # Rysowanie punktu początkowego (baza) na czerwono, ale z pustym środkiem
        if self.baza:
            plt.scatter(self.baza.x, self.baza.y, color='red', s=750, label='Baza', edgecolors='red', facecolors='none',
                        zorder=5, linewidth=3)

        # Wyświetlanie grafu z legendą
        plt.legend()
        plt.show()

    def rysuj_z_rozwiazaniem(self, rozwiazanie: list, size_x=10, size_y=10):
        """
        Rysuje graf z zaznaczeniem określonych krawędzi w rozwiązaniu.
        - rozwiazanie: lista list krawędzi (rozwiazanie dla jednej maszyny).
        """
        # Kolory dla etapów
        kolory_etapow = ['black', 'brown', 'green', 'blue', 'purple', 'red', 'pink', 'orange']
        # Liczba etapów
        stage_number = len(rozwiazanie)
        # Rozszerzanie listy kolorów, aby była wystarczająco długa
        kolory_etapow = kolory_etapow * ((stage_number // len(kolory_etapow)) + 1)

        G = nx.DiGraph()  # Używamy DiGraph, aby obsługiwać kierunkowe krawędzie

        # Dodaj wierzchołki
        for w in self.wierzcholki:
            G.add_node((w.x, w.y))

        # Dodaj krawędzie
        edge_labels = {}
        for k in self.krawedzie:
            G.add_edge((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))
            # Etykiety z priorytetem i poziomem śniegu
            edge_labels[((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))] = f"Pr: {k.priorytet}, SL: {k.snow_level}"

        # Określamy pozycje wierzchołków
        pos = {(w.x, w.y): (w.x, w.y) for w in self.wierzcholki}

        # Zwiększenie rozmiaru obrazu
        plt.figure(figsize=(size_x, size_y))

        # Rysowanie grafu (domyślnych krawędzi bez przezroczystości i strzałek)
        nx.draw(
            G, pos, with_labels=True, node_size=600, node_color='skyblue', font_size=10, font_weight='bold',
            edge_color='gray', width=2
        )

        # Rysowanie etykiet krawędzi
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

        # Zaznaczenie krawędzi rozwiązania (kolorem w zależności od etapu)
        already_drawn_edges = set()  # Zbiór już narysowanych krawędzi (dla obu kierunków)
        
        num_etapow = len(rozwiazanie)  # Liczba etapów (kroków)
        for idx, etap in enumerate(rozwiazanie):
            # Oblicz kolor na podstawie etapu (czerpiemy z listy kolorów)
            kolor = kolory_etapow[idx % len(kolory_etapow)]  # Używamy modula, aby cyklicznie przechodzić przez kolory

            # Oblicz grubość linii dla tego etapu (start od 8, zmniejszaj o 1 dla każdego kolejnego etapu)
            grubosc = max(10 - idx, 2)  # Minimalna grubość to 1, żeby nie była 0

            for krawedz in etap:
                # Krawędź w kierunku (start -> koniec) oraz w kierunku odwrotnym (koniec -> start)
                edge_tuple = (krawedz.start.x, krawedz.start.y, krawedz.koniec.x, krawedz.koniec.y)
                reverse_edge_tuple = (krawedz.koniec.x, krawedz.koniec.y, krawedz.start.x, krawedz.start.y)
                
                # Narysowanie krawędzi, jeśli nie została jeszcze narysowana w danym kierunku
                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=[((krawedz.start.x, krawedz.start.y), (krawedz.koniec.x, krawedz.koniec.y))],
                    edge_color=kolor, width=grubosc, alpha=0.5, arrows=True, arrowstyle='-|>', arrowsize=14
                )
                # Dodanie krawędzi do zbioru narysowanych krawędzi (w obu kierunkach)
                already_drawn_edges.add(edge_tuple)
                already_drawn_edges.add(reverse_edge_tuple)

        # Rysowanie punktu początkowego (baza) na czerwono, ale z pustym środkiem
        if self.baza:
            plt.scatter(
                self.baza.x, self.baza.y, color='red', s=750, label='Baza', edgecolors='red', facecolors='none',
                zorder=5, linewidth=3
            )

        # Wyświetlanie grafu z legendą
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
