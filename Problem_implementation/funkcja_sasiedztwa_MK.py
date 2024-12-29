"""
Definicja dwóch funkcji sasiedztwa ->

- parametr 'rozw_aktalne' jest w postaci [Machine_object, Machine_object...]
- zwracane jest rozwiazanie w postaci [[sciezka_1, sciezka_2...], [] ...] - trasa dla jednej wylosowanej maszyny

def f_sasiad_1(rozw_aktalne, glebokosc_poszukiwan, graf, T_max):
    # Funkcja wybiera losowo maszyne, ktorej trasa bedzie modyfikowana
    # Nastepnie przez wybranie losowo sciezki z trasy stara znalezc sie 
    # nowa trase, ktora bedzie omijała jeden wierzcholek
    # Na końcu dzieli cala trase na wstepna ilosc etapow z odpowiednim czasem maksymalnym
    # przez co w efekcie otrzymujemy nowa trase od danego wierzcholka, ktora
    # moze byc krotsza/dluzsza w zaleznosci od wybranych krawedzi 
    # (ograniczona odpowiednim czasem maksymalnym i iloscia etapow)

    # Najwazniejszy jest tutaj parametr 'glebokosc_poszukiwan', ktory mowi przez ile maksymalnie
    # wierzcholkow mozna przejsc w celu ominiecia zadanego wierzcholka, jezeli parametr jest duzy
    # przez ograniczenie ilosci etapow i T_max, ktore moze usunac otrzymany fragment rozwiazania,
    # mozemy otrzymac od wybranego wierzcholka calkowicie nowa trase

    # Najlepsze efekty dla modyfikacji ostatniego etapu, przy innych duze prawdopodobienstwo 
    # powtarzania trasy, szczegolnie przy duzej wartosci parametru 'glebokosc_poszukiwan'

def f_sasiad_2(rozw_aktalne, graf, T_max):
    # Funkcja wybiera losowo maszyne, ktorej trasa bedzie modyfikowana
    # Nastepnie wybierany jest losowo etap (z pominieciem pierwszego - od bazy), 
    # gdzie w nowym rozwiazaniu zachowane zostaja poprzednie etapy, a etapy od wybranego
    # tworzone sa calkowicie od nowa wybierajac sciezki z wiekszym priorytetem
    # (z kilkoma ograniczeniami zapetlania sciezki)
    # W nowo tworzonych etapach uwzgledniany jest czas maksymalny

    # Parametr 'param2' odpowiada za ilosc zapamietanych, poprzednich sciezek dla aktualnej
    # sciezki, ktore nie moga sie powtorzyc, im wieksza jego wartosci tym mniej powtorzen, ale mniejsza
    # waga priorytetow

"""

import random

def f_sasiad_1(rozw_aktalne, glebokosc_poszukiwan, graf, T_max):
    # Funkcja wybiera losowo maszyne, ktorej trasa bedzie modyfikowana
    # Nastepnie przez wybranie losowo sciezki z trasy stara znalezc sie 
    # nowa trase, ktora bedzie omijała jeden wierzcholek
    # Na końcu dzieli cala trase na wstepna ilosc etapow z odpowiednim czasem maksymalnym
    # przez co w efekcie otrzymujemy nowa trase od danego wierzcholka, ktora
    # moze byc krotsza/dluzsza w zaleznosci od wybranych krawedzi 
    # (ograniczona odpowiednim czasem maksymalnym i iloscia etapow)

    # Najwazniejszy jest tutaj parametr 'glebokosc_poszukiwan', ktory mowi przez ile maksymalnie
    # wierzcholkow mozna przejsc w celu ominiecia zadanego wierzcholka, jezeli parametr jest duzy
    # przez ograniczenie ilosci etapow i T_max, ktore moze usunac otrzymany fragment rozwiazania,
    # mozemy otrzymac od wybranego wierzcholka calkowicie nowa trase

    # wybranie jednej maszyny (losowo)
    maszyna_id = random.randint(0, len(rozw_aktalne) - 1)
    maszyna = rozw_aktalne[maszyna_id]
    predkosc_maszyny = maszyna.speed
    rozw = maszyna.route

    # rozwiazanie w formie [[]], gdzie podlisty sa dla roznych etapow opadow (dla jednej maszyny)
    ilosc_etapow = len(rozw) # zapamietania liczby etapow
    # polaczenie podlist w jedna liste
    rozw_list = [krawedz for podlista in rozw for krawedz in podlista]

    id1 = random.randint(0, len(rozw_list) - 2) # wybranie losowej krawedzi
    id2 = id1 + 1

    licznik_stop = 0 # maksymalne przejscie kolejnych sciezek - przeszukanie krawedzi 
    if id1 == 0:
        licznik_stop = len(rozw_list) - 2
    else:
        licznik_stop = id1 - 1

    zmiana = True
    zmiana_drogi = True
    nowa_droga = [] # nowa droga pomijajaca jeden wierzcholek

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

        # przejscie do kolejnej sciezki w etapie w celu ponownego znalezienia pominiecia
        if nowa_droga == []:
            if id1 == (len(rozw_list) - 2):
                id1 = 0
                id2 = 1

            else:
                id1 += 1
                id2 += 1
        else:
            zmiana = False

        if id1 == licznik_stop:
            zmiana_drogi = False
            break

    if zmiana_drogi:
        nowe_rozw = rozw_list[0:id1] + nowa_droga + rozw_list[id2+1:]

        # teraz cala liste dzielimy na dana poczatkowa ilosc etapow, z odpowiednim czasem maksymalnym
        lista_rozw = [[] for lista in range(ilosc_etapow)]
        etap = 0
        czas_koszt = 0

        for krawedz in nowe_rozw:
            czas_koszt += krawedz.oblicz_dlugosc() / predkosc_maszyny

            if czas_koszt >= T_max:
                etap += 1
                czas_koszt = 0

                if etap > (ilosc_etapow - 1):
                    break
                else:
                    lista_rozw[etap].append(krawedz)

            else: 
                lista_rozw[etap].append(krawedz)

        return lista_rozw

    else:
        print("Brak zmiany!")
        return rozw
    



