import math
import matplotlib.pyplot as plt
import networkx as nx


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

    def get_danger_level(self):
        return self.snow_level * self.priorytet * self.pasy


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

    def rysuj(self):
        G = nx.Graph()

        # Dodaj wierzchołki
        for w in self.wierzcholki:
            G.add_node((w.x, w.y))

        # Dodaj krawędzie
        edge_labels = {}  # Słownik do przechowywania etykiet krawędzi
        for k in self.krawedzie:
            G.add_edge((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))
            # Etykiety z priorytetem i liczbą pasów
            edge_labels[((k.start.x, k.start.y), (k.koniec.x, k.koniec.y))] = f"Pr: {k.priorytet}, Pasy: {k.pasy}"

        # Określamy pozycje wierzchołków
        pos = {(w.x, w.y): (w.x, w.y) for w in self.wierzcholki}

        # Zwiększenie rozmiar obrazu
        plt.figure(figsize=(10, 10))

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
