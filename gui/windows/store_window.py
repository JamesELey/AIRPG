import tkinter as tk
from tkinter import ttk, messagebox
from gui.windows.base_window import BaseWindow # Assuming BaseWindow exists

# Helper function for centering windows (can be reused or moved)
def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

class StoreWindow(BaseWindow):
    def __init__(self, parent, game_instance):
        """Initialize the store window."""
        super().__init__(parent, "Item Store", "500x450")
        self.game = game_instance
        self.store_inventory = self.game.get_store_inventory()

        # Title and Credits Display
        ttk.Label(self.main_frame, text="Welcome to the Shop!", font=("TkDefaultFont", 14, "bold")).pack(pady=(0, 10))
        self.credits_label = ttk.Label(self.main_frame, text=f"Your Credits: {self.game.player.credits} G")
        self.credits_label.pack(pady=(0, 15))

        # Item Listbox
        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.item_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("TkDefaultFont", 10), height=12)
        self.item_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.item_listbox.yview)

        # Populate Listbox
        self.populate_store_list()

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        ttk.Button(button_frame, text="Buy Selected", command=self.buy_selected_item).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

        self.center_window()
        self.window.focus_set()

    def populate_store_list(self):
        """Fills the listbox with items and prices."""
        self.item_listbox.delete(0, tk.END) # Clear existing items
        for index, item_data in enumerate(self.store_inventory):
            name = item_data.get('name', 'Unknown Item')
            price = item_data.get('price', '?')
            description = item_data.get('description', 'No description')
            display_text = f"{name} - {price} G ({description})"
            self.item_listbox.insert(tk.END, display_text)

    def update_credits_label(self):
        """Updates the displayed player credits."""
        self.credits_label.config(text=f"Your Credits: {self.game.player.credits} G")

    def buy_selected_item(self):
        """Handles the purchase of the selected item."""
        selected_indices = self.item_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select an item to buy.", parent=self.window)
            return

        selected_index = selected_indices[0]
        selected_item_data = self.store_inventory[selected_index]
        item_name = selected_item_data.get('name', 'the selected item')
        item_price = selected_item_data.get('price', 0)

        confirm = messagebox.askyesno("Confirm Purchase",
                                      f"Buy {item_name} for {item_price} G?",
                                      parent=self.window)
        if confirm:
            data_to_send = selected_item_data
            success, message = self.game.purchase_item(data_to_send)
            if success:
                messagebox.showinfo("Purchase Successful", message, parent=self.window)
                self.update_credits_label() # Update displayed credits
            else:
                messagebox.showerror("Purchase Failed", message, parent=self.window) 