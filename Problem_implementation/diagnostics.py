import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# Lista danych wykresów (globalna zmienna do aktualizacji w funkcji)
plots = []
current_plot = [0]  # Indeks aktualnego wykresu


def update_plot(ax, index):
    """Aktualizuje wykres na podstawie indeksu."""
    plot = plots[index]
    ax.clear()
    ax.plot(plot["x"], plot["y"])
    ax.set_title(plot["title"])
    ax.set_ylabel(plot["ylabel"])
    ax.set_xlabel("Iteracja")
    ax.grid(True)
    fig.canvas.draw()


def next_plot(event):
    """Przełącza na kolejny wykres."""
    if current_plot[0] < len(plots) - 1:
        current_plot[0] += 1
        update_plot(ax, current_plot[0])


def prev_plot(event):
    """Przełącza na poprzedni wykres."""
    if current_plot[0] > 0:
        current_plot[0] -= 1
        update_plot(ax, current_plot[0])


def plot_diagnostic_charts(danger, best_danger, temperature):
    """Rysuje interaktywne wykresy diagnostyczne."""
    global plots, fig, ax  # Odwołanie do globalnych zmiennych

    # Aktualizacja danych wykresów
    plots = [
        {"title": "Poziom niebezpieczeństwa osiągnięty w danej iteracji", "x": range(len(danger)), "y": danger,
         "ylabel": "Niebezpieczeństwo"},
        {"title": "Zaakceptowany poziom niebezpieczeństwa", "x": range(len(best_danger)), "y": best_danger,
         "ylabel": "Niebezpieczeństwo"},
        {"title": "Temperatura", "x": range(len(temperature)), "y": temperature, "ylabel": ""},
    ]
    current_plot[0] = 0  # Reset indeksu wykresu

    # Tworzenie figury i osi
    fig, ax = plt.subplots(figsize=(10, 7))
    plt.subplots_adjust(bottom=0.2)  # Miejsce na przyciski

    # Dodawanie przycisków
    ax_prev = plt.axes((0.1, 0.05, 0.15, 0.075))  # Współrzędne przycisku poprzedniego
    ax_next = plt.axes((0.8, 0.05, 0.15, 0.075))  # Współrzędne przycisku następnego

    btn_prev = Button(ax_prev, "Previous")
    btn_next = Button(ax_next, "Next")

    btn_prev.on_clicked(prev_plot)
    btn_next.on_clicked(next_plot)

    # Rysowanie początkowego wykresu
    update_plot(ax, current_plot[0])

    # Wyświetlanie okna interaktywnego
    plt.show(block=False)  # Nie blokuj programu
    while plt.get_fignums():  # Dopóki istnieją otwarte okna
        plt.pause(0.1)  # Aktualizuj GUI