def f_sasiad_2(rozw_aktalne, graf, T_max, param2=2):
    # Funkcja wybiera losowo maszyne, ktorej trasa bedzie modyfikowana
    # Nastepnie wybierany jest losowo etap (z pominieciem pierwszego - od bazy), 
    # gdzie w nowym rozwiazaniu zachowane zostaja poprzednie etapy, a etapy od wybranego
    # tworzone sa calkowicie od nowa wybierajac sciezki z wiekszym priorytetem
    # (z kilkoma ograniczeniami zapetlania sciezki)
    # W nowo tworzonych etapach uwzgledniany jest czas maksymalny

    # Parametr 'param2' odpowiada za ilosc zapamietanych, poprzednich sciezek dla aktualnej
    # sciezki, ktore nie moga sie powtorzyc, im wieksza jego wartosci tym mniej powtorzen, ale mniejsza
    # waga priorytetow

    # wybranie jednej maszyny (losowo)
    maszyna_id = random.randint(0, len(rozw_aktalne) - 1)
    maszyna = rozw_aktalne[maszyna_id]
    predkosc_maszyny = maszyna.speed
    rozw = maszyna.route

    # rozwiazanie w formie [[]], gdzie podlisty sa dla roznych etapow opadow (dla jednej maszyny)
    ilosc_etapow = len(rozw) # zapamietania liczby etapow
    etap = random.randint(1, ilosc_etapow - 1) # wybranie losowego etapu (oprocz poczatkowego)

    if ilosc_etapow == 0:
        print("Brak zmiany! Tylko jeden etap!")
        return rozw

    nowe_rozw = rozw[:etap]  # zachowujemy etapy do wybranego w niezmienionej formie
    start_ = rozw[etap][0].start

    # zbior krawedzi poprzedniego etapu
    etap_back = etap - 1
    odwiedzone_krawedzie = set()
    for krawedz in rozw[etap_back]:
        odwiedzone_krawedzie.add(krawedz.start)
        odwiedzone_krawedzie.add(krawedz.koniec)

    for etap_id in range(etap, ilosc_etapow):
        czas_koszt = 0
        nowa_trasa = [] # trasa w danym etapie

        while czas_koszt < T_max:
            # posortowanie sąsiadów wierzchołka `start_` według priorytetu
            sasiadujace_krawedzie = graf.get_edges_from_vertex(start_)
            sasiadujace_krawedzie.sort(key=lambda krawedz: -krawedz.priorytet)  # Sortowanie malejąco po priorytecie

            # wybór krawędzi o najwyższym priorytecie, która nie prowadzi do odwiedzonego wierzchołka
            wybrana_krawedz = None
            for krawedz in sasiadujace_krawedzie:
                if krawedz.koniec not in [k.start for k in nowa_trasa[-param2:]] and krawedz.koniec not in odwiedzone_krawedzie:
                    wybrana_krawedz = krawedz
                    break
                elif krawedz.koniec not in [k.start for k in nowa_trasa[-param2:]]:
                    wybrana_krawedz = krawedz
                    break
                    

            # dodajemy wybraną krawędź do trasy i aktualizujemy czas
            nowa_trasa.append(wybrana_krawedz)
            czas_koszt += wybrana_krawedz.oblicz_dlugosc() / predkosc_maszyny
            start_ = wybrana_krawedz.koniec  # Aktualizacja bieżącego wierzchołka

            # sprawdzamy, czy przekroczyliśmy maksymalny czas
            if czas_koszt >= T_max:
                break

        # dodanie nowej trasy do etapu
        nowe_rozw.append(nowa_trasa)

        odwiedzone_krawedzie = set()
        for krawedz in rozw[etap_id]:
            odwiedzone_krawedzie.add(krawedz.start)
            odwiedzone_krawedzie.add(krawedz.koniec)

    return nowe_rozw

