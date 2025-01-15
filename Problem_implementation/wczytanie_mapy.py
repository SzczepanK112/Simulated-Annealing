from struktury_danych import *

# Funkcja realizuje wczytanie grafu z podanego rozkladu ulic w pliku 'rozklad_ulic.txt', 
# gdzie dane reprezentowane sa w nastepujacy sposob:
# (wierzcholek_1) (wierzcholek_2) priorytet pasy


def wczytaj_graf_z_pliku(nazwa_pliku):
    graf = Graf(true_location=False)  # Tworzymy pusty graf
    
    with open(nazwa_pliku, 'r') as plik:
        linie = plik.readlines()  # Wczytujemy wszystkie linie z pliku
        
        # Sprawdzamy, czy linia nie jest pusta
        linie = [linia.strip() for linia in linie if linia.strip()]

        # Pierwszy punkt traktujemy jako bazę
        pierwsza_linijka = linie[0]
        pkt_start, pkt_koniec, priorytet, pasy = pierwsza_linijka.split(" ")
        pkt_start = eval(pkt_start)  # Konwertujemy np. "(0, 0)" na krotkę (0, 0)
        pkt_koniec = eval(pkt_koniec)
        priorytet = int(priorytet)
        pasy = int(pasy)
        
        graf.dodaj_krawedz(pkt_start, pkt_koniec, priorytet, pasy)
        graf.dodaj_baze(*pkt_start) # Dodanie bazy

        # Przechodzimy przez resztę linii - wczytanie reszty ulic
        for linia in linie[1:]:
            try:
                pkt_start, pkt_koniec, priorytet, pasy = linia.split(" ")
                pkt_start = eval(pkt_start)
                pkt_koniec = eval(pkt_koniec)
                priorytet = int(priorytet)
                pasy = int(pasy)
                
                graf.dodaj_krawedz(pkt_start, pkt_koniec, priorytet, pasy)
            except ValueError as e:
                print(f"Nieprawidłowy format w linii: '{linia}'. Błąd: {e}")
                continue  # Ignorujemy błędną linię

    return graf  # Zwracamy gotowy graf 
