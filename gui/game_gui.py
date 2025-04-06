import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import traceback
import logging # Import logging
from .windows.battle_window import BattleWindow
from .windows.item_window import ItemWindow
from .windows.portal_window import PortalWindow
from .windows.boss_battle_window import BossBattleWindow
from .windows.store_window import StoreWindow
from items.crop import Crop
from grid_game import GridGame, STORE_SYMBOL, PORTAL_SYMBOL
from datetime import datetime

# Helper function for centering windows (could be moved to a utils file)
def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

class GameGUI:
    def __init__(self, root, game_instance):
        """Initialize the game GUI"""
        self.root = root
        self.game = game_instance
        self.messages = []
        self.battle_in_progress = False
        self.current_battle_npc = None

        self.setup_window()
        self.create_styles()
        self.create_frames()
        self.create_grid()
        self.create_stats_panel()
        self.create_inventory_panel()
        self.create_controls()
        self.create_message_log()
        self.create_controls_panel()
        self.bind_keys()

        # Add welcome message
        self.add_message("Welcome to Grid Game! Use WASD to move.")

        # Initial updates
        self.update_grid()
        self.update_stats()
        logging.info("GameGUI initialized and initial elements updated.")

        # Add Save/Load buttons
        save_load_frame = ttk.Frame(self.game_frame)
        save_load_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        save_load_frame.grid_columnconfigure(0, weight=1)
        save_load_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(save_load_frame, text="💾 Save Game", command=self.open_save_dialog).grid(row=0, column=0, padx=5, sticky="ew")
        # No load button here anymore, loading happens from main menu
        # ttk.Button(save_load_frame, text="📂 Load Game", command=self.load_game).grid(row=0, column=1, padx=5, sticky="ew")

    def setup_window(self):
        """Set up the main window"""
        self.root.title("Grid Game")
        self.root.geometry("1200x900")  # Increased width from 1024 to 1200

        # Configure custom font for sprites
        # DejaVu Sans has good Unicode support
        self.sprite_font = ('DejaVu Sans', 14)

        def confirm_close():
            if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
                self.root.quit()

        self.root.protocol("WM_DELETE_WINDOW", confirm_close)

        # Configure root window to be resizable
        self.root.resizable(True, True)

        # Configure minimum window size
        self.root.minsize(1200, 900)  # Increased minimum width from 1024 to 1200

    def create_styles(self):
        """Configure ttk styles"""
        self.style = ttk.Style()
        self.style.configure("Grid.TButton", width=4, padding=4)
        self.style.configure(
            "Player.TButton", background='blue', foreground='white')
        self.style.configure("Portal.TButton", background='purple')
        self.style.configure("Enemy.TButton", background='red')
        self.style.configure("Store.TButton", background='green')
        self.style.configure("Crop.TButton", background='brown')

    def create_frames(self):
        """Create main frame layout"""
        # Main game area (left side)
        self.game_frame = ttk.Frame(self.root, padding="10")
        self.game_frame.grid(row=0, column=0, sticky="nsew")

        # Right panel for stats and inventory
        self.right_panel = ttk.Frame(self.root, padding="10")
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def create_grid(self):
        """Create the game grid display"""
        self.grid_frame = ttk.Frame(self.game_frame, padding="10")
        self.grid_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights
        for i in range(self.game.grid_height + 1):
            self.grid_frame.grid_columnconfigure(i, weight=1)
            self.grid_frame.grid_rowconfigure(i, weight=1)

        # Create column labels
        for j in range(self.game.grid_width):
            label = ttk.Label(self.grid_frame, text=str(j))
            label.grid(row=0, column=j+1, padx=2, pady=2)

        # Create grid buttons
        self.grid_buttons = []
        for i in range(self.game.grid_height):
            # Add row label
            label = ttk.Label(self.grid_frame, text=str(i))
            label.grid(row=i+1, column=0, padx=2, pady=2)

            row = []
            for j in range(self.game.grid_width):
                btn = ttk.Button(
                    self.grid_frame,
                    style="Grid.TButton",
                    width=4
                )
                btn.grid(row=i+1, column=j+1, padx=2, pady=2, sticky="nsew")
                row.append(btn)
            self.grid_buttons.append(row)

    def create_stats_panel(self):
        """Create the player stats panel"""
        stats_frame = ttk.LabelFrame(self.right_panel, text="Player Stats", padding="10")
        stats_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Configure grid weights for stats_frame
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)

        # Create a Text widget for stats display with scrollbar
        stats_container = ttk.Frame(stats_frame)
        stats_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure container weights
        stats_container.grid_columnconfigure(0, weight=1)
        stats_container.grid_rowconfigure(0, weight=1)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(stats_container)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Create text widget with scrollbar
        self.stats_text = tk.Text(
            stats_container,
            height=35,
            width=55,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        self.stats_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.stats_text.yview)

        # Configure tags for text styling
        self.stats_text.tag_configure("center", justify="center")
        self.stats_text.tag_configure("header", font=("TkDefaultFont", 12, "bold"))
        self.stats_text.tag_configure("level", font=("TkDefaultFont", 16, "bold"), foreground="blue")
        
        # Configure color tags for progress bars
        self.stats_text.tag_configure("exp_color", foreground="#FF69B4")  # Pink
        self.stats_text.tag_configure("health_color", foreground="#32CD32")  # Lime Green
        self.stats_text.tag_configure("energy_color", foreground="#1E90FF")  # Dodger Blue

        # Make the text widget read-only
        self.stats_text.configure(state="disabled")

    def create_inventory_panel(self):
        """Create the inventory panel"""
        inv_frame = ttk.LabelFrame(
            self.right_panel, text="🎒 Inventory", padding="10")
        inv_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Create a frame for the listbox and scrollbar
        list_frame = ttk.Frame(inv_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        # Create listbox with scrollbar
        self.inventory_listbox = tk.Listbox(
            list_frame,
            height=10,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=("TkDefaultFont", 10)
        )
        self.inventory_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.inventory_listbox.yview)

        # Create buttons frame
        button_frame = ttk.Frame(inv_frame)
        button_frame.pack(fill="x", padx=5, pady=(5, 0))

        # Add Use Item button
        ttk.Button(
            button_frame,
            text="📦 Use Item",
            command=self.use_item
        ).pack(fill="x", pady=2)

        # Initial inventory update
        self.update_inventory()

    def create_controls(self):
        """Create the control buttons"""
        controls_frame = ttk.LabelFrame(
            self.right_panel, text="🎮 Controls", padding="10")
        controls_frame.grid(row=2, column=0, sticky="ew")

        controls = [
            ("⬆️", "w", 0, 1),
            ("⬅️", "a", 1, 0),
            ("⬇️", "s", 1, 1),
            ("➡️", "d", 1, 2),
            ("📊", "i", 2, 0),
            ("📜", "h", 2, 1),
            ("❌", "q", 2, 2)
        ]

        for text, cmd, row, col in controls:
            ttk.Button(
                controls_frame,
                text=text,
                command=lambda c=cmd: self.handle_command(c)
            ).grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

    def create_message_log(self):
        """Create the message log"""
        log_frame = ttk.LabelFrame(
            self.game_frame, text="Message Log", padding="5")
        log_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        self.message_text = tk.Text(
            log_frame, height=6, wrap="word", state="disabled")
        self.message_text.pack(fill="x")

    def create_controls_panel(self):
        """Create the controls help panel"""
        controls_frame = ttk.LabelFrame(
            self.right_panel, text="Controls", padding="10")
        controls_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))

        # Create a Text widget for controls display
        self.controls_text = tk.Text(
            controls_frame, height=15, width=40, wrap=tk.WORD)
        self.controls_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Add controls information
        controls_info = (
            "Movement Controls:\n"
            "   W - Move Up\n"
            "   S - Move Down\n"
            "   A - Move Left\n"
            "   D - Move Right\n"
            "   1/2 - Move Up/Down Levels (at portal)\n\n"

            "Game Actions:\n"
            "   E - Open Inventory\n"
            "   H - View Battle History\n"
            "   G - View Game Statistics\n"
            "   V - Toggle Survival Mode\n"
            "   Q - Quit Game\n\n"

            "Farming Controls:\n"
            "   F - Plant Crop (on empty tile)\n"
            "   R - Harvest Crop (when ready)\n"
            "   T - Check Crop Status\n\n"

            "Combat:\n"
            "   Y - Accept Battle\n"
            "   N - Decline Battle\n"
            "   I - Use Item in Battle\n\n"

            "Portal Travel:\n"
            "   K + number - Quick Travel to Level\n"
            "   (e.g., K5 to travel to level 5)\n"
        )

        self.controls_text.insert('1.0', controls_info)
        self.controls_text.configure(state="disabled")

    def bind_keys(self):
        """Bind keyboard controls"""
        # Movement keys
        self.root.bind("<w>", lambda e: self.safe_handle_command("w"))
        self.root.bind("<a>", lambda e: self.safe_handle_command("a"))
        self.root.bind("<s>", lambda e: self.safe_handle_command("s"))
        self.root.bind("<d>", lambda e: self.safe_handle_command("d"))

        # Game action keys
        self.root.bind(
            "<e>", lambda e: self.safe_handle_command("e"))  # Inventory
        # Battle History
        self.root.bind("<h>", lambda e: self.safe_handle_command("h"))
        # Game Statistics
        self.root.bind("<g>", lambda e: self.safe_handle_command("g"))
        # Toggle Survival Mode
        self.root.bind("<v>", lambda e: self.safe_handle_command("v"))
        self.root.bind("<q>", lambda e: self.safe_handle_command("q"))  # Quit

        # Farming keys
        # Plant Crop
        self.root.bind("<f>", lambda e: self.safe_handle_command("f"))
        # Harvest Crop
        self.root.bind("<r>", lambda e: self.safe_handle_command("r"))
        # Check Crop Status
        self.root.bind("<t>", lambda e: self.safe_handle_command("t"))

        # Combat keys
        # Accept Battle
        self.root.bind("<y>", lambda e: self.safe_handle_command("y"))
        # Decline Battle
        self.root.bind("<n>", lambda e: self.safe_handle_command("n"))
        # Use Item in Battle
        self.root.bind("<i>", lambda e: self.safe_handle_command("i"))

    def safe_handle_command(self, cmd):
        """Safely handle a command, checking for battle state"""
        if self.battle_in_progress and cmd in ['w', 'a', 's', 'd']:
            # If in battle but window is closed, offer to reopen it
            if self.current_battle_npc:
                if messagebox.askyesno("Battle in Progress", "Would you like to reopen the battle window?"):
                    self.reopen_battle_window()
                return
            else:
                # If somehow battle_in_progress is True but no NPC, reset the state
                self.battle_in_progress = False
                self.current_battle_npc = None
        self.handle_command(cmd)

    def handle_command(self, cmd):
        """Handle game commands"""
        logging.info(f"Handling command: '{cmd}'") # Log command received
        try:
            if cmd in ["w", "a", "s", "d"]:
                self.move_player(cmd)
            elif cmd == "e":
                self.use_item()
            elif cmd == "h":
                self.show_history()
            elif cmd == "g":
                self.show_game_stats()
            elif cmd == "v":
                self.toggle_survival_mode()
            elif cmd == "f":
                self.show_crop_planting_dialog()
            elif cmd == "r":
                self.harvest_crop()
            elif cmd == "t":
                self.check_crop_status()
            elif cmd == "i":
                self.show_stats()
            elif cmd == "q":
                logging.info("Command 'q' received for quit confirmation.")
                if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
                    logging.info("Quit confirmed. Closing application.")
                    self.root.quit()
                else:
                    logging.info("Quit cancelled.")
            elif cmd == "1" or cmd == "2": # Add cases for portal movement
                # Command originates from handle_portal_action after button click in dialog.
                # No need to re-check position here, assume context is correct.
                logging.info(f"Portal action '{cmd}' received, calling handle_portal_movement.")
                self.handle_portal_movement(cmd)

        except Exception as e:
            logging.exception(f"Error handling command '{cmd}'.") # Log exceptions during command handling
            self.add_message(f"Error during command execution: {str(e)}")
            # traceback.print_exc() # Logging handles traceback now

    def move_player(self, direction):
        """Handle player movement"""
        logging.debug(f"Attempting move: {direction}")
        if self.battle_in_progress:
            logging.warning("Move attempt failed: Battle in progress.")
            self.add_message("Cannot move while in battle!")
            return

        # Check if player has enough energy
        if self.game.player.energy <= 0:
            self.add_message("Not enough energy to move!")
            return

        # Get the target position
        target_pos = self.game.get_target_position(direction)
        if not target_pos:
            self.add_message("Cannot move outside the grid!")
            return

        # Get current position before moving
        old_pos = self.game.player_pos.copy()

        # Check if moving onto a portal
        if target_pos == self.game.portal_pos:
            if self.game.player.energy >= 2:  # Portals cost 2 energy
                self.open_portal_dialog()
            else:
                self.add_message(
                    "Not enough energy to use portal! (Requires 2 energy)")
            return

        # Check if moving onto an NPC
        npc = None
        for npc_pos, n in self.game.npcs:
            if npc_pos == target_pos:
                npc = n
                break

        if npc:
            if self.game.player.energy >= 3:  # Battles cost 3 energy
                self.battle_in_progress = True
                self.current_battle_npc = npc  # Store the NPC
                self.open_battle_window()
            else:
                self.add_message("Not enough energy to battle! (Requires 3 energy)")
            return

        # Handle normal movement
        # Store old position
        old_level, old_row, old_col = old_pos

        # Update player position
        self.game.player_pos = target_pos
        new_level, new_row, new_col = target_pos

        # Update grid display
        if new_level != old_level:
            # Level change
            self.update_grid()
            self.add_message(f"Moved to level {new_level + 1}")
        else:
            # Same level movement
            # Check if there was a crop at the old position
            old_pos_tuple = tuple(old_pos)
            if old_pos_tuple in self.game.planted_crops:
                crops = self.game.planted_crops[old_pos_tuple]
                if isinstance(crops, list):
                    # For multiple crops, show the most grown one
                    most_grown = max(crops, key=lambda c: c.growth_progress)
                    symbol = most_grown.get_growth_stage()
                else:
                    symbol = crops.get_growth_stage()
                self.grid_buttons[old_row][old_col].configure(text=symbol)
            elif old_pos == self.game.portal_pos:
                self.grid_buttons[old_row][old_col].configure(text='🌀')
            else:
                self.grid_buttons[old_row][old_col].configure(text=' ')
            
            # Update new position with player symbol
            self.grid_buttons[new_row][new_col].configure(text='P')

            direction_text = {'w': 'up', 's': 'down',
                              'a': 'left', 'd': 'right'}
            self.add_message(
                f"Moved {direction_text[direction]} (Energy: {self.game.player.energy})")

        # Deduct energy and update stats
        self.game.player.energy -= 1
        self.update_stats()

        # Check for low energy
        if self.game.player.energy <= 2:
            if messagebox.askyesno("Low Energy",
                                   "Your energy is running low! Would you like to buy more energy for 10 credits?"):
                if self.game.player.credits >= 10:
                    self.game.player.credits -= 10
                    self.game.player.energy = self.game.player.max_energy
                    self.add_message("Bought more energy!")
                    self.update_stats()
                else:
                    self.add_message("Not enough credits to buy energy!")

        # After move logic, check for triggering other actions
        self.handle_player_move(self.game.player_pos)

    def handle_portal_movement(self, action):
        """Handle portal movement after portal window closes"""
        try:
            level = self.game.player_pos[0]
            if action == "1":  # Down
                self.game.player_pos[0] = level - 1
            else:  # Up
                self.game.player_pos[0] = level + 1

            # Generate new portal position
            self.game.portal_pos = [
                self.game.player_pos[0],
                random.randint(0, self.game.grid_height - 1),
                random.randint(0, self.game.grid_width - 1)
            ]

            # Generate new NPCs
            level = self.game.player_pos[0]
            num_npcs = random.randint(2, 4)
            self.game.npcs = []

            from entities.npc import NPC
            for i in range(num_npcs):
                while True:
                    npc_row = random.randint(0, self.game.grid_height - 1)
                    npc_col = random.randint(0, self.game.grid_width - 1)
                    pos = [level, npc_row, npc_col]

                    if (pos != self.game.player_pos and
                        pos != self.game.portal_pos and
                            not any(pos == npc_pos for npc_pos, _ in self.game.npcs)):
                        npc = NPC.generate_random(level)
                        self.game.npcs.append((pos, npc))
                        logging.debug(f"Generated NPC {i+1}/{num_npcs} ('{npc.symbol}') at {pos}") # Log NPC generation
                        break # Found a valid spot for this NPC

            # --- Populate the game grid for the new level --- #
            logging.debug(f"Calling populate_grid_for_level for level {level}")
            self.game.populate_grid_for_level(level)
            # ------------------------------------------------ #

            # Update GUI elements based on the now-populated grid
            self.update_grid()
            self.update_stats()
            self.update_inventory()
            self.add_message(
                f"Used portal to move to level {self.game.player_pos[0] + 1}")

        except Exception as e:
            self.add_message(f"Error during portal movement: {str(e)}")
            traceback.print_exc()

    def open_battle_window(self):
        """Open the battle window with current NPC"""
        battle_window = BattleWindow(self.root, self.game, self.current_battle_npc, self.handle_battle_end)
        
        # Store the battle window reference
        self.current_battle_window = battle_window
        
        # Bind window close event to the window attribute
        battle_window.window.protocol("WM_DELETE_WINDOW", lambda: self.handle_battle_window_close(battle_window))
        
    def reopen_battle_window(self):
        """Reopen the battle window if a battle is in progress"""
        if self.battle_in_progress and self.current_battle_npc:
            self.open_battle_window()
            
    def handle_battle_window_close(self, battle_window):
        """Handle battle window being closed"""
        # Only show confirmation if battle is still in progress
        if self.battle_in_progress:
            if messagebox.askyesno("Close Battle", "Are you sure you want to close the battle window? You can reopen it by trying to move."):
                battle_window.destroy()
        else:
            # If battle is over, just close the window
            battle_window.destroy()
        
    def handle_battle_end(self, result):
        """Handle end of battle"""
        self.battle_in_progress = False
        self.current_battle_npc = None  # Clear the stored NPC
        
        if result is True:  # Victory
            self.add_message("Battle won!")
        elif result is False:  # Defeat
            self.add_message("Battle lost!")
        else:  # Run away
            self.add_message("Ran away from battle!")
            
        self.update_stats()
        self.update_inventory()
        self.update_grid()
        
        # Start countdown to auto-close the window
        if hasattr(self, 'current_battle_window'):
            countdown_seconds = 7
            self.start_battle_window_countdown(self.current_battle_window, countdown_seconds)
            
    def start_battle_window_countdown(self, battle_window, seconds):
        """Start a countdown to automatically close the battle window"""
        if seconds > 0 and battle_window.window.winfo_exists():
            # Update window title with countdown
            battle_window.window.title(f"Battle Complete - Closing in {seconds}s")
            # Schedule next countdown update
            self.root.after(1000, lambda: self.start_battle_window_countdown(battle_window, seconds - 1))
        elif battle_window.window.winfo_exists():
            # When countdown reaches 0, close the window
            battle_window.destroy()
            if hasattr(self, 'current_battle_window'):
                delattr(self, 'current_battle_window')

    def update_grid(self):
        """Update the grid display based on game state"""
        current_level = self.game.player_pos[0]
        grid_height = self.game.grid_height
        grid_width = self.game.grid_width

        # More efficient grid update:
        for r in range(grid_height):
            for c in range(grid_width):
                char = self.game.grid[current_level][r][c]
                btn = self.grid_buttons[r][c]

                # Check if button text needs updating (Font logic removed)
                if btn.cget('text') != char:
                    btn.configure(text=char)

                # Apply styling based on character
                style = "Grid.TButton" # Default
                if char == self.game.player.symbol:
                    style = "Player.TButton"
                elif char == PORTAL_SYMBOL:
                    style = "Portal.TButton"
                elif char == STORE_SYMBOL:
                     style = "Store.TButton"
                elif char in ['G', 'O', 'T', 'W', 'D', 'S']: # Example enemy symbols
                     style = "Enemy.TButton"
                elif char in ['🌱', '🌿', '🌾']:
                     style = "Crop.TButton"

                # Check if style needs updating
                if btn.cget('style') != style:
                    btn.configure(style=style)

    def update_stats(self):
        """Update the player stats display panel"""
        p = self.game.player
        self.stats_text.configure(state="normal")
        self.stats_text.delete(1.0, tk.END)

        # Header
        self.stats_text.insert(tk.END, f"--- {p.name} ---\n", ("header", "center"))
        self.stats_text.insert(tk.END, f"Level {p.level}\n", ("level", "center"))

        # HP/Energy Bars
        hp_percent = (p.health / p.max_health) * 100 if p.max_health > 0 else 0
        energy_percent = (p.energy / p.max_energy) * 100 if p.max_energy > 0 else 0
        self.stats_text.insert(tk.END, f"\nHP: {p.health}/{p.max_health}\n")
        self.stats_text.insert(tk.END, self._create_progress_bar(hp_percent, 20, '#'), ("health_color",))
        self.stats_text.insert(tk.END, f"\nEnergy: {p.energy}/{p.max_energy}\n")
        self.stats_text.insert(tk.END, self._create_progress_bar(energy_percent, 20, '='), ("energy_color",))

        # Experience Bar
        exp_percent = (p.experience / p.experience_to_next_level) * 100 if p.experience_to_next_level > 0 else 0
        self.stats_text.insert(tk.END, f"\nEXP: {p.experience}/{p.experience_to_next_level}\n")
        self.stats_text.insert(tk.END, self._create_progress_bar(exp_percent, 20, '*'), ("exp_color",))

        # Core Stats
        self.stats_text.insert(tk.END, f"\n\nAttributes:\n")
        self.stats_text.insert(tk.END, f"  Attack: {p.get_total_attack()}\n")
        self.stats_text.insert(tk.END, f"  Defense: {p.defense}\n")
        self.stats_text.insert(tk.END, f"  Agility: {p.agility}\n")

        # Other Info
        self.stats_text.insert(tk.END, f"\nCredits: {p.credits} G\n")
        # Display current weapon if equipped
        weapon_name = p.weapon.name if p.weapon else "None"
        self.stats_text.insert(tk.END, f"Weapon: {weapon_name}\n")
        # Display level keys
        keys_str = ', '.join(map(str, sorted(p.level_keys))) if p.level_keys else "None"
        self.stats_text.insert(tk.END, f"Portal Keys: {keys_str}\n")

        # Time and Weather
        self.stats_text.insert(tk.END, f"\nTime: {self.game.time_system.current_time.strftime('%I:%M %p')}\n")
        self.stats_text.insert(tk.END, f"Weather: {self.game.weather.get_weather_symbol()} {self.game.weather.get_weather_description()}\n")

        self.stats_text.configure(state="disabled")

    def _create_progress_bar(self, percent, length=20, char='#'):
        filled_length = int(length * (percent / 100))
        return char * filled_length + '-' * (length - filled_length)

    def update_inventory(self):
        """Update the inventory display"""
        self.inventory_listbox.delete(0, tk.END)

        if not self.game.player.inventory:
            self.inventory_listbox.insert(tk.END, "(Empty)")
            return

        for item in self.game.player.inventory:
            # Format item with emoji based on type
            if "Potion" in item.name:
                emoji = "🧪"
            elif "Phoenix" in item.name:
                emoji = "🔥"
            elif "Note" in item.name:
                emoji = "📝"
            elif "Sword" in item.name or "Blade" in item.name:
                emoji = "⚔️"
            elif "Shield" in item.name:
                emoji = "🛡️"
            else:
                emoji = "📦"

            self.inventory_listbox.insert(tk.END, f"{emoji} {item.name}")

    def use_item(self):
        """Handle item usage"""
        # Create a callback that will update both the message log and the inventory display
        def update_after_use(message):
            self.add_message(message)
            self.update_inventory()  # Update the inventory display
            self.update_stats()      # Update player stats display
        
        # Open the item window with the update callback
        ItemWindow(self.root, self.game, update_after_use)

    def add_message(self, message):
        """Add a message to the message log"""
        self.messages.append(message)
        if len(self.messages) > 100:
            self.messages.pop(0)

        self.message_text.configure(state="normal")
        self.message_text.delete(1.0, tk.END)
        for msg in self.messages[-6:]:
            self.message_text.insert(tk.END, msg + "\n")
        self.message_text.configure(state="disabled")

    def show_stats(self):
        """Show detailed player stats"""
        player = self.game.player
        stats_text = f"""Player Stats:
👑 Character Level: {player.level}
📊 Experience: {player.experience}/{player.experience_to_next_level}
❤️ Health: {player.health}/{player.max_health}
⚔️ Attack: {player.get_total_attack()} (Base: {player.attack})
🛡️ Defense: {player.defense}
💨 Agility: {player.agility}
⚡ Energy: {player.energy}/{player.max_energy}
💰 Credits: {player.credits}
🗺️ Current Floor: {self.game.player_pos[0] + 1}

🎒 Inventory:
"""
        if player.inventory:
            for item in player.inventory:
                stats_text += f"  • {item.name}\n"
        else:
            stats_text += "  (Empty)\n"

        if player.weapon:
            stats_text += f"\n⚔️ Weapon: {player.weapon.name} (+{player.weapon.attack} ATK)"

        messagebox.showinfo("Player Stats", stats_text)

    def show_history(self):
        """Show battle history"""
        if not self.game.battle_history:
            messagebox.showinfo("Battle History", "No battles yet!")
            return

        history_text = "Battle History:\n\n"
        for i, battle in enumerate(reversed(self.game.battle_history), 1):
            if battle.get("is_portal_boss", False):
                history_text += f"⚠️ Portal Boss Battle #{i}\n"
                history_text += f"📍 Level {battle['level']}: {battle['player_name']} vs Portal Guardians\n"
                history_text += f"👑 Bosses Defeated: {battle['bosses_defeated']}/2\n"
            else:
                history_text += f"Battle #{i}\n"
                history_text += f"📍 Level {battle['level']}: {battle['player_name']} vs {battle['npc_name']}\n"
                history_text += f"🎯 Result: {battle['result']} in {battle['turns']} turns\n"

            if battle['credits_gained'] > 0:
                history_text += f"💰 Credits gained: {battle['credits_gained']}\n"
            if battle['items_found']:
                history_text += f"🎁 Items found: {', '.join(battle['items_found'])}\n"
            history_text += "-" * 40 + "\n"

        messagebox.showinfo("Battle History", history_text)

    def toggle_survival_mode(self):
        """Toggle survival mode on/off"""
        if not self.game.is_survival_mode:
            if self.game.start_survival_mode():
                self.add_message(
                    "🌊 Survival Mode activated! Prepare for waves of enemies!")
                self.add_message(
                    f"Wave {self.game.survival_wave} starting with {self.game.enemies_remaining} enemies.")
            else:
                self.add_message(
                    "❌ Cannot start Survival Mode here. Move to an empty area first.")
        else:
            self.game.end_survival_mode()
            self.add_message("🔄 Survival Mode deactivated.")
        self.update_all()

    def show_crop_planting_dialog(self):
        """Show dialog for planting crops"""
        logging.info("Opening crop planting dialog.") # Log dialog opening
        if self.game.is_survival_mode:
            self.add_message("❌ Cannot plant crops during Survival Mode!")
            return

        # Create crop planting dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Plant Crop")
        dialog.geometry("500x600")  # Increased width and height

        # Create main frame with padding
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Center the dialog
        dialog.geometry(
            f"+{self.root.winfo_x() + 50}+{self.root.winfo_y() + 50}")

        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()

        # Add crop options
        ttk.Label(
            main_frame,
            text="Select crop to plant:",
            font=("TkDefaultFont", 12, "bold")
        ).pack(pady=(0, 20))

        # Show credits
        ttk.Label(
            main_frame,
            text=f"💰 Credits: {self.game.player.credits}",
            foreground="green",
            font=("TkDefaultFont", 11)
        ).pack(pady=(0, 10))

        # Show farming level
        ttk.Label(
            main_frame,
            text=f"🌾 Farming Level: {self.game.farming_stats['farming_level']} "
            f"(Exp: {self.game.farming_stats['farming_exp']}/{self.game.farming_stats['farming_exp_to_next']})",
            foreground="blue",
            font=("TkDefaultFont", 11)
        ).pack(pady=(0, 20))

        crop_var = tk.StringVar()
        crop_types = {
            crop["name"]: {"growth_time": crop["growth_time"],
                           "value": crop["value"]}
            for crop in Crop.get_available_crops()
        }

        # Add information about multi-planting
        multi_plant_level = self.game.get_farming_level_requirement(
            "multi_planting")
        if self.game.farming_stats["farming_level"] >= multi_plant_level:
            ttk.Label(
                main_frame,
                text="✨ Advanced Farming: Can plant up to 2 crops per tile",
                foreground="green",
                font=("TkDefaultFont", 11)
            ).pack(pady=(0, 20))
        else:
            ttk.Label(
                main_frame,
                text=f"🔒 Multi-planting unlocks at farming level {multi_plant_level}",
                foreground="gray",
                font=("TkDefaultFont", 11)
            ).pack(pady=(0, 20))

        # Create a frame for crop options with more padding
        crops_frame = ttk.Frame(main_frame)
        crops_frame.pack(fill="x", padx=20, pady=10)

        for crop_name, info in crop_types.items():
            seed_cost = info["value"] // 2
            crop_frame = ttk.Frame(crops_frame)
            crop_frame.pack(fill="x", pady=5)

            ttk.Radiobutton(
                crop_frame,
                text=f"{crop_name}",
                value=crop_name,
                variable=crop_var
            ).pack(side="left", padx=(0, 10))

            ttk.Label(
                crop_frame,
                text=f"Growth: {info['growth_time']}h | Value: {info['value']} credits | Seed: {seed_cost} credits",
                font=("TkDefaultFont", 10)
            ).pack(side="left")

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))

        def plant_selected_crop():
            crop_name = crop_var.get()
            if crop_name:
                info = crop_types[crop_name]
                crop = Crop(crop_name, info["growth_time"], info["value"])
                pos_tuple = tuple(self.game.player_pos)
                logging.info(f"Attempting to plant '{crop_name}' at {pos_tuple}.") # Log plant attempt

                success, message = self.game.plant_crop(
                    crop, self.game.player_pos)
                if success:
                    logging.info(f"Successfully planted '{crop_name}' at {pos_tuple}. Message: {message}") # Log success
                    self.add_message(f"🌱 {message}")
                    # Update the specific grid cell immediately
                    row, col = self.game.player_pos[1], self.game.player_pos[2]
                    self.grid_buttons[row][col].configure(text='🌱')
                    self.grid_buttons[row][col].update()
                    # Update other UI elements
                    self.update_stats()
                    self.root.update_idletasks()
                else:
                    logging.warning(f"Failed to plant '{crop_name}' at {pos_tuple}. Reason: {message}") # Log failure
                    self.add_message(f"❌ {message}")
            else:
                logging.warning("Planting cancelled: No crop selected.") # Log cancellation
            dialog.destroy()

        ttk.Button(
            button_frame,
            text="Plant",
            command=plant_selected_crop,
            style="Accent.TButton"
        ).pack(side="left", padx=5, expand=True)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="left", padx=5, expand=True)

    def harvest_crop(self):
        """Harvest crop at current position"""
        pos = tuple(self.game.player_pos)
        logging.info(f"Attempting harvest at {pos}.") # Log harvest attempt
        if pos in self.game.planted_crops:
            crops = self.game.planted_crops[pos]
            if isinstance(crops, list):
                ready = any(crop.growth_progress >= 1.0 for crop in crops)
            else:
                ready = crops.growth_progress >= 1.0

            if ready:
                value, names, level_up_message = self.game.harvest_crop(pos)
                if value:
                    crop_names_str = " + ".join(names)
                    logging.info(f"Harvest successful at {pos}: Harvested {crop_names_str} for {value} credits.") # Log success
                    self.add_message(
                        f"🌾 Harvested {crop_names_str} for {value} credits!")
                    if level_up_message:
                        logging.info(f"Farming level up: {level_up_message}") # Log level up
                        self.add_message(level_up_message)
                else:
                    # This case might mean harvest called but nothing was actually ready/returned value?
                    logging.warning(f"Harvest at {pos} attempted but returned no value (possibly already harvested or error).")
            else:
                if isinstance(crops, list):
                    progress = [int(crop.growth_progress * 100)
                                for crop in crops]
                    logging.info(f"Harvest failed at {pos}: Crops not ready (Progress: {min(progress)}% - {max(progress)}%).") # Log not ready (multi)
                    self.add_message(
                        f"🌱 Crops are only {min(progress)}% - {max(progress)}% grown.")
                else:
                    progress = int(crops.growth_progress * 100)
                    logging.info(f"Harvest failed at {pos}: Crop '{crops.name}' not ready (Progress: {progress}%)." ) # Log not ready (single)
                    self.add_message(f"🌱 Crop is only {progress}% grown.")
        else:
            logging.info(f"Harvest failed at {pos}: No crop present.") # Log no crop
            self.add_message("❌ No crop to harvest here!")

    def check_crop_status(self):
        """Check status of current and nearby crops"""
        current_pos_list = self.game.player_pos
        current_pos_tuple = tuple(current_pos_list)
        logging.info(f"Checking crop status around {current_pos_tuple}.") # Log check start

        # First check current position
        # current_pos = self.game.player_pos # Already have list form
        current_info = self.game.get_crop_info(current_pos_list)
        if current_info:
            logging.debug(f"Crop status at current tile {current_pos_tuple}: {current_info}") # Log current tile info
            self.add_message(f"🌱 Current tile: {current_info}")

        # Then check adjacent tiles
        crops_found = False
        level = current_pos_list[0]
        row = current_pos_list[1]
        col = current_pos_list[2]

        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip current position as it was checked above

                new_row = row + dy
                new_col = col + dx
                if (0 <= new_row < self.game.grid_height and
                        0 <= new_col < self.game.grid_width):
                    pos_list = [level, new_row, new_col]
                    pos_tuple = tuple(pos_list)
                    info = self.game.get_crop_info(pos_list)
                    if info:
                        crops_found = True
                        logging.debug(f"Crop status at adjacent tile {pos_tuple}: {info}") # Log adjacent tile info
                        self.add_message(f"🌱 At ({new_row},{new_col}): {info}")

        if not crops_found and not current_info:
            logging.info("Crop status check found no crops at current or adjacent tiles.") # Log no crops found
            self.add_message("❌ No crops found in current or adjacent tiles!")

    def update_all(self):
        """Update all GUI elements"""
        self.update_grid()
        self.update_stats()
        self.update_inventory()

    def show_portal_menu(self):
        """Show the portal interaction menu"""
        # Add logging here to confirm it's called
        logging.info(f"ENTERING show_portal_menu. Player at {self.game.player_pos}, Portal at {self.game.portal_pos}")

        portal_window = tk.Toplevel(self.root)
        portal_window.title("Portal")
        portal_window.geometry("400x300")

        # Make dialog modal
        portal_window.transient(self.root)
        portal_window.grab_set()

        # Center the window
        portal_window.geometry(
            f"+{self.root.winfo_x() + 200}+{self.root.winfo_y() + 200}")

        # Create main frame with padding
        main_frame = ttk.Frame(portal_window, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Portal info
        ttk.Label(
            main_frame,
            text="🌀 You've encountered a portal!",
            font=("TkDefaultFont", 12, "bold")
        ).pack(pady=(0, 20))

        # Show current level
        ttk.Label(
            main_frame,
            text=f"Current Level: {self.game.player_pos[0] + 1}",
            font=("TkDefaultFont", 11)
        ).pack(pady=(0, 20))

        # Portal options
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        # Down button (if not at lowest level)
        if self.game.player_pos[0] > 0:
            ttk.Button(
                button_frame,
                text="🔽 Go Down (1)",
                command=lambda: self.handle_portal_action("1", portal_window)
            ).pack(fill="x", pady=5)

        # Up button (if not at highest level)
        if self.game.player_pos[0] < self.game.max_level:
            ttk.Button(
                button_frame,
                text="🔼 Go Up (2)",
                command=lambda: self.handle_portal_action("2", portal_window)
            ).pack(fill="x", pady=5)

        # Cancel button
        ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=portal_window.destroy
        ).pack(fill="x", pady=5)

    def handle_portal_action(self, action, window):
        """Handle portal movement and close the portal window"""
        window.destroy()
        self.handle_command(action) # Process action like a key command

    def open_portal_dialog(self):
        """Show the portal interaction menu"""
        logging.info(f"ENTERING open_portal_dialog. Player at {self.game.player_pos}, Portal at {self.game.portal_pos}") # Log entry

        portal_window = tk.Toplevel(self.root)
        portal_window.title("Portal")
        portal_window.geometry("400x300")

        # Make dialog modal
        portal_window.transient(self.root)
        portal_window.grab_set()

        # Center the window
        portal_window.geometry(
            f"+{self.root.winfo_x() + 200}+{self.root.winfo_y() + 200}")

        # Create main frame with padding
        main_frame = ttk.Frame(portal_window, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Portal info
        ttk.Label(
            main_frame,
            text="🌀 You've encountered a portal!",
            font=("TkDefaultFont", 12, "bold")
        ).pack(pady=(0, 20))

        # Show current level
        ttk.Label(
            main_frame,
            text=f"Current Level: {self.game.player_pos[0] + 1}",
            font=("TkDefaultFont", 11)
        ).pack(pady=(0, 20))

        # Portal options
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        # Down button (if not at lowest level)
        if self.game.player_pos[0] > 0:
            ttk.Button(
                button_frame,
                text="🔽 Go Down (1)",
                command=lambda: self.handle_portal_action("1", portal_window)
            ).pack(fill="x", pady=5)

        # Up button (if not at highest level)
        if self.game.player_pos[0] < self.game.max_level:
            ttk.Button(
                button_frame,
                text="🔼 Go Up (2)",
                command=lambda: self.handle_portal_action("2", portal_window)
            ).pack(fill="x", pady=5)

        # Cancel button
        ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=portal_window.destroy
        ).pack(fill="x", pady=5)

    # --- Save/Load Dialogs and Actions ---

    def _format_metadata_for_display(self, metadata: dict) -> str:
        """Format save metadata into a readable string for list display."""
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

    def open_save_dialog(self):
        """Opens a dialog window to select a save slot."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Game Slot")
        dialog.geometry("450x300")
        dialog.transient(self.root) # Keep on top of main window
        dialog.grab_set() # Modal behavior
        center_window(dialog, 450, 300)
        dialog.focus_set()

        ttk.Label(dialog, text="Select a slot to save:").pack(pady=10)

        # Listbox to show slots
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate listbox with slot info
        all_metadata = GridGame.get_all_save_metadata()
        slot_data_map = {}
        for i, metadata in enumerate(all_metadata):
            slot = i + 1
            display_text = self._format_metadata_for_display(metadata)
            listbox.insert(tk.END, display_text)
            slot_data_map[i] = slot # Map listbox index to slot number
            if metadata: # Highlight existing saves?
                listbox.itemconfig(i, {'fg': 'navy'})
            else:
                listbox.itemconfig(i, {'fg': 'gray'})

        def perform_save():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select a slot.", parent=dialog)
                return

            selected_index = selected_indices[0]
            slot_to_save = slot_data_map[selected_index]
            existing_metadata = all_metadata[selected_index]

            confirm = True
            if existing_metadata:
                confirm = messagebox.askyesno("Overwrite Save?",
                                              f"Slot {slot_to_save} already contains a save. Overwrite?",
                                              parent=dialog)
            if confirm:
                logging.info(f"Attempting to save game to slot {slot_to_save}.")
                if self.game.save_game(slot_to_save):
                    logging.info(f"Game successfully saved to slot {slot_to_save}.")
                    self.add_message(f"Game saved to Slot {slot_to_save}.")
                    dialog.destroy()
                else:
                    logging.error(f"Failed to save game to slot {slot_to_save}.")
                    self.add_message(f"Failed to save game to Slot {slot_to_save}.")
                    messagebox.showerror("Save Error", "Could not save the game. Check console for details.", parent=dialog)
            else:
                logging.info(f"Save to slot {slot_to_save} cancelled by user.")

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        ttk.Button(button_frame, text="Save", command=perform_save).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

    def handle_player_move(self, new_pos):
        """Handle actions triggered after player moves to a new position."""
        level, row, col = new_pos
        logging.debug(f"Player moved to [{level}, {row}, {col}]. Checking for encounters.")

        # --- Add detailed logging for portal check ---
        logging.debug(f"Checking portal: Player pos = {new_pos}, Portal pos = {self.game.portal_pos}")
        # Check for Portal encounter
        if new_pos == self.game.portal_pos:
            logging.info("Player position MATCHES portal position. Calling open_portal_dialog.") # Log match
            self.open_portal_dialog()
            return # Stop further checks
        # ---------------------------------------------

        # Check for Store encounter
        if any(store_pos == new_pos for store_pos in self.game.store_pos):
             logging.info(f"Entered Store at [{level}, {row}, {col}]. Opening store dialog.")
             self.open_store_dialog()
             return # Stop further checks

        # Check for harvestable crops (if not battling or portaling)
        self.check_and_prompt_harvest(level, row, col)

    def check_and_prompt_harvest(self, level, row, col):
        """Check if there's a harvestable crop and prompt the player."""
        pos_tuple = (level, row, col)
        if pos_tuple in self.game.planted_crops:
            crops = self.game.planted_crops[pos_tuple]
            is_ready = False
            crop_names = []

            if isinstance(crops, list): # Check for multi-crop tile
                ready_crops = [c for c in crops if c.growth_progress >= 1.0]
                if ready_crops:
                    is_ready = True
                    crop_names = [c.name for c in ready_crops]
            elif isinstance(crops, Crop): # Single crop
                if crops.growth_progress >= 1.0:
                    is_ready = True
                    crop_names = [crops.name]

            if is_ready:
                names_str = " and ".join(crop_names)
                if messagebox.askyesno("Harvest Ready", f"🌱 {names_str} is ready to harvest!\nDo you want to harvest it now? (Uses 'R' key)"):
                    self.handle_command("r") # Trigger harvest action

    def open_store_dialog(self):
        """Opens the store window."""
        if hasattr(self, 'current_store_window') and self.current_store_window.window.winfo_exists():
            self.current_store_window.window.focus_set()
            return # Don't open multiple store windows

        # Pass self (GameGUI instance) to StoreWindow if needed for callbacks
        self.current_store_window = StoreWindow(self.root, self.game)
        # Example of making it wait:
        # self.root.wait_window(self.current_store_window.window)
        # Update after closing:
        logging.debug("Store dialog closed. Updating stats and inventory.")
        self.update_stats()
        self.update_inventory()

    def start_battle(self, npc):
        """Starts a battle with the given NPC"""
        # ... existing code ...
        return row_cells

        grid_display = [generate_row(r) for r in range(grid_height)]

        # Update buttons based on grid_display
        for r in range(grid_height):
            for c in range(grid_width):
                char = grid_display[r][c]
                btn = self.grid_buttons[r][c]
                btn.configure(text=char)

                # Apply styling based on character
                style = "Grid.TButton" # Default
                if char == self.game.player.symbol:
                    style = "Player.TButton"
                elif char == '@':
                    style = "Portal.TButton"
                elif char == STORE_SYMBOL:
                     style = "Store.TButton" # Add style for store
                elif char in ['G', 'O', 'T', 'W', 'D', 'S']: # Example enemy symbols
                     style = "Enemy.TButton"
                elif char in ['🌱', '🌿', '🌾']: # Crop symbols
                     style = "Crop.TButton"

                btn.configure(style=style)
