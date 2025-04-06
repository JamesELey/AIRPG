import tkinter as tk
from tkinter import ttk


class BaseWindow:
    def __init__(self, parent, title, geometry="400x300"):
        """Initialize base window with common functionality"""
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(geometry)
        self.window.transient(parent)  # Make window modal
        self.window.grab_set()  # Make window modal

        # Create main frame with padding
        self.main_frame = ttk.Frame(self.window, padding="20")
        self.main_frame.pack(fill='both', expand=True)

    def center_window(self):
        """Center the window on the screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')

    def destroy(self):
        """Close the window"""
        self.window.destroy()
