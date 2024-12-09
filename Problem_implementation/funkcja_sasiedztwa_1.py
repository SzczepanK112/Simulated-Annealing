import random

def f_sasiad_1(rozw, glebokosc_poszukiwan, graf):
    # Rozwiazanie w formie [[]], gdzie podlisty sa dla roznych etapow opadow
    # Zapamietanie wszystkich podslist przed zlaczeniem w celu pozniejszego odtworzenia
    ilosc_podlist = 0
    dlugosci_podlist = []
    for lista in rozw:
        dlugosci_podlist.append(len(lista))
        ilosc_podlist += 1

    # Polaczenie podlist w jedna liste
    rozw_list = [krawedz for podlista in rozw for krawedz in podlista]

    id1 = random.randint(0, len(rozw_list) - 2) #Wybranie losowej krawedzi dla listy rozwiazania
    licznik = len(rozw_list) # maksymalne przejscie
    id2 = id1 + 1
    zmiana = True
    zmiana_drogi = True
    nowa_droga = [] # Nowa droga pomijajaca jeden wierzcholek

    while zmiana:
        krawedz_los = rozw_list[id1]
        krawedz_next = rozw_list[id2]
        
        max_glebokosc_ = glebokosc_poszukiwan
        start_ = krawedz_los.start
        cel_ = krawedz_next.koniec
        unik_ = krawedz_los.koniec

        # Funkcja ktora szuka nowej drogi z ominieciem danego wierzcholka
        # max_glebokosc - to parametr, ktory okresla jak gleboko funkcja moze szukac nowej drogi
        # Zwrocenie listy krawedzi (nowej drogi) w przypadku braku pusta lista ([])
        def znajdz_nowa_droge(start, cel, max_glebokosc, unik):
            odwiedzone = []  # Lista odwiedzonych wierzchołków
            odwiedzone.append(unik) # Dodanie wierzcholka, ktory ma byc ominięty
            stack = [(start, 0, [])]  # Para (wierzchołek, głębokość, lista_krawedzi)

            while stack:
                aktualny_wierzcholek, glebokosc, sciezka = stack.pop()

                if glebokosc > max_glebokosc:
                    continue
                if aktualny_wierzcholek == cel:
                    return sciezka  # Zwracamy listę krawędzi, które tworzą ścieżkę
                if aktualny_wierzcholek in odwiedzone:
                    continue

                odwiedzone.append(aktualny_wierzcholek)

                # Dodaj sąsiadów do stosu
                for sasiad in aktualny_wierzcholek.sasiedzi:
                    if sasiad not in odwiedzone:
                        # Wyszukujemy krawędź łączącą `current` i `sasiad`
                        krawedz = graf.get_edge(aktualny_wierzcholek, sasiad)
                        if krawedz:
                            # Tworzymy nową listę krawędzi (ścieżka + krawędź)
                            nowa_sciezka = sciezka + [krawedz]
                            stack.append((sasiad, glebokosc + 1, nowa_sciezka))
            
            return []  # Jeśli nie znaleziono drogi, zwracamy pustą listę

        nowa_droga = znajdz_nowa_droge(start_, cel_, max_glebokosc_, unik_)

        if nowa_droga == []:
            if id1 == (len(rozw_list) - 2):
                id1 = 0
                id2 = 1

            else:
                id1 += 1
                id2 += 1
        else:
            zmiana = False

        if id1 == licznik:
            zmiana_drogi = False
            break

    if zmiana_drogi:
        nowe_rozw = rozw_list[0:id1] + nowa_droga + rozw_list[id2+1:]
        return nowe_rozw

    else:
        print("Brak możliwości zmiany")