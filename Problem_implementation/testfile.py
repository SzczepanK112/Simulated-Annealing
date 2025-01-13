from wczytanie_mapy import *
from solution import *

nazwa_pliku = 'rozklad_ulic.txt'
# Tworzenie grafu
graf = wczytaj_graf_z_pliku(nazwa_pliku)

snowfall_forecast = [8, 3, 7, 2, 1, 5]

m1 = Machine()
m2 = Machine()
m3 = Machine(speed=2)

machines = [m1, m2, m3]

Tmax = 20

problem = RoadClearingProblem(snowfall_forecast, graf, machines, Tmax)

best_solution, best_danger = problem.simulated_annealing_2(
    initial_temperature=1000,
    cooling_rate=0.98,
    max_iterations=1000,
    max_iterations_in_step=0
)

# print("Najlepsze rozwiązanie:", [machine.route for machine in best_solution])
rozw = [machine.route for machine in best_solution]

for j, route in enumerate(rozw):
    route_l = 0
    print(f'------- MASZYNA {j + 1} -------')
    for i, stage in enumerate(route):
        stage_l = 0
        for edge in stage:
            length = edge.oblicz_dlugosc()
            stage_l += length
            route_l += length

        print(f'Etap: {i + 1} -> długość: {stage_l}')
    print(f'\nTrasa: {route} \n')
    print(f'Długość całości: {route_l}\n')

print(Tmax * len(snowfall_forecast))
print("Poziom zagrożenia:", best_danger)
