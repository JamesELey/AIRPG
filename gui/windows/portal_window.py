import tkinter as tk
from tkinter import ttk, messagebox
from .base_window import BaseWindow
from .boss_battle_window import BossBattleWindow


class PortalWindow(BaseWindow):
    def __init__(self, parent, game_instance, on_portal_action):
        """Initialize portal window"""
        super().__init__(parent, "Portal", "400x300")
        self.game = game_instance
        self.on_portal_action = on_portal_action

        self.create_portal_options()
        self.center_window()

    def create_portal_options(self):
        """Create portal movement options"""
        ttk.Label(
            self.main_frame,
            text="You've encountered a portal!",
            font=('Arial', 12, 'bold')
        ).pack(pady=10)

        ttk.Button(
            self.main_frame,
            text="🔽 Go Down (1)",
            command=lambda: self.handle_portal_action("1")
        ).pack(pady=5)

        ttk.Button(
            self.main_frame,
            text="🔼 Go Up (2)",
            command=lambda: self.handle_portal_action("2")
        ).pack(pady=5)

        ttk.Button(
            self.main_frame,
            text="❌ Cancel",
            command=self.destroy
        ).pack(pady=5)

    def ensure_level_keys_is_set(self):
        """Ensure level_keys exists and is a set"""
        if not hasattr(self.game.player, 'level_keys'):
            self.game.player.level_keys = set()
        elif not isinstance(self.game.player.level_keys, set):
            # Convert to set if it's not already a set
            self.game.player.level_keys = set(self.game.player.level_keys)

    def handle_portal_action(self, action):
        """Handle portal movement action"""
        try:
            # Check energy cost
            if self.game.player.energy < 2:
                messagebox.showwarning(
                    "Low Energy", "Not enough energy to use portal! (Requires 2 energy)")
                self.destroy()
                return

            # Deduct portal energy cost
            self.game.player.energy -= 2

            target_level = None
            if action == "1" and self.game.player_pos[0] > 0:  # Go down
                target_level = self.game.player_pos[0] - 1
            # Go up
            elif action == "2" and self.game.player_pos[0] < self.game.grid_depth - 1:
                target_level = self.game.player_pos[0] + 1

            if target_level is not None:
                # Ensure level_keys is a set
                self.ensure_level_keys_is_set()

                # Check if player has key for this level
                has_key = target_level in self.game.player.level_keys

                if not has_key:
                    # Show boss battle prompt
                    if messagebox.askyesno("Boss Battle",
                                           "You must defeat the portal guardians to proceed! Would you like to challenge them?\n\nThis will cost 15 energy."):
                        if self.game.player.energy >= 15:
                            self.game.player.energy -= 15
                            self.destroy()  # Close portal window
                            # Show boss battle window
                            BossBattleWindow(
                                self.window.master,
                                self.game,
                                target_level,
                                lambda result: self.handle_boss_battle_result(
                                    result, target_level, action)
                            )
                        else:
                            messagebox.showwarning(
                                "Low Energy", "Not enough energy for boss battle! (Requires 15 energy)")
                            self.game.player.energy += 2  # Refund portal cost
                            self.destroy()
                    else:
                        self.game.player.energy += 2  # Refund portal cost
                        self.destroy()
                else:
                    # Player has key, proceed with movement
                    self.destroy()
                    self.on_portal_action(action)
            else:
                # Invalid movement direction
                if action == "1":
                    messagebox.showwarning(
                        "Invalid Move", "Cannot go down from the bottom level!")
                else:
                    messagebox.showwarning(
                        "Invalid Move", "Cannot go up from the top level!")
                self.game.player.energy += 2  # Refund energy
                self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error using portal: {str(e)}")
            self.destroy()

    def handle_boss_battle_result(self, result, target_level, action):
        """Handle the result of a boss battle"""
        if result:
            self.ensure_level_keys_is_set()
            self.game.player.level_keys.add(target_level)
            # Proceed with portal movement
            self.on_portal_action(action)
        else:
            messagebox.showinfo(
                "Battle Result", "Failed to defeat the guardians. Try again when you're stronger!")
