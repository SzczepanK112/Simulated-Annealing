import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wczytanie_mapy import wczytaj_graf_z_pliku  # Funkcja do wczytania grafu
from solution import RoadClearingProblem, Machine  # Algorytm optymalizacji
from diagnostics import plot_diagnostic_charts
from fast_map_import import get_graph_of_city


class RoadClearingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Optymalizacja Odśnieżania Dróg")
        self.root.geometry("1700x950")
        self.root.configure(bg='white')
        self.root.resizable(False, False)

        # Stylizacja
        style = ttk.Style()
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", foreground="black", font=("Arial", 10))
        style.configure("TButton", background="#DDD", foreground="black", font=("Arial", 10))
        style.configure("Remove.TButton", background="#FF5555", foreground="white", font=("Arial", 10, "bold"))
        style.configure("Start.TButton", background="#555", foreground="black", font=("Arial", 12, "bold"), padding=10)
        style.configure("TEntry", background="#333", foreground="black")

        # Główna ramka
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Układ okna
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Przycisk wczytania pliku
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(pady=5)

        self.load_file_button = ttk.Button(button_frame, text="Wczytaj z pliku txt", command=self.load_file)
        self.load_file_button.pack(side=tk.LEFT, padx=5)

        self.choose_location_button = ttk.Button(button_frame, text="Wybierz lokację", command=self.choose_location)
        self.choose_location_button.pack(side=tk.LEFT, padx=5)
        self.selected_city_label = ttk.Label(left_frame, text="Wybrane miasto: ")
        self.selected_city_label.pack(pady=5)

        # Parametry optymalizacji
        params_frame = ttk.Frame(left_frame)
        params_frame.pack(pady=5)

        self.time_between_label = ttk.Label(params_frame, text="Czas pomiędzy opadami:")
        self.time_between_label.pack(pady=5)
        self.time_between_entry = ttk.Entry(params_frame)
        self.time_between_entry.pack()

        self.snowfall_label = ttk.Label(params_frame, text="Prognoza opadów (np. [3,4,5,6]):")
        self.snowfall_label.pack(pady=5)
        self.snowfall_entry = ttk.Entry(params_frame)
        self.snowfall_entry.pack()

        self.temperature_label = ttk.Label(params_frame, text="Temperatura:")
        self.temperature_label.pack(pady=5)
        self.temperature_entry = ttk.Entry(params_frame)
        self.temperature_entry.pack()

        self.cooling_rate_label = ttk.Label(params_frame, text="Współczynnik chłodzenia (0.95 - 0.99):")
        self.cooling_rate_label.pack(pady=5)
        self.cooling_rate_entry = ttk.Entry(params_frame)
        self.cooling_rate_entry.pack()

        self.max_iterations_label = ttk.Label(params_frame, text="Maksymalna liczba iteracji:")
        self.max_iterations_label.pack(pady=5)
        self.max_iterations_entry = ttk.Entry(params_frame)
        self.max_iterations_entry.pack()

        # Lista maszyn
        self.machine_list_frame = ttk.LabelFrame(left_frame, text='Zarządzanie maszynami', padding=10, height=250)
        self.machine_list_frame.pack_propagate(False)
        self.machine_list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.machine_list = []
        self.machine_canvas = tk.Canvas(self.machine_list_frame, height=250)
        self.machine_scrollbar = ttk.Scrollbar(self.machine_list_frame, orient=tk.VERTICAL, command=self.machine_canvas.yview)
        self.machine_canvas.configure(yscrollcommand=self.machine_scrollbar.set)
        self.scrollable_frame = ttk.Frame(self.machine_canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.machine_canvas.configure(
                scrollregion=self.machine_canvas.bbox("all")
            )
        )
        self.machine_window = self.machine_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=250)
        self.machine_canvas.configure(yscrollcommand=self.machine_scrollbar.set)
        self.machine_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.machine_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        self.machine_canvas.configure(scrollregion=self.machine_canvas.bbox('all'))

        self.add_machine_button = ttk.Button(left_frame, text="Dodaj maszynę", command=self.add_machine)
        self.machine_list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.add_machine_button.pack(pady=5, fill=tk.X)

        # Wybór metody sąsiedztwa
        self.neighborhood_methods = {
            "MK1": 0,  # Załaduj funkcję
            "MK2": 1,  # Załaduj funkcję
            "SK1": 2,  # Załaduj funkcję
            "SK2": 3  # Załaduj funkcję
        }

        self.neighborhood_choices = {}
        self.neighborhood_frame = ttk.LabelFrame(left_frame, text='Wybierz wykorzystywane metody tworzenia sąsiedztwa', padding=10)
        self.neighborhood_frame.pack(pady=10, fill=tk.X, ipadx=5, ipady=5, expand=False)
        for method in self.neighborhood_methods.keys():
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.neighborhood_frame, text=method, variable=var)
            chk.pack(anchor='w')
            self.neighborhood_choices[method] = var

        # Miejsce na graf
        self.graph_frame = ttk.Frame(right_frame)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.figure = plt.Figure(figsize=(10, 5))  # Poszerzenie wykresu horyzontalnie
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Przycisk start na dole
        self.start_button = ttk.Button(left_frame, text="Start", command=self.run_optimization, style="Start.TButton")
        self.start_button.pack(side=tk.BOTTOM, pady=15, fill=tk.X, ipadx=10, ipady=5)

    def choose_location(self):
        city_window = tk.Toplevel(self.root)
        city_window.title("Wybierz miasto")
        city_window.geometry("350x300")
        tk.Label(city_window, text="Wybierz miasto:", font=("Arial", 12)).pack(pady=10)

        cities = ["Warszawa", "Kraków", "Wrocław", "Poznań", "Gdańsk", "Sandomierz", "Kęty"]
        self.selected_city = tk.StringVar(value=cities[0])

        for city in cities:
            tk.Radiobutton(city_window, text=city, variable=self.selected_city, value=city).pack(anchor='w')

        def set_city():
            self.selected_city_label.config(text=f"Wybrane miasto: {self.selected_city.get()}")
            city_window.destroy()
            self.root.update_idletasks()
            city_window.destroy()

            try:
                self.road_graph = get_graph_of_city(self.selected_city.get(), custom_drogi=["tertiary", "residential"])
                print("Graf załadowany")
                self.draw_graph()
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się wczytać grafu: {e}")

        ttk.Button(city_window, text="OK", command=set_city).pack(pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pliki tekstowe", "*.txt")])
        if file_path:
            try:
                self.road_graph = wczytaj_graf_z_pliku(file_path)
                print("Graf załadowany")
                self.draw_graph()
                messagebox.showinfo("Sukces", "Plik został wczytany poprawnie!")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się wczytać grafu: {e}")

    def draw_graph(self):
        if not hasattr(self, 'road_graph'):
            messagebox.showerror("Błąd", "Graf nie został wczytany.")
            return

        self.ax.clear()
        self.road_graph.rysuj(ax=self.ax, show_labels=False, show_edge_labels=False, node_size=50, edge_width=2)
        self.canvas.draw()

    def add_machine(self):
        if len(self.machine_list) >= 7:
            messagebox.showwarning("Limit osiągnięty", "Nie można dodać więcej niż 7 maszyn.")
            return
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.X, pady=2)
        label = ttk.Label(frame, text=f"Maszyna {len(self.machine_list) + 1} - Prędkość (km/h):")
        label.pack(side=tk.LEFT)
        entry = ttk.Entry(frame, width=5, font=("Arial", 10), justify='center', foreground='black')
        entry.pack(side=tk.LEFT, padx=5)
        remove_button = tk.Button(frame, text="X", command=lambda: self.remove_machine(frame), bg='red', fg='white', font=("Arial", 10, "bold"))
        remove_button.pack(padx=0)
        self.machine_list.append((frame, label, entry, remove_button))
        self.scrollable_frame.update_idletasks()
        self.machine_canvas.configure(scrollregion=self.machine_canvas.bbox("all"))

    def remove_machine(self, frame):
        frame.destroy()
        self.machine_list = [m for m in self.machine_list if m[0] != frame]
        self.scrollable_frame.update_idletasks()
        self.machine_canvas.configure(scrollregion=self.machine_canvas.bbox("all"))

    def run_optimization(self):
        if not hasattr(self, 'road_graph') or self.road_graph is None:
            messagebox.showerror("Błąd", "Najpierw wczytaj plik z układem ulic.")
            return

        try:
            Tmax = int(self.time_between_entry.get())
            max_iterations = int(self.max_iterations_entry.get())
            snowfall_forecast = list(map(int, self.snowfall_entry.get().strip('[]').split(',')))
            temperature = float(self.temperature_entry.get())
            cooling_rate = float(self.cooling_rate_entry.get())

            machines = []
            for frame, label, entry, remove_button in self.machine_list:
                try:
                    speed = float(entry.get())
                    machines.append(Machine(speed=speed))
                except ValueError:
                    messagebox.showerror("Błąd", "Podaj poprawne wartości prędkości dla wszystkich maszyn.")
                    return

            selected_methods = [key for key, var in self.neighborhood_choices.items() if var.get()]
            if not selected_methods:
                messagebox.showerror("Błąd", "Wybierz przynajmniej jedną metodę sąsiedztwa.")
                return

            # Załaduj funkcje sąsiedztwa
            neighborhood_functions = [self.neighborhood_methods[method] for method in selected_methods]

            problem = RoadClearingProblem(snowfall_forecast, self.road_graph, machines, Tmax)
            best_solution, best_danger, diagnostics = problem.simulated_annealing_2(
                initial_temperature=temperature,
                cooling_rate=cooling_rate,
                max_iterations=max_iterations,
                choose_neighbour_function=neighborhood_functions
            )

            messagebox.showinfo("Optymalizacja zakończona", f"Najlepszy poziom zagrożenia: {best_danger}")

            self.visualize_solution(diagnostics, best_solution)

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się uruchomić optymalizacji: {e}")

    def visualize_solution(self, diagnostics, solution):
        if not solution:
            return

        self.road_graph.rysuj_z_rozwiazaniem(solution[0], ax=self.ax)
        plot_diagnostic_charts(*diagnostics)


if __name__ == "__main__":
    root = tk.Tk()
    app = RoadClearingApp(root)
    root.mainloop()
