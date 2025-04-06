import tkinter as tk
from tkinter import ttk, messagebox
from .base_window import BaseWindow
import logging # Import logging


class ItemWindow(BaseWindow):
    def __init__(self, parent, game_instance, update_callback=None):
        """Initialize item window"""
        super().__init__(parent, "Use Item", "300x400")
        self.game = game_instance
        self.update_callback = update_callback

        self.create_item_list()
        self.create_buttons()
        self.center_window()

    def create_item_list(self):
        """Create the item selection list"""
        # Show current HP
        ttk.Label(
            self.main_frame,
            text=f"Current HP: {self.game.player.health}/{self.game.player.max_health}"
        ).pack(pady=5)

        # Create listbox for items
        self.item_listbox = tk.Listbox(self.main_frame, height=10)
        self.item_listbox.pack(fill='x', pady=5)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.main_frame, orient='vertical', command=self.item_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.item_listbox.configure(yscrollcommand=scrollbar.set)

        # Populate item list
        for item in self.game.player.inventory:
            self.item_listbox.insert(
                tk.END, f"{item.name} - {item.description}")

    def create_buttons(self):
        """Create action buttons"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(
            button_frame,
            text="Use Item",
            command=self.use_selected_item
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side='right', padx=5)

    def use_selected_item(self):
        """Handle using the selected item"""
        selection = self.item_listbox.curselection()
        if selection:
            index = selection[0]
            # Make sure we have items in inventory
            if index < len(self.game.player.inventory):
                item = self.game.player.inventory[index]
                
                # Check if we should confirm using this item
                if not self.confirm_item_use(item):
                    # User cancelled the item use
                    if self.update_callback:
                        self.update_callback(f"Cancelled using {item.name}")
                    return
                
                logging.info(f"Attempting to use item: '{item.name}'")

                # Use the item via the player object or game logic
                # Assuming item.use returns (success, message)
                if hasattr(item, 'use'):
                    success, message = item.use(self.game.player)
                    if success:
                        logging.info(f"Item used successfully: '{item.name}'. Message: {message}")
                        # Remove consumable item from inventory after successful use
                        # We need a better way to determine if an item is consumable
                        # For now, assume Potions and SickNotes are consumable
                        if "Potion" in item.__class__.__name__ or "SickNote" in item.__class__.__name__:
                            logging.debug(f"Removing used consumable item: '{item.name}'")
                            self.game.player.remove_from_inventory(item)
                        self.create_item_list() # Refresh list
                        self.update_callback(message) # Update parent GUI
                        # Potentially close if only one use action?
                        # self.destroy()
                    else:
                        logging.warning(f"Failed to use item: '{item.name}'. Reason: {message}")
                        messagebox.showwarning("Item Use Failed", message, parent=self.window)
                else:
                    message = f"{item.name} is not usable."
                    logging.error(f"Item use error: '{item.name}' has no use() method.")
                    messagebox.showerror("Item Error", message, parent=self.window)
            else:
                if self.update_callback:
                    self.update_callback("No item selected")

    def confirm_item_use(self, item):
        """
        Confirm whether an item should be used based on its value.
        Returns True if the item use is confirmed or doesn't need confirmation.
        Returns False if the user cancelled.
        """
        # Determine if confirmation is needed based on item value
        threshold = 100  # Items worth 100 or more require confirmation
        
        if hasattr(item, 'value') and item.value >= threshold:
            # Show confirmation dialog for valuable items
            confirmation_title = "Confirm Item Use"
            confirmation_message = f"Are you sure you want to use {item.name} (worth {item.value} credits)?"
            return messagebox.askyesno(confirmation_title, confirmation_message)
        
        # No confirmation needed for common items
        return True

    def refresh_item_list(self):
        """Refresh the item list to show current inventory"""
        # Save current selection if possible
        selected_indices = self.item_listbox.curselection()
        selected_index = selected_indices[0] if selected_indices else None
        
        # Clear and repopulate the list
        self.item_listbox.delete(0, tk.END)
        
        # Populate item list
        for item in self.game.player.inventory:
            self.item_listbox.insert(tk.END, f"{item.name} - {item.description}")
        
        # Restore selection if possible and valid
        if selected_index is not None and selected_index < len(self.game.player.inventory):
            self.item_listbox.selection_set(selected_index)
        elif self.game.player.inventory:
            # Select the first item if nothing was selected before
            self.item_listbox.selection_set(0)

    def on_close(self):
        self.window.destroy()
