import tkinter as tk
from tkinter import ttk, messagebox
from .base_window import BaseWindow
import random # Import random for respawn location
import logging # Import logging


class BattleWindow(BaseWindow):
    def __init__(self, parent, game_instance, npc, on_battle_end):
        """Initialize battle window"""
        super().__init__(parent, "Battle", "800x800")  # Increased window size
        logging.info(f"Battle started. Player: '{game_instance.player.name}' vs NPC: '{npc.name}' (Level {npc.level})")
        self.game = game_instance
        self.npc = npc
        self.on_battle_end = on_battle_end
        self.turn = 1

        # Create main container
        self.main_container = ttk.Frame(self.window)
        self.main_container.pack(fill='both', expand=True)

        # Create content frame directly (no canvas needed since we don't need scrolling)
        self.main_frame = ttk.Frame(self.main_container)
        self.main_frame.pack(fill='both', expand=True)

        # Battle info
        self.create_info_frame()
        self.create_battle_log()
        self.create_action_buttons()

        # Create bottom frame for continue button (always visible)
        self.bottom_frame = ttk.Frame(self.window)
        self.bottom_frame.pack(side='bottom', fill='x', padx=10, pady=5)

        # Initial battle message
        self.update_battle_log(
            f"Battle between {self.game.player.name} and {self.npc.name} ({self.npc.symbol})!")
        stats_message = (
            f"{self.game.player.name} Stats: HP: {self.game.player.health}/{self.game.player.max_health}, "
            f"ATK: {self.game.player.get_total_attack()}, DEF: {self.game.player.defense}, "
            f"AGI: {self.game.player.agility}"
        )
        self.update_battle_log(stats_message)

        self.center_window()

    def create_info_frame(self):
        """Create the battle information frame"""
        info_frame = ttk.LabelFrame(
            self.main_frame, text="Battle Info", padding="5")  # Reduced padding
        info_frame.pack(fill='x', padx=5, pady=2)  # Reduced margins

        # Player info
        player_frame = ttk.Frame(info_frame)
        player_frame.pack(fill='x', pady=2)  # Reduced spacing

        ttk.Label(player_frame, text=f"Player: {self.game.player.name}", font=(
            'Arial', 11)).pack(side='left')
        self.player_hp_label = ttk.Label(
            player_frame,
            text=f"HP: {self.game.player.health}/{self.game.player.max_health}",
            font=('Arial', 11)
        )
        self.player_hp_label.pack(side='right')

        # NPC info
        npc_frame = ttk.Frame(info_frame)
        npc_frame.pack(fill='x', pady=2)  # Reduced spacing

        ttk.Label(npc_frame, text=f"Enemy: {self.npc.name} ({self.npc.symbol})", font=(
            'Arial', 11)).pack(side='left')
        self.npc_hp_label = ttk.Label(
            npc_frame,
            text=f"HP: {self.npc.health}/{self.npc.max_health}",
            font=('Arial', 11)
        )
        self.npc_hp_label.pack(side='right')

    def create_battle_log(self):
        """Create the battle log"""
        log_frame = ttk.LabelFrame(
            self.main_frame, text="Battle Log", padding="5")  # Reduced padding
        log_frame.pack(fill='both', expand=True, padx=5,
                       pady=2)  # Reduced margins

        # Create Text widget with scrollbar
        self.battle_log = tk.Text(log_frame, height=25, wrap='word', font=(
            'Arial', 11))  # Increased height
        scrollbar = ttk.Scrollbar(
            log_frame, orient='vertical', command=self.battle_log.yview)
        self.battle_log.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.battle_log.pack(fill='both', expand=True)

        # Make read-only
        self.battle_log.configure(state='disabled')

    def show_battle_result(self, result):
        """Show battle result and cleanup"""
        # Disable action buttons
        self.disable_action_buttons()

        # Create continue button in the bottom frame
        ttk.Button(
            self.bottom_frame,
            text="Continue",
            command=lambda: self.handle_battle_end(result)
        ).pack(fill='x', padx=10, pady=5)

    def update_battle_log(self, message):
        """Update the battle log with a new message"""
        self.battle_log.configure(state='normal')
        self.battle_log.insert('end', message + '\n')
        self.battle_log.see('end')
        self.battle_log.configure(state='disabled')

    def update_stats_display(self):
        """Update the HP displays"""
        self.player_hp_label.configure(
            text=f"HP: {self.game.player.health}/{self.game.player.max_health}"
        )
        self.npc_hp_label.configure(
            text=f"HP: {self.npc.health}/{self.npc.max_health}"
        )

    def handle_attack(self):
        """Handle attack action"""
        # Disable action buttons during attack sequence
        self.disable_action_buttons()

        # Log turn number
        self.update_battle_log(f"\nTurn {self.turn}")

        # Log initial stats
        self.update_battle_log(
            f"\nInitial Stats:"
            f"\n{self.game.player.name}: HP {self.game.player.health}/{self.game.player.max_health}, "
            f"ATK {self.game.player.get_total_attack()}, DEF {self.game.player.defense}, AGI {self.game.player.agility}"
            f"\n{self.npc.name}: HP {self.npc.health}/{self.npc.max_health}, "
            f"ATK {self.npc.get_total_attack()}, DEF {self.npc.defense}, AGI {self.npc.agility}"
        )

        # Determine who goes first based on agility
        if self.game.player.agility >= self.npc.agility:
            self.update_battle_log(
                f"\n{self.game.player.name} acts first (AGI: {self.game.player.agility} >= {self.npc.agility})")
            # Player attacks first
            damage = self.game.player.attack_character(self.npc)
            self.update_battle_log(
                f"{self.game.player.name} attacks {self.npc.name} for {damage} damage! "
                f"{self.npc.name} has {self.npc.health}/{self.npc.max_health} HP remaining"
            )
            self.update_stats_display()

            if not self.npc.is_alive():
                self.update_battle_log(f"\n{self.npc.name} has been defeated!")

                # Give all rewards immediately
                exp_gain = self.npc.get_experience_value()
                credits_gain = self.npc.get_credit_value()
                old_level = self.game.player.level

                # Add experience and check for level up
                self.game.player.add_experience(exp_gain)
                self.game.player.credits += credits_gain
                # --- ADDED DEBUG LOG ---
                logging.debug(f"[BattleWindow] Credits Awarded: {credits_gain}. Player credits NOW: {self.game.player.credits}")
                # ---------------------

                # Show rewards in battle log
                self.update_battle_log(f"Gained {exp_gain} experience!")
                self.update_battle_log(
                    f"Experience: {self.game.player.experience}/{self.game.player.experience_to_next_level}")
                self.update_battle_log(f"Earned {credits_gain} credits!")

                # Check for item drops
                dropped_items = self.npc.get_drops()
                if dropped_items:
                    for item in dropped_items:
                        self.game.player.add_item(item)
                        self.update_battle_log(f"Found {item.name}!")

                # Record battle in history
                self.game.record_battle(
                    self.npc.name,
                    True,  # Victory
                    self.turn,
                    credits_gain,
                    [item.name for item in dropped_items] if dropped_items else []
                )

                # If leveled up, show level up message in battle log
                if self.game.player.level > old_level:
                    self.update_battle_log(
                        f"\n🎉 Level up! {old_level} -> {self.game.player.level}")
                    self.update_battle_log(
                        f"HP: {self.game.player.max_health} (+{int(self.game.player.max_health * 0.1)})")
                    self.update_battle_log(
                        f"Attack: {self.game.player.attack} (+{int(self.game.player.attack * 0.1)})")
                    self.update_battle_log(
                        f"Defense: {self.game.player.defense} (+{int(self.game.player.defense * 0.1)})")
                    self.update_battle_log(
                        f"Agility: {self.game.player.agility} (+{int(self.game.player.agility * 0.1)})")

                # Update all GUI elements immediately
                self.on_battle_end(True)

                self.show_battle_result(True)
                return

            # NPC counter-attack
            damage = self.npc.attack_character(self.game.player)
            self.update_battle_log(
                f"{self.npc.name} counter-attacks for {damage} damage! "
                f"{self.game.player.name} has {self.game.player.health}/{self.game.player.max_health} HP remaining"
            )
            self.update_stats_display()
        else:
            self.update_battle_log(
                f"\n{self.npc.name} acts first (AGI: {self.npc.agility} > {self.game.player.agility})")
            # NPC attacks first
            damage = self.npc.attack_character(self.game.player)
            self.update_battle_log(
                f"{self.npc.name} attacks {self.game.player.name} for {damage} damage! "
                f"{self.game.player.name} has {self.game.player.health}/{self.game.player.max_health} HP remaining"
            )
            self.update_stats_display()

            if not self.game.player.is_alive():
                self.update_battle_log(
                    f"\n{self.game.player.name} has been defeated!")
                # Record battle in history
                self.game.record_battle(
                    self.npc.name,
                    False,  # Defeat
                    self.turn,
                    0,  # No credits gained
                    []  # No items gained
                )

                # Update all GUI elements immediately
                self.on_battle_end(False)

                self.show_battle_result(False)
                return

            # Player counter-attack
            damage = self.game.player.attack_character(self.npc)
            self.update_battle_log(
                f"{self.game.player.name} counter-attacks for {damage} damage! "
                f"{self.npc.name} has {self.npc.health}/{self.npc.max_health} HP remaining"
            )
            self.update_stats_display()

            if not self.npc.is_alive():
                self.update_battle_log(f"\n{self.npc.name} has been defeated!")

                # Give all rewards immediately
                exp_gain = self.npc.get_experience_value()
                credits_gain = self.npc.get_credit_value()
                old_level = self.game.player.level

                # Add experience and check for level up
                self.game.player.add_experience(exp_gain)
                self.game.player.credits += credits_gain
                # --- ADDED DEBUG LOG ---
                logging.debug(f"[BattleWindow] Credits Awarded: {credits_gain}. Player credits NOW: {self.game.player.credits}")
                # ---------------------

                # Show rewards in battle log
                self.update_battle_log(f"Gained {exp_gain} experience!")
                self.update_battle_log(
                    f"Experience: {self.game.player.experience}/{self.game.player.experience_to_next_level}")
                self.update_battle_log(f"Earned {credits_gain} credits!")

                # Check for item drops
                dropped_items = self.npc.get_drops()
                if dropped_items:
                    for item in dropped_items:
                        self.game.player.add_item(item)
                        self.update_battle_log(f"Found {item.name}!")

                # Record battle in history
                self.game.record_battle(
                    self.npc.name,
                    True,  # Victory
                    self.turn,
                    credits_gain,
                    [item.name for item in dropped_items] if dropped_items else []
                )

                # If leveled up, show level up message in battle log
                if self.game.player.level > old_level:
                    self.update_battle_log(
                        f"\n🎉 Level up! {old_level} -> {self.game.player.level}")
                    self.update_battle_log(
                        f"HP: {self.game.player.max_health} (+{int(self.game.player.max_health * 0.1)})")
                    self.update_battle_log(
                        f"Attack: {self.game.player.attack} (+{int(self.game.player.attack * 0.1)})")
                    self.update_battle_log(
                        f"Defense: {self.game.player.defense} (+{int(self.game.player.defense * 0.1)})")
                    self.update_battle_log(
                        f"Agility: {self.game.player.agility} (+{int(self.game.player.agility * 0.1)})")

                # Update all GUI elements immediately
                self.on_battle_end(True)

                self.show_battle_result(True)
                return

        self.turn += 1
        self.enable_action_buttons()
        self.update_battle_log("\nReady for next turn...")

    def disable_action_buttons(self):
        """Disable all action buttons"""
        for button in self.action_buttons:
            button.configure(state='disabled')

    def enable_action_buttons(self):
        """Enable all action buttons"""
        for button in self.action_buttons:
            button.configure(state='normal')

    def create_action_buttons(self):
        """Create battle action buttons"""
        options_frame = ttk.LabelFrame(
            self.main_frame, text="Actions", padding="5")  # Reduced padding
        options_frame.pack(fill='x', padx=5, pady=2)  # Reduced margins

        # Store buttons in a list for easy access
        self.action_buttons = []

        # Create a style for larger buttons
        style = ttk.Style()
        style.configure('Battle.TButton', font=(
            'Arial', 11), padding=5)  # Added style

        attack_button = ttk.Button(
            options_frame,
            text="⚔️ Attack",
            command=self.handle_attack,
            style='Battle.TButton'
        )
        attack_button.pack(fill='x', pady=2)  # Reduced spacing
        self.action_buttons.append(attack_button)

        item_button = ttk.Button(
            options_frame,
            text="📦 Use Item",
            command=self.handle_item,
            style='Battle.TButton'
        )
        item_button.pack(fill='x', pady=2)  # Reduced spacing
        self.action_buttons.append(item_button)

        run_button = ttk.Button(
            options_frame,
            text="🏃 Run Away",
            command=self.handle_run,
            style='Battle.TButton'
        )
        run_button.pack(fill='x', pady=2)  # Reduced spacing
        self.action_buttons.append(run_button)

    def handle_item(self):
        """Handle item usage"""
        from ..windows.item_window import ItemWindow
        ItemWindow(self.window, self.game, self.update_battle_log)

    def handle_run(self):
        """Handle run attempt"""
        if random.random() < 0.5:
            self.update_battle_log("Successfully ran away!")
            # Disable buttons during run sequence
            self.disable_action_buttons()
            # Show battle result with None to indicate run away
            self.show_battle_result(None)
        else:
            self.update_battle_log("Couldn't escape! The battle continues!")
            # If escape fails, player loses their turn and NPC attacks
            damage = self.npc.attack_character(self.game.player)
            self.update_battle_log(
                f"{self.npc.name} attacks {self.game.player.name} for {damage} damage! "
                f"{self.game.player.name} has {self.game.player.health}/{self.game.player.max_health} HP remaining"
            )
            self.update_stats_display()

            if not self.game.player.is_alive():
                self.show_battle_result(False)
            else:
                self.enable_action_buttons()

    def handle_battle_end(self, result):
        """Handle the end of the battle (victory or defeat)"""
        if result: # Player won
            logging.info(f"Battle ended: Player Victory against '{self.npc.name}'.")
            # Find original NPC position before clearing
            original_pos = None
            for pos, npc_obj in self.game.npcs:
                if npc_obj == self.npc:
                    original_pos = pos
                    break

            if original_pos:
                # Clear old NPC position from grid
                self.game.grid[original_pos[0]][original_pos[1]][original_pos[2]] = ' '
                # Remove NPC from the game's list
                self.game.npcs = [(p, n) for p, n in self.game.npcs if n != self.npc]

                # Respawn the NPC
                increased_stat = self.npc.respawn()
                self.update_battle_log(f"{self.npc.name} is recovering... ({increased_stat.capitalize()} increased!)")

                # Find new position
                new_pos = self.game.find_random_empty_spot(original_pos[0])
                if new_pos:
                    self.game.npcs.append((new_pos, self.npc))
                    self.game.grid[new_pos[0]][new_pos[1]][new_pos[2]] = self.npc.symbol
                    self.update_battle_log(f"{self.npc.name} respawned elsewhere on this level.")
                else:
                    log_msg = f"{self.npc.name} could not find a place to respawn on this level! (Will remain defeated for now)"
                    logging.error(log_msg)
                    self.update_battle_log(log_msg)
            else:
                 log_msg = f"Error finding original position for defeated NPC '{self.npc.name}'. Respawn skipped."
                 logging.error(log_msg)
                 self.update_battle_log(log_msg)
        else:
            logging.info(f"Battle ended: Player Defeat against '{self.npc.name}'.")
            # Handle defeat logic if needed (e.g., game over screen, respawn player)
            # Currently, the GUI just closes, and the player remains at 0 HP.

        # Call the original callback provided by GameGUI
        self.on_battle_end(result)
        self.destroy() # Close the battle window
