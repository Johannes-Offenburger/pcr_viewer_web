import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
import math
import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PCRViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("PCR CSV Viewer – interaktiv & übersichtlich")
        self.master.geometry("1100x850")

        self.label = tk.Label(master, text="Keine Datei ausgewählt", font=("Arial", 10))
        self.label.pack(pady=5)

        self.btn = tk.Button(master, text="CSV auswählen", command=self.load_and_plot_csv)
        self.btn.pack(pady=5)

        self.compare_btn = tk.Button(master, text="Kanalvergleich", command=self.open_compare_window)
        self.compare_btn.pack(pady=5)

        self.canvas = None

        # zum späteren Zugriff
        self.df = None
        self.cycle = None
        self.data_cols = []

    def load_and_plot_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV-Dateien", "*.csv")])
        if not file_path:
            return

        filename = os.path.basename(file_path)
        self.label.config(text=f"Angezeigt: {filename}")

        try:
            df = pd.read_csv(file_path, sep=';')
        except Exception as e:
            print(f"Fehler beim Einlesen: {e}")
            return

        if 'cycle' not in df.columns:
            print("Spalte 'cycle' nicht gefunden.")
            return

        cycle = df['cycle']

        selected_cols = [
            'temp_wellblock', 'temp_heatsink', 'temp_led',
            'F1', 'F2', 'FZ', 'F3', 'F4', 'FY', 'F5', 'FXL',
            'F6', 'F7', 'F8', 'NIR', 'VIS'
        ]
        data_cols = [col for col in selected_cols if col in df.columns]
        num_plots = len(data_cols)
        cols = 2
        rows = math.ceil(num_plots / cols)

        fig, axes = plt.subplots(rows, cols, figsize=(14, rows * 2.8), squeeze=False)
        fig.suptitle("PCR-Kurvenübersicht", fontsize=16, weight='bold')

        for idx, col in enumerate(data_cols):
            r, c = divmod(idx, cols)
            ax = axes[r][c]
            ax.plot(cycle, df[col], label=col, color='tab:blue', linewidth=1.5)
            ax.set_title(col, fontsize=10, fontweight='bold', pad=8)
            ax.tick_params(labelbottom=True, labelleft=True, labelsize=8)
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.grid(True, linestyle='--', alpha=0.4)
            for spine in ax.spines.values():
                spine.set_edgecolor('lightgray')
                spine.set_linewidth(1)

        for i in range(num_plots, rows * cols):
            r, c = divmod(i, cols)
            fig.delaxes(axes[r][c])

        plt.tight_layout(rect=[0, 0.04, 1, 0.95])

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Speichern für Vergleich
        self.df = df
        self.cycle = cycle
        self.data_cols = data_cols

    def open_compare_window(self):
        if self.df is None or self.cycle is None:
            print("Bitte zuerst eine CSV laden.")
            return

        win = tk.Toplevel(self.master)
        win.title("Kanalvergleich")
        win.geometry("600x500")

        tk.Label(win, text="Zähler (oben):").pack(pady=5)
        var_a = tk.StringVar(value=self.data_cols[0])
        dropdown_a = tk.OptionMenu(win, var_a, *self.data_cols)
        dropdown_a.pack()

        tk.Label(win, text="Nenner (unten):").pack(pady=5)
        var_b = tk.StringVar(value=self.data_cols[1])
        dropdown_b = tk.OptionMenu(win, var_b, *self.data_cols)
        dropdown_b.pack()

        # Plotbereich
        fig, ax = plt.subplots(figsize=(7, 3))
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True, pady=10)

        def update_plot(*args):
            a = var_a.get()
            b = var_b.get()
            if not a or not b:
                return
            try:
                y = self.df[a] / self.df[b]
            except Exception as e:
                print(f"Fehler bei Division: {e}")
                return

            ax.clear()
            ax.plot(self.cycle, y, label=f"{a} / {b}", color='tab:green')
            ax.set_title(f"{a} / {b}", fontsize=12, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.4)
            ax.tick_params(labelsize=8)
            ax.set_xlabel("")
            ax.set_ylabel("")
            canvas.draw()

        # Automatische Aktualisierung bei Auswahländerung
        var_a.trace_add('write', update_plot)
        var_b.trace_add('write', update_plot)
        update_plot()

# App starten
if __name__ == "__main__":
    root = tk.Tk()
    app = PCRViewer(root)
    root.mainloop()