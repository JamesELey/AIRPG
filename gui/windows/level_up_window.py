import tkinter as tk
from tkinter import ttk


class LevelUpWindow:
    def __init__(self, parent, player, old_level):
        self.window = tk.Toplevel(parent)
        self.window.title("🎉 Level Up!")
        self.window.geometry("300x400")

        # Create main frame
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Header
        ttk.Label(
            self.main_frame,
            text=f"Level Up! {old_level} → {player.level}",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Stat increases
        stats = [
            ("Max HP", player.max_health, 20),
            ("Attack", player.attack, 5),
            ("Defense", player.defense, 3),
            ("Agility", player.agility, 2),
            ("Max Energy", player.max_energy, 10)
        ]

        for i, (stat_name, current_value, increase) in enumerate(stats, start=1):
            ttk.Label(
                self.main_frame,
                text=f"{stat_name}:",
                font=("Arial", 12)
            ).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)

            ttk.Label(
                self.main_frame,
                text=f"{current_value - increase} → {current_value} (+{increase})",
                font=("Arial", 12)
            ).grid(row=i, column=1, padx=5, pady=5, sticky=tk.E)

        # Close button
        ttk.Button(
            self.main_frame,
            text="Continue",
            command=self.window.destroy
        ).grid(row=len(stats) + 1, column=0, columnspan=2, pady=20)

        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        parent.wait_window(self.window)
