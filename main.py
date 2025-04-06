import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import traceback
import logging # Import logging
from grid_game import GridGame
from gui.game_gui import GameGUI
from datetime import datetime

SAVE_FILENAME = "savegame.json"

def show_error_and_exit(title, message, error=None):
    """Show error message and exit the program"""
    full_message = message
    if error:
        full_message += f"\n\nError details:\n{str(error)}"
        print(f"Error: {str(error)}")
        traceback.print_exc()

    try:
        messagebox.showerror(title, full_message)
    except:
        print(f"\n{title}\n{full_message}")

    sys.exit(1)


def center_window(window, width, height):
    """Center a tkinter window on the screen."""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def launch_game_gui(root, game_instance):
    """Helper function to launch the main game GUI."""
    # Clean up any existing widgets in root before launching GUI
    for widget in root.winfo_children():
        widget.destroy()
    root.title("Grid Game") # Reset title
    GameGUI(root, game_instance)
    center_window(root, 1200, 900) # Use GameGUI default size

def _format_metadata_for_display(metadata: dict) -> str:
    """Format save metadata into a readable string for list display (Copied from GameGUI for main menu use)."""
    if not metadata:
        return "[Empty Slot]"

    player_name = metadata.get('player_name', 'Unknown')
    level = metadata.get('player_level', '?')
    save_time_str = "Unknown Time"
    if metadata.get('save_time'):
        try:
            save_dt = datetime.fromisoformat(metadata['save_time'])
            save_time_str = save_dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            pass # Keep default if format is wrong

    return f"Slot {metadata['slot']}: {player_name} (Lvl {level}) - Saved: {save_time_str}"

