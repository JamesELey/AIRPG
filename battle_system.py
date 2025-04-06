import random
import time
from .items import Weapon
from .entities import NPC


class BattleSystem:
    def __init__(self, game):
        self.game = game
        self.battle_history = []

    def generate_attack_text(self, attacker, defender, damage, weapon_damage):
        """Generate descriptive text for attacks"""
        weapon_verbs = {
            'Sword': ['slashes', 'strikes', 'cuts', 'swings at'],
            'Axe': ['hacks', 'chops', 'cleaves', 'strikes'],
            'Spear': ['thrusts', 'jabs', 'pierces', 'stabs'],
            'Bow': ['shoots', 'fires at', 'looses an arrow at', 'aims at'],
            'Dagger': ['stabs', 'slashes', 'cuts', 'pierces'],
            'Mace': ['smashes', 'crushes', 'strikes', 'bashes'],
            'Staff': ['strikes', 'hits', 'bashes', 'swings at'],
            'Crossbow': ['shoots', 'fires at', 'looses a bolt at', 'aims at']
        }

        hit_descriptions = [
            "landing a solid hit",
            "finding its mark",
            "striking true",
            "hitting its target",
            "making contact",
            "landing a blow"
        ]

        if attacker.weapon:
            verb = random.choice(weapon_verbs.get(
                attacker.weapon.name, ['attacks']))
            hit_desc = random.choice(hit_descriptions)
            return f"⚔️ {attacker.name} {verb} {defender.name} with their {attacker.weapon.name.lower()} {hit_desc} for {damage} damage!"
        else:
            return f"⚔️ {attacker.name} attacks {defender.name} for {damage} damage!"

    def handle_phoenix_down(self, player):
        """Handle Phoenix Down revival"""
        phoenix_down = next(
            (item for item in player.inventory if item.name == "Phoenix Down"), None)
        if phoenix_down:
            print(f"\n💀 {player.name} has fallen! But wait...")
            print(f"You have a Phoenix Down in your inventory!")
            choice = input("Use Phoenix Down to revive? (y/n): ").lower()
            if choice in ['y', 'yes']:
                player.inventory.remove(phoenix_down)
                player.health = player.max_health
                print(
                    f"\n🔥 Used Phoenix Down. {player.name} has been revived with {player.health} HP!")
                print(f"The battle continues!")
                return True
        return False

    def _display_battle_stats(self, player, npc):
        """Display battle statistics for both combatants"""
        print(f"\n{player.name} Stats: HP: {player.health}/{player.max_health}, ATK: {player.get_total_attack()} (Base: {player.attack})")
        if player.weapon:
            print(
                f"⚔️ Weapon: {player.weapon.name} (+{player.weapon.attack} ATK)")
        print(f"🛡️ DEF: {player.defense}, AGI: {player.agility}")
        print(f"💰 Credits: {player.credits}")

        print(f"\n{npc.name} Stats: HP: {npc.health}/{npc.max_health}, ATK: {npc.get_total_attack()} (Base: {npc.attack})")
        if npc.weapon:
            print(f"⚔️ Weapon: {npc.weapon.name} (+{npc.weapon.attack} ATK)")
        print(f"🛡️ DEF: {npc.defense}, AGI: {npc.agility}")
        print(f"💰 Credits: {npc.credits}")

    def _handle_item_usage(self, player):
        """Handle item usage during battle"""
        print("\nYour inventory:")
        if not player.inventory:
            print("No items available.")
            return

        # Display items with numbers
        for i, item in enumerate(player.inventory, 1):
            print(f"{i}. {item.name} - {item.description}")

        # Get item choice
        choice = input(
            "\nEnter item number to use (or press Enter to cancel): ").strip()
        if not choice:
            return

        try:
            item_index = int(choice) - 1
            if 0 <= item_index < len(player.inventory):
                selected_item = player.inventory[item_index]
                old_health = player.health  # Store old health to calculate healing
                # Remove item before using it
                player.inventory.remove(selected_item)
                # Use the item
                selected_item.use(player)
                health_gained = player.health - old_health  # Calculate healing done
                print(f"\nUsed {selected_item.name}!")
                if health_gained > 0:
                    print(f"❤️ Healed for {health_gained} HP!")
                print(f"Current HP: {player.health}/{player.max_health}")

                # Update game statistics for item usage
                self.game.game_stats["items_used"][selected_item.name] = self.game.game_stats["items_used"].get(
                    selected_item.name, 0) + 1
            else:
                print("Invalid item number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    def battle(self, player, npc):
        """Run a battle between player and NPC"""
        battle_data = {
            "player_name": player.name,
            "npc_name": npc.name,
            "npc_symbol": npc.symbol,
            "level": npc.level,
            "turns": 0,
            "player_start_hp": player.health,
            "npc_start_hp": npc.health,
            "phoenix_downs_used": 0,
            "result": None,
            "player_end_hp": 0,
            "npc_end_hp": 0,
            "credits_gained": 0,
            "items_found": [],
            "experience_gained": 0
        }

        print(f"\nBattle between {player.name} and {npc.name} ({npc.symbol})!")
        print(f"Player Stats: HP: {player.health}/{player.max_health}, ATK: {player.attack} (Base: {player.attack}), DEF: {player.defense}, AGI: {player.agility}")

        # Reset health for both characters
        player.health = player.max_health
        npc.health = npc.max_health

        # Battle loop
        while True:
            battle_data["turns"] += 1
            print(f"\nTurn {battle_data['turns']}")

            # Player's turn
            if not self._process_attack(player, npc, battle_data):
                # Player was defeated
                battle_data["player_end_hp"] = player.health
                battle_data["npc_end_hp"] = npc.health
                # Reset combo on defeat
                self.game.combo_count = 0
                self.game.combo_multiplier = 1.0
                return self._handle_defeat(player, npc, battle_data)

            # NPC's turn
            if not self._process_attack(npc, player, battle_data):
                # NPC was defeated
                battle_data["player_end_hp"] = player.health
                battle_data["npc_end_hp"] = npc.health
                # Increase combo on victory
                self.game.combo_count += 1
                self.game.combo_multiplier = 1.0 + (0.1 * self.game.combo_count)
                return self._handle_victory(player, npc, battle_data)

    def _process_attack(self, attacker, defender, battle_data):
        """Process an attack between two characters"""
        print(f"\n{attacker.name}'s turn:")
        damage = attacker.attack_character(defender)
        weapon_damage = attacker.weapon.attack if attacker.weapon else 0
        print(self.generate_attack_text(
            attacker, defender, damage, weapon_damage))

        if weapon_damage > 0:
            print(f"  (Base: {attacker.attack}, Weapon: +{weapon_damage})")
        print(f"🛡️ {defender.name}'s defense reduced damage by {defender.defense}")
        print(
            f"❤️ {defender.name} has {defender.health}/{defender.max_health} HP remaining")

        # Handle Phoenix Down if player dies
        if not defender.is_alive() and defender == self.game.player:
            if self.handle_phoenix_down(defender):
                battle_data["phoenix_downs_used"] += 1
                return True

        return defender.is_alive()

    def _handle_victory(self, player, npc, battle_data):
        """Handle player victory in battle"""
        print(f"\n{'='*50}")
        print("Battle Results:")
        print(f"{'='*50}")

        # Calculate rewards with combo multiplier
        base_credit_reward = int(npc.credits * 0.08)
        combo_bonus = int(base_credit_reward * (self.game.combo_multiplier - 1))
        credit_reward = base_credit_reward + combo_bonus
        player.credits += credit_reward
        battle_data["result"] = "Victory"
        battle_data["credits_gained"] = credit_reward

        # Update game statistics
        self.game.game_stats["monsters_killed"] += 1
        self.game.game_stats["battles_won"] += 1
        self.game.game_stats["total_credits_earned"] += credit_reward

        # Display results
        print(f"\n🎉 {player.name} wins the battle!")
        print(
            f"🏆 {player.name} defeated {npc.name} ({npc.symbol}) in {battle_data['turns']} turns!")
        print(
            f"❤️ {player.name} finished with {player.health}/{player.max_health} HP")
        print(
            f"💰 {player.name} gained {credit_reward} credits! (Base: {base_credit_reward} + Combo Bonus: {combo_bonus})")

        # Handle item drops
        if npc.inventory:
            for item in npc.inventory:
                player.inventory.append(item)
                battle_data["items_found"].append(item.name)
                print(f"🎁 You found {item.name}!")

        # Handle enemy respawn if it's not a boss
        if hasattr(npc, 'is_boss') and not npc.is_boss:
            # Get the NPC's position from the game's npcs list
            for npc_pos, npc_obj in self.game.npcs:
                if npc_obj == npc:
                    # Remove from current position
                    self.game.grid[npc_pos[0]][npc_pos[1]][npc_pos[2]] = ' '
                    self.game.npcs.remove((npc_pos, npc_obj))
                    
                    # Respawn the NPC
                    increased_stat = npc_obj.respawn()
                    print(f"\n{npc_obj.name} has respawned with increased {increased_stat}!")
                    
                    # Find new random position on same level
                    while True:
                        row = random.randint(0, self.game.grid_height - 1)
                        col = random.randint(0, self.game.grid_width - 1)
                        if self.game.is_position_empty(npc_pos[0], row, col):
                            self.game.grid[npc_pos[0]][row][col] = npc_obj.symbol
                            self.game.npcs.append(([npc_pos[0], row, col], npc_obj))
                            break
                    break

        # Add battle to history
        self.battle_history.append(battle_data)
        return True

    def _handle_defeat(self, player, npc, battle_data):
        """Handle player defeat in battle"""
        print(f"\n{'='*50}")
        print("Battle Results:")
        print(f"{'='*50}")

        # Calculate penalties
        credit_loss = int(player.credits * 0.08)
        npc.credits += credit_loss
        battle_data["result"] = "Defeat"

        # Update game statistics
        self.game.game_stats["battles_lost"] += 1

        # Display results
        print(f"\n💀 {npc.name} wins the battle!")
        print(
            f"🏆 {npc.name} ({npc.symbol}) defeated {player.name} in {battle_data['turns']} turns!")
        print(f"❤️ {npc.name} finished with {npc.health}/{npc.max_health} HP")
        print(
            f"💰 {npc.name} gained {credit_loss} credits! (8% of {player.name}'s {player.credits} credits)")

        # Add battle to history
        self.battle_history.append(battle_data)
        return False

    def battle_portal_boss(self, player):
        """Trigger a boss battle with two NPCs when player tries to use a portal"""
        # Update game statistics for portal boss attempts
        self.game.game_stats["portal_boss_attempts"] += 1

        print(f"\n{'='*50}")
        print("⚠️ PORTAL BOSS BATTLE ⚠️")
        print(f"{'='*50}")
        print("\nThe portal's energy fluctuates violently as you approach...")
        print("Two powerful guardians materialize, blocking your path!")

        # Create two boss NPCs with enhanced stats
        boss_symbols = ['B', 'K']  # B for Boss, K for King
        boss_types = ['Guardian', 'Warden']
        boss_adjectives = [
            'Ancient', 'Corrupted', 'Void', 'Eternal', 'Shadow',
            'Infernal', 'Celestial', 'Abyssal', 'Divine', 'Phantom'
        ]

        bosses = []
        for i in range(2):
            # Generate more balanced stats based on player's current level
            # Reduced level multiplier and base stats for easier early game
            # Reduced from 0.15 to 0.08 per level
            level_multiplier = 1.0 + (self.game.player_pos[0] * 0.08)

            # Base stats now scale with player's stats
            # 80% of player's health
            health = int((player.max_health * 0.8) * level_multiplier)
            # 70% of player's attack
            attack = int((player.attack * 0.7) * level_multiplier)
            # 70% of player's defense
            defense = int((player.defense * 0.7) * level_multiplier)
            # 70% of player's agility
            agility = int((player.agility * 0.7) * level_multiplier)
            credits = int(random.randint(1000, 3000) * level_multiplier)

            # Weapon stats also scaled down
            weapon_names = ['Sword', 'Axe', 'Spear', 'Bow',
                            'Dagger', 'Mace', 'Staff', 'Crossbow']
            weapon_prefixes = ['Soul', 'Doom', 'Void',
                               'Dragon', 'Ancient', 'Chaos', 'Abyssal', 'Divine']
            weapon_name = f"{random.choice(weapon_prefixes)} {random.choice(weapon_names)}"
            weapon_attack = int((player.weapon.attack if player.weapon else player.attack)
                                * 0.5 * level_multiplier)  # 50% of player's weapon attack
            boss_weapon = Weapon(weapon_name, weapon_attack)

            # Generate boss name
            boss_name = f"{random.choice(boss_adjectives)} {boss_types[i]} of Level {self.game.player_pos[0]}"

            # Create the boss character using generate_random
            boss = NPC.generate_random(self.game.player_pos[0], is_boss=True)
            boss.name = boss_name  # Override the generated name
            boss.symbol = boss_symbols[i]  # Override the symbol
            boss.weapon = boss_weapon
            boss.credits = credits
            boss.inventory = []

            # Give boss better items
            for _ in range(2):  # Each boss has 2 items
                # Higher chance of better items
                # Adjusted weights to favor lower tier items
                weights = [30, 30, 25, 15]
                item_index = random.choices(
                    range(len(self.game.available_items)), weights=weights, k=1)[0]
                boss.inventory.append(self.game.available_items[item_index])

            bosses.append(boss)

        # Display boss information
        for i, boss in enumerate(bosses):
            print(f"\nBoss #{i+1}: {boss.name} ({boss.symbol})")
            print(
                f"HP: {boss.health}/{boss.max_health}, ATK: {boss.get_total_attack()} (Base: {boss.attack})")
            print(f"⚔️ Weapon: {boss.weapon.name} (+{boss.weapon.attack} ATK)")
            print(f"🛡️ DEF: {boss.defense}, AGI: {boss.agility}")

        # Ask if player wants to use items before the first boss
        print("\nWould you like to use any items before facing the first guardian?")
        use_items = input(
            "Enter 'y' to use items, any other key to continue: ").lower()
        if use_items == 'y':
            self._handle_item_usage(player)

        input("\nPress Enter to begin the boss battle...")

        # Begin the sequential battles
        # Player must defeat both bosses to proceed
        battle_results = []
        remaining_health = player.health  # Track player health between fights
        total_credits_gained = 0
        items_found = []
        total_turns = 0
        boss_battle_record = []

        for i, boss in enumerate(bosses):
            self.game.clear_screen()
            print(f"\n{'='*50}")
            print(f"Boss Battle {i+1}/2: {player.name} vs {boss.name}")
            print(f"{'='*50}")

            # Restore player's health to the current value (persists between boss fights)
            player.health = remaining_health

            # Battle with current boss
            result = self.battle(player, boss)
            battle_results.append(result)

            # Get the most recent battle data
            if self.battle_history:
                recent_battle = self.battle_history[-1]
                total_turns += recent_battle["turns"]
                if recent_battle["result"] == "Victory":
                    total_credits_gained += recent_battle["credits_gained"]
                    items_found.extend(recent_battle["items_found"])

                # Store this boss fight record for overall summary
                boss_battle_record.append({
                    "boss_name": boss.name,
                    "boss_symbol": boss.symbol,
                    "result": recent_battle["result"],
                    "turns": recent_battle["turns"],
                    "player_end_hp": recent_battle["player_end_hp"],
                    "boss_end_hp": recent_battle["npc_end_hp"]
                })

            # Update player's remaining health for next fight
            remaining_health = player.health

            # If player defeated, end the battles
            if not player.is_alive():
                # Add overall portal boss battle entry to history
                portal_battle_data = {
                    "player_name": player.name,
                    "is_portal_boss": True,
                    "portal_level": self.game.player_pos[0],
                    "npc_name": "Portal Guardians",
                    "npc_symbol": "PG",
                    "level": self.game.player_pos[0],
                    "turns": total_turns,
                    "player_start_hp": player.max_health,  # Start with max health
                    "npc_start_hp": sum(boss.max_health for boss in bosses),
                    "phoenix_downs_used": sum(1 for battle in self.battle_history[-len(bosses):] if battle.get("phoenix_downs_used", 0) > 0),
                    "result": "Defeat",
                    "player_end_hp": 0,
                    "npc_end_hp": sum(data["boss_end_hp"] for data in boss_battle_record),
                    "credits_gained": total_credits_gained,
                    "items_found": items_found,
                    "boss_battles": boss_battle_record,
                    "bosses_defeated": sum(1 for result in battle_results if result)
                }
                self.battle_history.append(portal_battle_data)

                print("\nYou have been defeated by the portal guardians!")
                return False

            # Between boss fights, give player a chance to use items
            if i < len(bosses) - 1:
                print(
                    "\nYou've defeated one guardian, but another still blocks your path!")
                print(f"Your current HP: {player.health}/{player.max_health}")

                # Ask if player wants to use items before next fight
                print("\nWould you like to use items before facing the next guardian?")
                use_items = input(
                    "Enter 'y' to use items, any other key to continue: ").lower()
                if use_items == 'y':
                    self._handle_item_usage(player)

        # Add overall portal boss battle entry to history
        portal_battle_data = {
            "player_name": player.name,
            "is_portal_boss": True,
            "portal_level": self.game.player_pos[0],
            "npc_name": "Portal Guardians",
            "npc_symbol": "PG",
            "level": self.game.player_pos[0],
            "turns": total_turns,
            "player_start_hp": player.max_health,  # Start with max health
            "npc_start_hp": sum(boss.max_health for boss in bosses),
            "phoenix_downs_used": sum(1 for battle in self.battle_history[-len(bosses):] if battle.get("phoenix_downs_used", 0) > 0),
            "result": "Victory" if all(battle_results) else "Partial Victory",
            "player_end_hp": player.health,
            "npc_end_hp": 0 if all(battle_results) else sum(data["boss_end_hp"] for data in boss_battle_record),
            "credits_gained": total_credits_gained,
            "items_found": items_found,
            "boss_battles": boss_battle_record,
            "bosses_defeated": sum(1 for result in battle_results if result)
        }
        self.battle_history.append(portal_battle_data)

        # Check if player won all battles
        if all(battle_results):
            print("\n🎉 You have defeated all the portal guardians!")
            print("The portal stabilizes, allowing you to pass through safely.")

            # Update game statistics for successful portal boss defeat
            self.game.game_stats["portal_bosses_defeated"] += 1

            # Award special rewards for defeating portal bosses
            self.award_portal_boss_rewards(player)

            return True
        else:
            return False

    def award_portal_boss_rewards(self, player):
        """Award special rewards for defeating portal bosses"""
        print(f"\n{'='*50}")
        print("🏆 PORTAL GUARDIAN REWARDS 🏆")
        print(f"{'='*50}")
        print("\nThe defeated guardians leave behind powerful energy that enhances your abilities!")

        # Calculate reward values based on player level
        level_multiplier = 1.0 + \
            (0.1 * self.game.player_pos[0])  # 10% per level

        # 1. Bonus Credits (always awarded)
        bonus_credits = int(random.randint(500, 1000) * level_multiplier)
        player.credits += bonus_credits
        print(
            f"\n💰 You gain {bonus_credits} bonus credits from the portal energy!")

        # 2. Permanent Stat Boost (random stat)
        stat_boost_chance = 0.7  # 70% chance for stat boost
        if random.random() < stat_boost_chance:
            # Choose which stat to boost
            stat_choice = random.randint(1, 4)
            boost_amount = 0

            if stat_choice == 1:  # Max Health boost
                boost_amount = int(random.randint(10, 20) * level_multiplier)
                player.max_health += boost_amount
                player.health += boost_amount  # Also increase current health
                print(
                    f"\n❤️ Your max health permanently increases by {boost_amount}!")
                print(f"   New max health: {player.max_health}")

            elif stat_choice == 2:  # Attack boost
                boost_amount = int(random.randint(2, 5) * level_multiplier)
                player.attack += boost_amount
                print(
                    f"\n⚔️ Your attack permanently increases by {boost_amount}!")
                print(f"   New attack: {player.attack}")

            elif stat_choice == 3:  # Defense boost
                boost_amount = int(random.randint(2, 5) * level_multiplier)
                player.defense += boost_amount
                print(
                    f"\n🛡️ Your defense permanently increases by {boost_amount}!")
                print(f"   New defense: {player.defense}")

            elif stat_choice == 4:  # Agility boost
                boost_amount = int(random.randint(1, 3) * level_multiplier)
                player.agility += boost_amount
                print(
                    f"\n💨 Your agility permanently increases by {boost_amount}!")
                print(f"   New agility: {player.agility}")

        # 3. Energy Boost (always awarded)
        energy_boost = int(random.randint(20, 50) * level_multiplier)
        # 20% of energy boost also increases max energy
        max_energy_boost = int(energy_boost * 0.2)

        player.energy = min(player.energy + energy_boost,
                            player.max_energy + max_energy_boost)
        player.max_energy += max_energy_boost

        print(f"\n⚡ Your energy is restored by {energy_boost} points!")
        print(f"   Your max energy increases by {max_energy_boost} points!")
        print(f"   New energy: {player.energy}/{player.max_energy}")

        # 4. Special Item Reward (chance based)
        special_item_chance = 0.5  # 50% chance for special item
        if random.random() < special_item_chance:
            # Determine which items to give
            # Higher levels have better chances for better items
            if self.game.player_pos[0] >= 8:  # High level
                # Strong preference for large potions and phoenix downs
                weights = [5, 15, 40, 40]
            elif self.game.player_pos[0] >= 4:  # Mid level
                # Preference for medium/large potions
                weights = [10, 30, 40, 20]
            else:  # Low level
                weights = [20, 40, 30, 10]  # More balanced distribution

            # Select random item based on weights
            item_index = random.choices(
                range(len(self.game.available_items)), weights=weights, k=1)[0]
            selected_item = self.game.available_items[item_index]

            # Add item to inventory
            player.inventory.append(selected_item)
            print(
                f"\n🎁 You find a {selected_item.name} among the guardian's remains!")

            # 25% chance to get a second item at higher levels
            if self.game.player_pos[0] >= 5 and random.random() < 0.25:
                item_index = random.choices(
                    range(len(self.game.available_items)), weights=weights, k=1)[0]
                second_item = self.game.available_items[item_index]
                player.inventory.append(second_item)
                print(f"   You also find a {second_item.name}!")

        # Wait for player to acknowledge
        input("\nPress Enter to continue...")
