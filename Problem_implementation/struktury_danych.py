import math
import matplotlib.pyplot as plt
import networkx as nx

class Wierzcholek: # Obrazuje poczatek/koniec ulicy lub skrzyzowanie ulic
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sasiedzi = []  # Lista sąsiednich wierzcholkow 

    def dodaj_sasiada(self, krawedz):
        self.sasiedzi.append(krawedz)

    def __repr__(self):
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other): # Pozwala porownac identycznosc dwoch wierzcholkow
        if isinstance(other, Wierzcholek):
            return (self.x, self.y) == (other.x, other.y)
        return False
    

class Krawedz: # Obrazuje ulice polaczona przez dwa wierzcholki
    def __init__(self, start, koniec, priorytet=0, pasy=1):
        self.start = start
        self.koniec = koniec
        self.priorytet = priorytet # priorytet w zakresie 0-100
        self.pasy = pasy  # ilosc pasow
        self.dlugosc = self.oblicz_dlugosc() 
        
    def oblicz_dlugosc(self):
        return math.sqrt((self.start.x - self.koniec.x) ** 2 + (self.start.y - self.koniec.y) ** 2)

    def __repr__(self):
        return f"{self.start} -> {self.koniec}"
    

class Graf: # Obrazuje pelny rozklad ulic/skrzyzowan
    def __init__(self):
        self.wierzcholki = []
        self.krawedzie = []
        self.baza = None  # Punkt początkowy (baza)

    def dodaj_baze(self, x, y):
        # Ustawia punkt początkowy
        self.baza = Wierzcholek(x, y)
        if self.baza not in self.wierzcholki:
            self.wierzcholki.append(self.baza)

    def dodaj_wierzcholek(self, x, y):
        # Dodaje wierzchołek do grafu, jeśli nie istnieje.

        w = Wierzcholek(x, y)
        if w not in self.wierzcholki:
            self.wierzcholki.append(w)
        return w

    def dodaj_krawedz(self, punkt1, punkt2, priorytet, pasy):
        # Dodaje krawędź do grafu między punktami (x1, y1) a (x2, y2), uwzględniając kierunek.

        w1 = self.dodaj_wierzcholek(*punkt1)
        w2 = self.dodaj_wierzcholek(*punkt2)
        krawedz = Krawedz(w1, w2, priorytet, pasy)
        self.krawedzie.append(krawedz)

        # Powiąż krawędź z wierzchołkami
        w1.dodaj_sasiada(w2)
        if pasy > 1:
            w2.dodaj_sasiada(w1)
        # Jeśli krawędź/ulica ma tylko jeden pas, dodajemy tylko od wierzchołka startowego do końcowego

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
        pos = { (w.x, w.y): (w.x, w.y) for w in self.wierzcholki }

        # Zwiększenie rozmiar obrazu
        plt.figure(figsize=(10, 10)) 

        # Rysowanie grafu
        nx.draw(G, pos, with_labels=True, node_size=600, node_color='skyblue', font_size=10, font_weight='bold', edge_color='gray', width=4)

        # Rysowanie etykiet krawędzi
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

        # Rysowanie punktu początkowego (baza) na czerwono, ale z pustym środkiem
        if self.baza:
            plt.scatter(self.baza.x, self.baza.y, color='red', s=750, label='Baza', edgecolors='red', facecolors='none', zorder=5, linewidth=3)

        # Wyświetlanie grafu z legendą
        plt.legend()
        plt.show()
