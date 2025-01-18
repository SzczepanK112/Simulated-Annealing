import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from solution import *
from struktury_danych import *
import networkx as nx
from typing import List, Union
import random


class SnowClearingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Snow Clearing Optimization System")
        self.root.geometry("1200x800")

        # Initialize data structures
        self.road_layout = None
        self.machines = []
        self.current_solution = None

        # Create main container
        self.main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create left panel for controls
        self.create_left_panel()

        # Create right panel for visualization
        self.create_right_panel()

        # Initialize matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.visualization_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_left_panel(self):
        left_panel = ttk.Frame(self.main_container)
        self.main_container.add(left_panel, weight=1)

        # Graph Creation Section
        graph_frame = ttk.LabelFrame(left_panel, text="Graph Creation", padding=10)
        graph_frame.pack(fill=tk.X, padx=5, pady=5)

        # Base location inputs
        ttk.Label(graph_frame, text="Base Location:").pack()
        base_frame = ttk.Frame(graph_frame)
        base_frame.pack(fill=tk.X)
        self.base_x = ttk.Entry(base_frame, width=10)
        self.base_x.pack(side=tk.LEFT, padx=2)
        self.base_y = ttk.Entry(base_frame, width=10)
        self.base_y.pack(side=tk.LEFT, padx=2)
        ttk.Button(base_frame, text="Set Base", command=self.set_base).pack(side=tk.LEFT, padx=2)

        # Edge creation inputs
        ttk.Label(graph_frame, text="Add Edge:").pack()
        edge_frame = ttk.Frame(graph_frame)
        edge_frame.pack(fill=tk.X)

        # Start point
        start_frame = ttk.Frame(edge_frame)
        start_frame.pack(fill=tk.X)
        ttk.Label(start_frame, text="Start:").pack(side=tk.LEFT)
        self.start_x = ttk.Entry(start_frame, width=10)
        self.start_x.pack(side=tk.LEFT, padx=2)
        self.start_y = ttk.Entry(start_frame, width=10)
        self.start_y.pack(side=tk.LEFT, padx=2)

        # End point
        end_frame = ttk.Frame(edge_frame)
        end_frame.pack(fill=tk.X)
        ttk.Label(end_frame, text="End:").pack(side=tk.LEFT)
        self.end_x = ttk.Entry(end_frame, width=10)
        self.end_x.pack(side=tk.LEFT, padx=2)
        self.end_y = ttk.Entry(end_frame, width=10)
        self.end_y.pack(side=tk.LEFT, padx=2)

        # Priority and lanes
        prop_frame = ttk.Frame(edge_frame)
        prop_frame.pack(fill=tk.X)
        ttk.Label(prop_frame, text="Priority:").pack(side=tk.LEFT)
        self.priority = ttk.Entry(prop_frame, width=10)
        self.priority.pack(side=tk.LEFT, padx=2)
        ttk.Label(prop_frame, text="Lanes:").pack(side=tk.LEFT)
        self.lanes = ttk.Entry(prop_frame, width=10)
        self.lanes.pack(side=tk.LEFT, padx=2)

        ttk.Button(edge_frame, text="Add Edge", command=self.add_edge).pack(pady=5)

        # Optimization Section
        opt_frame = ttk.LabelFrame(left_panel, text="Optimization Settings", padding=10)
        opt_frame.pack(fill=tk.X, padx=5, pady=5)

        # Machine settings
        machine_frame = ttk.Frame(opt_frame)
        machine_frame.pack(fill=tk.X)
        ttk.Label(machine_frame, text="Number of Machines:").pack(side=tk.LEFT)
        self.num_machines = ttk.Entry(machine_frame, width=10)
        self.num_machines.pack(side=tk.LEFT, padx=2)

        # Snowfall forecast
        forecast_frame = ttk.Frame(opt_frame)
        forecast_frame.pack(fill=tk.X)
        ttk.Label(forecast_frame, text="Snowfall Forecast:").pack(side=tk.LEFT)
        self.forecast = ttk.Entry(forecast_frame)
        self.forecast.pack(side=tk.LEFT, padx=2)

        # Time limit
        time_frame = ttk.Frame(opt_frame)
        time_frame.pack(fill=tk.X)
        ttk.Label(time_frame, text="Time Limit (Tmax):").pack(side=tk.LEFT)
        self.tmax = ttk.Entry(time_frame, width=10)
        self.tmax.pack(side=tk.LEFT, padx=2)

        # Optimization buttons
        ttk.Button(opt_frame, text="Initialize Problem", command=self.initialize_problem).pack(pady=5)
        ttk.Button(opt_frame, text="Run Optimization", command=self.run_optimization).pack(pady=5)

        # Output Section
        output_frame = ttk.LabelFrame(left_panel, text="Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=10)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def create_right_panel(self):
        self.visualization_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.visualization_frame, weight=2)

    def set_base(self):
        try:
            x = float(self.base_x.get())
            y = float(self.base_y.get())
            if not self.road_layout:
                self.road_layout = Graf()
            self.road_layout.dodaj_baze(x, y)
            self.update_visualization()
            self.log_output("Base set at ({}, {})".format(x, y))
        except ValueError:
            messagebox.showerror("Error", "Invalid base coordinates")

    def add_edge(self):
        try:
            start = (float(self.start_x.get()), float(self.start_y.get()))
            end = (float(self.end_x.get()), float(self.end_y.get()))
            priority = int(self.priority.get())
            lanes = int(self.lanes.get())

            if not self.road_layout:
                self.road_layout = Graf()

            self.road_layout.dodaj_krawedz(start, end, priority, lanes)
            self.update_visualization()
            self.log_output(f"Edge added: {start} -> {end}")
        except ValueError:
            messagebox.showerror("Error", "Invalid edge parameters")

    def initialize_problem(self):
        try:
            num_machines = int(self.num_machines.get())
            forecast = [int(x) for x in self.forecast.get().split(',')]
            tmax = float(self.tmax.get())

            if not self.road_layout:
                raise ValueError("No road layout defined")

            self.machines = [Machine(speed=1) for _ in range(num_machines)]
            self.current_solution = RoadClearingProblem(forecast, self.road_layout, self.machines, tmax)
            self.log_output("Problem initialized successfully")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def run_optimization(self):
        if not self.current_solution:
            messagebox.showerror("Error", "Please initialize the problem first")
            return

        try:
            solution, danger = self.current_solution.simulated_annealing_2(
                initial_temperature=100,
                cooling_rate=0.95,
                max_iterations=1000,
                max_iterations_in_step=100
            )
            self.log_output(f"Optimization completed. Final danger level: {danger}")
            self.update_visualization(show_solution=True)
        except Exception as e:
            messagebox.showerror("Error", f"Optimization failed: {str(e)}")

    def update_visualization(self, show_solution=False):
        self.ax.clear()
        if self.road_layout:
            if show_solution and self.current_solution:
                self.road_layout.rysuj_z_rozwiazaniem([m.route for m in self.machines])
            else:
                self.road_layout.rysuj()
        self.canvas.draw()

    def log_output(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)


def main():
    root = tk.Tk()
    app = SnowClearingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()