def main():
    # --- Setup Logging --- 
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # File Handler (writes logs to a file, overwrites each run)
    log_file = "game_actions.log"

    logging.basicConfig(
        level=logging.INFO, # Log INFO level and above (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'),
            logging.StreamHandler() # Also print logs to console
        ]
    )
    logging.info("--- Game Started ---")

    try:
        logging.info("Initializing Tkinter root window.")
        print("Starting Grid Game...")
        root = tk.Tk()
        root.title("Grid Game - Main Menu")
        root.geometry("300x200")
        center_window(root, 300, 200)

        # --- Main Menu Frame ---
        menu_frame = ttk.Frame(root, padding="20")
        menu_frame.pack(fill='both', expand=True)

        ttk.Label(menu_frame, text="Grid Game", font=("TkDefaultFont", 16, "bold")).pack(pady=(0, 20))

        # --- Button Functions ---
        def attempt_continue_game():
            logging.info("'Continue Game' selected.")
            print("Attempting to continue game...")
            most_recent_slot = GridGame.find_most_recent_save_slot()
            if most_recent_slot:
                logging.info(f"Most recent save found in slot {most_recent_slot}. Attempting load.")
                print(f"Found most recent save in slot {most_recent_slot}. Loading...")
                loaded_game = GridGame.load_game(most_recent_slot)
                if loaded_game:
                    logging.info(f"Game successfully loaded from slot {most_recent_slot}.")
                    launch_game_gui(root, loaded_game)
                else:
                    logging.error(f"Failed to load game from slot {most_recent_slot}.")
                    messagebox.showerror("Load Error", f"Failed to load game from slot {most_recent_slot}.")
            else:
                logging.warning("No save files found to continue.")
                print("No save files found to continue.")
                messagebox.showinfo("Continue Failed", "No save files found. Start a new game or load manually.")

        def open_load_dialog():
            logging.info("'Load Game' selected. Opening load dialog.")
            print("Opening load game dialog...")
            dialog = tk.Toplevel(root)
            dialog.title("Load Game Slot")
            dialog.geometry("450x300")
            dialog.transient(root)
            dialog.grab_set()
            center_window(dialog, 450, 300)
            dialog.focus_set()

            ttk.Label(dialog, text="Select a slot to load:").pack(pady=10)

            list_frame = ttk.Frame(dialog)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=listbox.yview)

            all_metadata = GridGame.get_all_save_metadata()
            slot_data_map = {}
            has_saves = False
            for i, metadata in enumerate(all_metadata):
                slot = i + 1
                display_text = _format_metadata_for_display(metadata)
                listbox.insert(tk.END, display_text)
                slot_data_map[i] = slot
                if metadata:
                    listbox.itemconfig(i, {'fg': 'navy'})
                    has_saves = True
                else:
                    listbox.itemconfig(i, {'fg': 'gray'})

            def perform_load():
                selected_indices = listbox.curselection()
                if not selected_indices:
                    messagebox.showwarning("No Selection", "Please select a slot.", parent=dialog)
                    return

                selected_index = selected_indices[0]
                slot_to_load = slot_data_map[selected_index]
                if not all_metadata[selected_index]: # Check if slot is actually empty
                    messagebox.showwarning("Empty Slot", "This slot is empty.", parent=dialog)
                    return

                logging.info(f"Attempting to load game from slot {slot_to_load} via Load Dialog.")
                print(f"Attempting to load game from slot {slot_to_load}...")
                loaded_game = GridGame.load_game(slot_to_load)
                if loaded_game:
                    logging.info(f"Game successfully loaded from slot {slot_to_load}.")
                    dialog.destroy()
                    launch_game_gui(root, loaded_game)
                else:
                    logging.error(f"Failed to load game from slot {slot_to_load} via Load Dialog.")
                    messagebox.showerror("Load Error", f"Failed to load game from slot {slot_to_load}. The file might be corrupted.", parent=dialog)

            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
            load_button = ttk.Button(button_frame, text="Load", command=perform_load)
            load_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

            if not has_saves:
                load_button.config(state=tk.DISABLED)

        def show_new_game_setup():
            logging.info("'Start New Game' selected.")
            print("Starting new game setup...")
            menu_frame.destroy()
            setup_new_game_screen(root)

        # --- Menu Buttons ---
        continue_button = ttk.Button(menu_frame, text="▶️ Continue", command=attempt_continue_game)
        continue_button.pack(fill='x', pady=5)
        ttk.Button(menu_frame, text="📂 Load Game", command=open_load_dialog).pack(fill='x', pady=5)
        ttk.Button(menu_frame, text="✨ Start New Game", command=show_new_game_setup).pack(fill='x', pady=5)
        quit_button = ttk.Button(menu_frame, text="❌ Quit", command=lambda: (logging.info("Quit selected from menu."), root.quit()))
        quit_button.pack(fill='x', pady=5)

        # Disable Continue button if no saves exist
        if GridGame.find_most_recent_save_slot() is None:
            continue_button.config(state=tk.DISABLED)

        # --- New Game Setup Screen (Function) ---
        def setup_new_game_screen(parent_window):
            parent_window.title("Grid Game - New Game")
            new_game_frame = ttk.Frame(parent_window, padding="20")
            new_game_frame.pack(fill='both', expand=True)

            ttk.Label(new_game_frame, text="Enter your name:").pack(pady=(0, 10))
            name_var = tk.StringVar(value="Player")
            name_entry = ttk.Entry(new_game_frame, textvariable=name_var)
            name_entry.pack(pady=(0, 20))

            # Difficulty Selection
            ttk.Label(new_game_frame, text="Select Difficulty:").pack(pady=(10, 5))
            difficulty_var = tk.StringVar(value="Medium") # Default to Medium
            difficulty_frame = ttk.Frame(new_game_frame)
            difficulty_frame.pack()

            difficulties = [("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")]
            for text, value in difficulties:
                ttk.Radiobutton(difficulty_frame, text=text, variable=difficulty_var, value=value).pack(side=tk.LEFT, padx=10)

            def start_new_game_action():
                try:
                    player_name = name_var.get()
                    if not player_name:
                        player_name = "Player" # Default if empty

                    selected_difficulty = difficulty_var.get()
                    logging.info(f"Starting new game. Name: '{player_name}', Difficulty: {selected_difficulty}.")
                    print(f"Starting new game with player name: {player_name}, Difficulty: {selected_difficulty}")

                    # Hide the setup screen
                    new_game_frame.destroy()

                    # Create NEW game instance
                    game_instance = GridGame() # Fresh instance
                    # game_instance.player.name = player_name # Set player name (now done in initialize_player)

                    # Initialize player based on difficulty
                    game_instance.initialize_player(player_name, selected_difficulty)

                    # Launch GUI
                    parent_window.title("Grid Game") # Reset title
                    launch_game_gui(parent_window, game_instance)

                except Exception as e:
                    logging.exception("Exception occurred while starting new game.") # Log exception info
                    show_error_and_exit("Error", "Failed to start new game", e)

            ttk.Button(new_game_frame, text="▶️ Start Game", command=start_new_game_action).pack()
            name_entry.focus_set()
            name_entry.bind('<Return>', lambda e: start_new_game_action())

        # --- Start Event Loop ---
        print("Showing main menu...")
        print("Starting main event loop...")
        root.mainloop()
        logging.info("--- Main event loop ended. Game closing. ---")
        print("Main event loop ended")

    except Exception as e:
        logging.exception("Critical error occurred in main function.") # Log critical exceptions
        show_error_and_exit("Critical Error", "A critical error occurred", e)


if __name__ == "__main__":
    main()
