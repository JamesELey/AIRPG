import tkinter as tk
from tkinter import ttk, messagebox
from .base_window import BaseWindow
from ..windows.item_window import ItemWindow


class BossBattleWindow(BaseWindow):
    def __init__(self, parent, game_instance, target_level, on_battle_end):
        """Initialize boss battle window"""
        super().__init__(parent, "Portal Boss Battle", "600x800")
        self.game = game_instance
        self.target_level = target_level
        self.on_battle_end = on_battle_end

        # Create boss NPCs
        from entities.npc import NPC
        self.boss1 = NPC.generate_random(target_level + 1, is_boss=True)
        self.boss2 = NPC.generate_random(target_level + 1, is_boss=True)

        self.create_battle_info()
        self.create_boss_frames()
        self.create_battle_log()
        self.create_battle_button()
        self.center_window()

    def create_battle_info(self):
        """Create battle information header"""
        ttk.Label(
            self.main_frame,
            text="⚠️ PORTAL BOSS BATTLE ⚠️",
            font=('Arial', 16, 'bold')
        ).pack(pady=10)

        ttk.Label(
            self.main_frame,
            text="Two powerful guardians block your path!",
            font=('Arial', 12)
        ).pack(pady=5)

    def create_boss_frames(self):
        """Create frames showing boss information"""
        # Boss 1 info
        boss1_frame = ttk.LabelFrame(
            self.main_frame, text=f"Boss #1: {self.boss1.name}", padding="10")
        boss1_frame.pack(fill='x', pady=10)
        ttk.Label(
            boss1_frame, text=f"Health: {self.boss1.health}/{self.boss1.max_health}").pack()
        ttk.Label(
            boss1_frame, text=f"Attack: {self.boss1.get_total_attack()}").pack()
        ttk.Label(boss1_frame, text=f"Defense: {self.boss1.defense}").pack()

        # Boss 2 info
        boss2_frame = ttk.LabelFrame(
            self.main_frame, text=f"Boss #2: {self.boss2.name}", padding="10")
        boss2_frame.pack(fill='x', pady=10)
        ttk.Label(
            boss2_frame, text=f"Health: {self.boss2.health}/{self.boss2.max_health}").pack()
        ttk.Label(
            boss2_frame, text=f"Attack: {self.boss2.get_total_attack()}").pack()
        ttk.Label(boss2_frame, text=f"Defense: {self.boss2.defense}").pack()

    def create_battle_log(self):
        """Create the battle log frame"""
        log_frame = ttk.LabelFrame(
            self.main_frame, text="Battle Log", padding="10")
        log_frame.pack(fill='both', expand=True, pady=10)

        self.battle_log = tk.Text(log_frame, height=10, wrap='word')
        self.battle_log.pack(fill='both', expand=True)
        self.battle_log.configure(state='disabled')

        scrollbar = ttk.Scrollbar(
            log_frame, orient='vertical', command=self.battle_log.yview)
        scrollbar.pack(side='right', fill='y')
        self.battle_log.configure(yscrollcommand=scrollbar.set)

    def create_battle_button(self):
        """Create the battle control button"""
        self.battle_button = ttk.Button(
            self.main_frame,
            text="Begin Battle with First Guardian",
            command=self.start_boss_battles
        )
        self.battle_button.pack(pady=10)

    def update_battle_log(self, message):
        """Update the battle log with a new message"""
        self.battle_log.configure(state='normal')
        self.battle_log.insert('end', message + '\n')
        self.battle_log.see('end')
        self.battle_log.configure(state='disabled')

    def start_boss_battles(self):
        """Start the sequential boss battles"""
        # Disable the button during battle
        self.battle_button.configure(state='disabled')

        # Battle first boss
        result1 = self.game.battle(
            self.game.player, self.boss1, self.update_battle_log)
        if result1 and self.game.player.is_alive():
            # Ask if player wants to use items before second battle
            if messagebox.askyesno("Use Items",
                                   "You've defeated the first guardian! Would you like to use items before facing the second?"):
                ItemWindow(self.window, self.game, self.update_battle_log)

            # Update button for second boss
            self.battle_button.configure(
                text="Begin Battle with Second Guardian",
                state='normal',
                command=self.battle_second_boss
            )
        else:
            self.update_battle_log(
                "Defeat! The first guardian was too strong!")
            self.show_continue_button(False)

    def ensure_level_keys_is_set(self):
        """Ensure level_keys exists and is a set"""
        if not hasattr(self.game.player, 'level_keys'):
            self.game.player.level_keys = set()
        elif not isinstance(self.game.player.level_keys, set):
            # Convert to set if it's not already a set
            self.game.player.level_keys = set(self.game.player.level_keys)

    def battle_second_boss(self):
        """Handle the second boss battle"""
        # Disable the button during battle
        self.battle_button.configure(state='disabled')

        # Battle second boss
        result2 = self.game.battle(
            self.game.player, self.boss2, self.update_battle_log)
        if result2:
            self.ensure_level_keys_is_set()
            self.game.player.level_keys.add(self.target_level)
            self.update_battle_log(
                "🎉 Victory! You've defeated both guardians and gained a level key!")
            self.show_continue_button(True)
        else:
            self.update_battle_log(
                "Defeat! The second guardian was too strong!")
            self.show_continue_button(False)

    def show_continue_button(self, victory):
        """Show the continue button and end the battle"""
        self.battle_button.configure(
            text="Continue",
            state='normal',
            command=lambda: self.handle_battle_end(victory)
        )

    def handle_battle_end(self, victory):
        """Handle the end of the boss battles"""
        if victory:
            # Calculate and award experience (base 150 exp + level bonus)
            # More experience for boss battles
            exp_gain = 150 + (self.target_level * 20)
            old_level = self.game.player.level

            # Add experience and check for level up
            self.game.player.add_experience(exp_gain)

            # Show experience and level up message
            self.update_battle_log(
                f"Gained {exp_gain} experience from defeating the portal guardians!")
            if self.game.player.level > old_level:
                level_diff = self.game.player.level - old_level
                self.update_battle_log(
                    f"🎉 Level Up! You are now level {self.game.player.level}!")
                if level_diff > 1:
                    self.update_battle_log(f"Gained {level_diff} levels!")

                # Show stat increases
                self.update_battle_log("Stats increased:")
                self.update_battle_log(
                    f"❤️ Max HP: +20 (Now {self.game.player.max_health})")
                self.update_battle_log(
                    f"⚔️ Attack: +5 (Now {self.game.player.attack})")
                self.update_battle_log(
                    f"🛡️ Defense: +3 (Now {self.game.player.defense})")
                self.update_battle_log(
                    f"💨 Agility: +2 (Now {self.game.player.agility})")
                self.update_battle_log(
                    f"⚡ Max Energy: +10 (Now {self.game.player.max_energy})")

            self.ensure_level_keys_is_set()
            self.game.player.level_keys.add(self.target_level)

        self.on_battle_end(victory)
        self.destroy()
