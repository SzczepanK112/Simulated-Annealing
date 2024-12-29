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

Tmax = 30

problem = RoadClearingProblem(snowfall_forecast, graf, machines, Tmax)

best_solution, best_danger = problem.simulated_annealing(
    initial_temperature=500,
    cooling_rate=0.98,
    max_iterations=30000
)

print("Najlepsze rozwiązanie:", [machine.route for machine in best_solution])
print("Poziom zagrożenia:", best_danger)

