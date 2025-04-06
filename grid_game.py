import random
import json
import os
from datetime import datetime, timedelta
import traceback
import logging
import importlib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from entities.player import Player
from entities.npc import NPC
from items.item import Item
from items.weapon import Weapon
from items.potion import Potion, SmallPotion, MediumPotion, LargePotion
from items.energy_potion import EnergyPotion
from items.revive_potion import RevivePotion
from items.crop import Crop
from systems.time_system import TimeSystem
from systems.weather_system import WeatherSystem
from utils.environment import get_env, get_float_env

# Import ItemFactory for deserialization
from items.item_factory import ItemFactory

# Import specific item types for store inventory
from items.sick_note import SickNote

# Define store symbol
STORE_SYMBOL = '$'
# Define portal symbol
PORTAL_SYMBOL = '@'

# Try to import and use dotenv, but handle gracefully if it fails
try:
    from dotenv import load_dotenv
    # Try to load environment variables, but don't fail if there's an issue
    try:
        # Try different encodings
        try:
            load_dotenv(encoding='utf-8-sig')  # Handle UTF-8 with BOM
            env_loaded = True
        except BaseException:
            try:
                load_dotenv(encoding='utf-8')  # Try standard UTF-8
                env_loaded = True
            except BaseException:
                load_dotenv(encoding='ascii')  # Fallback to ASCII
        env_loaded = True
    except Exception as e:
        print(f"Note: Using default settings (could not load .env file)")
        env_loaded = False
except ImportError:
    print("Note: Using default settings (python-dotenv not installed)")
    env_loaded = False


def get_env(key, default):
    """Helper function to get environment variable with a default value"""
    if env_loaded:
        try:
            return os.getenv(key, default)
        except BaseException:
            return default
    else:
        return default


def get_float_env(key, default):
    """Helper function to get environment variable as float with a default value"""
    value = get_env(key, default)
    try:
        return float(value)
    except (ValueError, TypeError):
        return float(default)


class Item:
    def __init__(self, name, description, effect=None):
        self.name = name
        self.description = description
        self.effect = effect
        
    def use(self, character):
        if self.effect:
            return self.effect(character)
        return False

# Item effects defined as functions


def small_potion_effect(character):
    heal_amount = 20
    if character.health < character.max_health:
        old_health = character.health
        character.health = min(
            character.health + heal_amount, character.max_health)
        print(
            f"🧪 Used Small Potion. Restored {character.health - old_health} HP.")
        return True
    else:
        print(f"❌ {character.name} is already at full health!")
        return False
        
        
def medium_potion_effect(character):
    heal_amount = 50
    if character.health < character.max_health:
        old_health = character.health
        character.health = min(
            character.health + heal_amount, character.max_health)
        print(
            f"🧪 Used Medium Potion. Restored {character.health - old_health} HP.")
        return True
    else:
        print(f"❌ {character.name} is already at full health!")
        return False
        
        
def large_potion_effect(character):
    heal_amount = 100
    if character.health < character.max_health:
        old_health = character.health
        character.health = min(
            character.health + heal_amount, character.max_health)
        print(
            f"🧪 Used Large Potion. Restored {character.health - old_health} HP.")
        return True
    else:
        print(f"❌ {character.name} is already at full health!")
        return False
        
        
def phoenix_down_effect(character):
    if character.health <= 0:
        # Changed to restore full health instead of half
        character.health = character.max_health
        print(
            f"🔥 Used Phoenix Down. {character.name} has been revived with {character.health} HP!")
        return True
    else:
        print(
            f"❌ Cannot use Phoenix Down on {character.name} while they are still alive!")
        return False


def sick_note_effect(character):
    print(
        f"📝 {character.name} is holding onto the Sick Note to skip a portal boss battle.")
    return False  # Don't consume the item when checking it


class Character:
    def __init__(self, name, health, attack, defense,
                 agility, symbol, weapon=None, credits=0):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.agility = agility
        self.symbol = symbol
        self.weapon = weapon
        self.credits = credits
        self.energy = 50  # Starting energy
        self.max_energy = 50  # Maximum energy
        self.inventory = []  # Add inventory list to store items
        self.level_keys = []  # Add list to track which level keys the player has
        
    def is_alive(self):
        return self.health > 0
        
    def has_energy(self, amount):
        return self.energy >= amount
        
    def use_energy(self, amount):
        if self.has_energy(amount):
            self.energy -= amount
            return True
        return False
        
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        return actual_damage
        
    def attack_character(self, target):
        total_attack = self.attack
        if self.weapon:
            total_attack += self.weapon.attack
        return target.take_damage(total_attack)
        
    def get_total_attack(self):
        return self.attack + (self.weapon.attack if self.weapon else 0)

    def add_to_inventory(self, item):
        self.inventory.append(item)

    def remove_from_inventory(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False


class GridGame:

    # --- Remove Class Attributes / Constants --- #
    # PORTAL_SYMBOL = '@'
    # STORE_SYMBOL = '$'
    # PLAYER_SYMBOL = 'P' # Player class defines its own symbol
    # ----------------------------------------- #

    # --- Grid Population (Defined BEFORE __init__) --- #
    def populate_grid_for_level(self, level: int):
        """Updates the internal grid data for a specific level based on current game state."""
        # Check if grid exists and level is valid
        if not hasattr(self, 'grid') or not (0 <= level < len(self.grid)):
             logging.error(f"Attempted to populate invalid level {level} or grid not initialized.")
             return
        # Check if grid dimensions are set
        if not hasattr(self, 'grid_height') or not hasattr(self, 'grid_width'):
             logging.error(f"Grid dimensions not set before populating level {level}.")
             return

        logging.debug(f"Populating grid for level {level}.")
        # Clear the level grid first (fill with empty space)
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                self.grid[level][r][c] = ' '

        # Place portal if it's on this level and exists
        if hasattr(self, 'portal_pos') and self.portal_pos and self.portal_pos[0] == level:
            _, r, c = self.portal_pos
            if 0 <= r < self.grid_height and 0 <= c < self.grid_width:
                self.grid[level][r][c] = PORTAL_SYMBOL
            else:
                logging.warning(f"Portal position {self.portal_pos} out of bounds for level {level}.")

        # Place stores if they are on this level and exist
        if hasattr(self, 'store_pos'):
             for store_pos in self.store_pos:
                if store_pos[0] == level:
                    _, r, c = store_pos
                    if 0 <= r < self.grid_height and 0 <= c < self.grid_width:
                        self.grid[level][r][c] = STORE_SYMBOL
                    else:
                        logging.warning(f"Store position {store_pos} out of bounds for level {level}.")

        # Place NPCs if they are on this level and exist
        if hasattr(self, 'npcs'):
             for npc_pos, npc in self.npcs:
                if npc_pos[0] == level:
                    _, r, c = npc_pos
                    if 0 <= r < self.grid_height and 0 <= c < self.grid_width:
                        # Ensure NPC symbol doesn't overwrite portal or store (portal/store take precedence)
                        if self.grid[level][r][c] == ' ':
                             self.grid[level][r][c] = npc.symbol
                    else:
                        logging.warning(f"NPC position {npc_pos} out of bounds for level {level}.")

        # Place crops if they are on this level and exist
        if hasattr(self, 'planted_crops'):
             for crop_pos_tuple, crops_obj in self.planted_crops.items():
                if crop_pos_tuple[0] == level:
                    _, r, c = crop_pos_tuple
                    if 0 <= r < self.grid_height and 0 <= c < self.grid_width:
                        symbol = '?' # Default crop symbol
                        if isinstance(crops_obj, list): # Multi-crop
                            if crops_obj:
                                 most_grown = max(crops_obj, key=lambda crop: crop.growth_progress)
                                 symbol = most_grown.get_growth_stage()
                        elif isinstance(crops_obj, Crop): # Single crop
                            symbol = crops_obj.get_growth_stage()

                        # Ensure crop doesn't overwrite portal/store/NPC (they take precedence)
                        if self.grid[level][r][c] == ' ':
                            self.grid[level][r][c] = symbol
                    else:
                        logging.warning(f"Crop position {crop_pos_tuple} out of bounds for level {level}.")

        # Place player if they are on this level and exist
        if hasattr(self, 'player') and hasattr(self, 'player_pos') and self.player_pos[0] == level:
            _, r, c = self.player_pos
            if 0 <= r < self.grid_height and 0 <= c < self.grid_width:
                 self.grid[level][r][c] = self.player.symbol
            else:
                logging.error(f"Player position {self.player_pos} out of bounds for level {level}!")


    # --- Initialization --- #
    def __init__(self):
        """Initialize the game"""
        # Load grid dimensions first as they are needed by populate_grid
        self.grid_width = int(get_env('GRID_WIDTH', 12))
        self.grid_height = int(get_env('GRID_HEIGHT', 12))
        self.grid_depth = int(get_env('GRID_DEPTH', 3))
        self.max_level = self.grid_depth - 1
        self.min_level = 0

        # Initialize grid structure needed by populate_grid
        self.grid = [[[' ' for _ in range(self.grid_width)] for _ in range(self.grid_height)] for _ in range(self.grid_depth)]

        # Game mode flags
        self.is_survival_mode = False

        # Initialize stats dictionaries
        self.farming_stats = {
            "crops_planted": 0, "crops_harvested": 0, "total_crop_value": 0,
            "farming_level": 1, "farming_exp": 0,
            "farming_exp_to_next": self.calculate_farming_exp_to_next(1) # Use helper
        }
        self.survival_stats = {
            "waves_completed": 0, "total_enemies_defeated": 0, "highest_wave_reached": 0,
            "best_completion_time": None, "total_rewards_earned": 0
        }
        self.game_stats = {
            "battles_won": 0, "battles_lost": 0, "monsters_killed": 0,
            "total_credits_earned": 0, "highest_level": 1, "portal_bosses_defeated": 0
        }
        self.battle_history = []

        # Initialize player object (needed by populate_grid)
        self.player = Player("Player", 100, 10, 5, 5)

        # Initialize position/object lists/dicts (needed by populate_grid)
        self.player_pos = [0, self.grid_height // 2, self.grid_width // 2] # Start near center
        self.portal_pos = None # Will be placed by place_portal
        self.npcs = [] # Will be placed by place_npcs
        self.store_pos = [] # Will be placed by place_stores
        self.planted_crops = {} # Crop dictionary

        # Call placement methods (these set the *.pos attributes)
        self.place_portal()
        self.place_npcs()
        self.place_stores() # Ensure stores are placed

        # Initialize Time and Weather Systems
        self.time_system = TimeSystem()
        self.weather = WeatherSystem()

        # Populate the starting grid (Level 0) data using the initialized positions
        self.populate_grid_for_level(0)

    # --- Placement Helpers (Called by __init__) --- #
    def place_portal(self):
        """Place the portal randomly on the current level."""
        # Needs self.player_pos to be set first
        level = self.player_pos[0]
        while True:
            row = random.randint(0, self.grid_height - 1)
            col = random.randint(0, self.grid_width - 1)
            pos = [level, row, col]
            # Ensure portal is not at the exact player start position
            if pos != self.player_pos:
                self.portal_pos = pos
                break

    def place_npcs(self):
        """Place NPCs randomly on the current level."""
        # Needs self.player_pos and self.portal_pos to be set
        self.npcs = []
        level = self.player_pos[0]
        num_npcs = random.randint(2, 4)
        for i in range(num_npcs):
            attempts = 0
            while attempts < 100:
                row = random.randint(0, self.grid_height - 1)
                col = random.randint(0, self.grid_width - 1)
                pos = [level, row, col]
                is_player = (pos == self.player_pos)
                is_portal = (self.portal_pos and pos == self.portal_pos)
                is_store = any(pos == store_p for store_p in self.store_pos) # Check stores too
                is_other_npc = any(pos == npc_p for npc_p, _ in self.npcs)

                if not is_player and not is_portal and not is_store and not is_other_npc:
                    npc = NPC.generate_random(level)
                    self.npcs.append((pos, npc))
                    break
                attempts += 1
            if attempts == 100:
                logging.warning(f"Could not place NPC {i + 1}/{num_npcs} on level {level} after 100 attempts.")

    def place_stores(self):
        """Place stores randomly on the current level (currently only level 0)."""
        # Needs self.player_pos and self.portal_pos
        level = 0 # Assuming stores only on level 0 for now
        self.store_pos = []
        num_stores = random.randint(1, 2)
        for i in range(num_stores):
            attempts = 0
            while attempts < 100:
                row = random.randint(0, self.grid_height - 1)
                col = random.randint(0, self.grid_width - 1)
                pos = [level, row, col]
                is_player = (pos == self.player_pos)
                is_portal = (self.portal_pos and pos == self.portal_pos)
                is_other_store = any(pos == store_p for store_p in self.store_pos)

                if not is_player and not is_portal and not is_other_store:
                    self.store_pos.append(pos)
                    break
                attempts += 1
            if attempts == 100:
                logging.warning(f"Could not place Store {i + 1}/{num_stores} on level {level} after 100 attempts.")

    # --- Gameplay Methods --- #
    def get_npc_at(self, level: int, row: int, col: int) -> Optional[NPC]:
        """Return the NPC object at the specified coordinates, or None if no NPC is there."""
        target_pos = [level, row, col]
        for npc_pos, npc_obj in self.npcs:
            if npc_pos == target_pos:
                return npc_obj
        return None

    def get_target_position(self, direction):
        """Calculate target position based on movement direction"""
        level, row, col = self.player_pos
        next_pos = list(self.player_pos) # Copy current position

        if direction == 'w': next_pos[1] = row - 1
        elif direction == 's': next_pos[1] = row + 1
        elif direction == 'a': next_pos[2] = col - 1
        elif direction == 'd': next_pos[2] = col + 1
        # Keep level the same for normal movement

        # Check bounds
        if not (0 <= next_pos[1] < self.grid_height and 0 <= next_pos[2] < self.grid_width):
            return None # Invalid move

        return next_pos

    def initialize_player(self, player_name: str, difficulty: str):
        """Initializes the player with a name and starting items based on difficulty."""
        self.player.name = player_name
        self.player.inventory = [] # Ensure inventory is clear first
        logging.info(f"Initializing player '{player_name}' with difficulty '{difficulty}'")

        if difficulty == "Easy":
            # More items for Easy
            for _ in range(5): self.player.add_to_inventory(SmallPotion())
            for _ in range(2): self.player.add_to_inventory(MediumPotion())
            for _ in range(2): self.player.add_to_inventory(RevivePotion())
        elif difficulty == "Medium":
            for _ in range(3): self.player.add_to_inventory(SmallPotion())
            self.player.add_to_inventory(MediumPotion())
            self.player.add_to_inventory(RevivePotion())
        elif difficulty == "Hard":
            self.player.add_to_inventory(SmallPotion())
        else: # Default to medium if difficulty string is unknown
             logging.warning(f"Unknown difficulty '{difficulty}'. Defaulting to Medium starting items.")
             for _ in range(3): self.player.add_to_inventory(SmallPotion())
             self.player.add_to_inventory(MediumPotion())
             self.player.add_to_inventory(RevivePotion())

    # --- Store --- #
    def get_store_inventory(self) -> List[Dict[str, Any]]:
         """Returns the list of items available in the store."""
         # Define items and their prices
         inventory = [
             {'item': SmallPotion(), 'price': 25},
             {'item': MediumPotion(), 'price': 60},
             {'item': LargePotion(), 'price': 150},
             {'item': EnergyPotion("Small Energy Potion", "Restores 20 Energy", 20), 'price': 30},
             {'item': EnergyPotion("Medium Energy Potion", "Restores 50 Energy", 50), 'price': 70},
             {'item': EnergyPotion("Large Energy Potion", "Restores 100 Energy", 100), 'price': 160},
             {'item': RevivePotion(), 'price': 300},
             {'item': Weapon("Iron Sword", "A basic sword", 10), 'price': 100},
             {'item': SickNote(), 'price': 500}
         ]
         # Convert item objects to dicts suitable for purchase_item
         store_data = []
         for entry in inventory:
             item_obj = entry['item']
             data = {
                 'name': item_obj.name,
                 'description': item_obj.description,
                 'price': entry['price'],
                 'class_name': item_obj.__class__.__name__,
                 'module_name': item_obj.__class__.__module__,
             }
             # Add specific attributes needed for reconstruction
             if hasattr(item_obj, 'attack'): data['attack'] = item_obj.attack
             if hasattr(item_obj, 'healing_amount'): data['healing_amount'] = item_obj.healing_amount
             if hasattr(item_obj, 'energy_restore'): data['energy_restore'] = item_obj.energy_restore
             # Add value if needed?
             store_data.append(data)
         return store_data

    def purchase_item(self, selected_item_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Handles the player attempting to purchase an item."""
        price = selected_item_data.get('price')
        item_class_name = selected_item_data.get('class_name')
        item_module_name = selected_item_data.get('module_name')
        item_name = selected_item_data.get('name', 'Unknown Item')

        logging.info(f"Attempting purchase: Item='{item_name}', Price={price}, PlayerCredits={self.player.credits}")

        if price is None or item_class_name is None or item_module_name is None:
            logging.error(f"Purchase failed: Invalid item data received: {selected_item_data}")
            return False, "Invalid item data."

        if self.player.credits >= price:
            try:
                module = importlib.import_module(item_module_name)
                item_class = getattr(module, item_class_name)

                item_args = {
                    'name': selected_item_data.get('name'),
                    'description': selected_item_data.get('description', 'No description')
                }
                if item_class_name == 'Weapon': item_args['attack'] = selected_item_data.get('attack', 0)
                elif item_class_name == 'Potion': item_args['healing_amount'] = selected_item_data.get('healing_amount', 0)
                elif item_class_name == 'EnergyPotion': item_args['energy_restore'] = selected_item_data.get('energy_restore', 0)
                # Add elifs for RevivePotion, SickNote if they need args (RevivePotion(), SickNote() are likely fine)

                new_item = item_class(**item_args)

                self.player.credits -= price
                self.player.add_to_inventory(new_item)
                logging.info(f"Purchase successful: Item='{new_item.name}', Cost={price}, NewCredits={self.player.credits}")
                print(f"Player Purchased {new_item.name} for {price} credits.")
                return True, f"Purchased {new_item.name}!"
            except (ImportError, AttributeError, TypeError) as e:
                logging.exception(f"Purchase failed: Error creating item instance for {item_class_name} from {item_module_name}. Data: {selected_item_data}")
                return False, f"Error purchasing item: {e}"
        else:
            logging.warning(f"Purchase failed: Not enough credits. Item='{item_name}', Price={price}")
            return False, "Not enough credits."

    # --- Farming --- #
    def get_farming_level_requirement(self, feature):
         """Get the farming level required for a feature"""
         requirements = { "multi_planting": 3 }
         return requirements.get(feature, 1)

    def calculate_farming_exp_to_next(self, level):
        """Calculate experience needed for next farming level"""
        return int(100 * (1.5 ** (level - 1)))

    def add_farming_exp(self, exp_gained):
        """Add farming experience and handle level ups"""
        self.farming_stats["farming_exp"] += exp_gained
        leveled_up = False
        level_up_message = ""
        while self.farming_stats["farming_exp"] >= self.farming_stats["farming_exp_to_next"]:
            leveled_up = True
            self.farming_stats["farming_level"] += 1
            self.farming_stats["farming_exp"] -= self.farming_stats["farming_exp_to_next"]
            self.farming_stats["farming_exp_to_next"] = self.calculate_farming_exp_to_next(
                self.farming_stats["farming_level"])
            level_up_message = f"🌟 Farming level up! Now level {self.farming_stats['farming_level']}"
        return level_up_message if leveled_up else None # Return message only on level up

    def plant_crop(self, crop: Crop, position: list) -> Tuple[bool, str]:
        """Plant a crop at the specified position"""
        level, row, col = position
        seed_cost = crop.value // 2  # Simple seed cost calculation

        if self.player.credits < seed_cost:
            return False, f"Not enough credits (need {seed_cost})"

        if not (0 <= level < self.grid_depth and 0 <= row < self.grid_height and 0 <= col < self.grid_width):
            return False, "Position is out of bounds"

        pos_tuple = tuple(position)
        can_multi_plant = self.farming_stats["farming_level"] >= self.get_farming_level_requirement("multi_planting")
        existing_crops = self.planted_crops.get(pos_tuple)

        if existing_crops:
            if not can_multi_plant:
                return False, f"Cannot plant multiple crops in one tile (requires farming level {self.get_farming_level_requirement('multi_planting')})"
            if isinstance(existing_crops, list) and len(existing_crops) >= 2:
                return False, "Maximum 2 crops per tile allowed"
            if not isinstance(existing_crops, list) and len([existing_crops]) >= 2:  # Should not happen if logic correct
                return False, "Maximum 2 crops per tile allowed (logic error check)"

        # Only allow planting on empty grid cells (' ')
        if self.grid[level][row][col] != ' ':
            return False, "Position is not empty ground"

        crop.planted_time = self.time_system.current_time
        crop.growth_progress = 0.0

        if pos_tuple in self.planted_crops:
            if isinstance(self.planted_crops[pos_tuple], list):
                self.planted_crops[pos_tuple].append(crop)
            else:  # Convert single crop to list
                self.planted_crops[pos_tuple] = [self.planted_crops[pos_tuple], crop]
        else:
            self.planted_crops[pos_tuple] = crop  # Store single crop initially

        self.grid[level][row][col] = '🌱'  # Update grid visually
        self.player.credits -= seed_cost
        self.farming_stats["crops_planted"] += 1
        level_up_message = self.add_farming_exp(10)

        message = f"Crop planted successfully! Cost: {seed_cost} credits."
        if level_up_message:
            message += f" {level_up_message}"
        return True, message

    def harvest_crop(self, position_tuple: tuple) -> Tuple[int, List[str], Optional[str]]:
        """Harvest crop(s) at the specified position tuple."""
        if position_tuple not in self.planted_crops:
            return 0, [], None  # No crop here

        crops_at_pos = self.planted_crops[position_tuple]
        total_value = 0
        harvested_names = []
        level_up_message = None
        exp_gained = 0
        crops_remaining = []

        if isinstance(crops_at_pos, list):
            for crop in crops_at_pos:
                if crop.growth_progress >= 1.0:
                    total_value += crop.value
                    harvested_names.append(crop.name)
                    exp_gained += 25  # Exp per harvested crop
                else:
                    crops_remaining.append(crop)  # Keep unripe crops
            if crops_remaining:
                self.planted_crops[position_tuple] = crops_remaining  # Update list
            else:
                del self.planted_crops[position_tuple]  # Remove if all harvested
        elif isinstance(crops_at_pos, Crop):  # Single crop case
            if crops_at_pos.growth_progress >= 1.0:
                total_value += crops_at_pos.value
                harvested_names.append(crops_at_pos.name)
                exp_gained += 25
                del self.planted_crops[position_tuple]  # Remove harvested crop
            # else: leave the unripe single crop

        if total_value > 0:
            self.player.credits += total_value
            self.farming_stats["crops_harvested"] += len(harvested_names)
            self.farming_stats["total_crop_value"] += total_value
            level_up_message = self.add_farming_exp(exp_gained)
            # Clear grid cell only if the key was deleted (no remaining crops)
            if position_tuple not in self.planted_crops:
                level, row, col = position_tuple
                self.grid[level][row][col] = ' '  # Clear visually

        return total_value, harvested_names, level_up_message

    def get_crop_info(self, position: list) -> Optional[str]:
        """Get status string for crop(s) at the given position list."""
        pos_tuple = tuple(position)
        if pos_tuple in self.planted_crops:
            crops = self.planted_crops[pos_tuple]
            if isinstance(crops, list):
                infos = []
                for crop in crops:
                    prog = int(crop.growth_progress * 100)
                    stage = crop.get_growth_stage()
                    infos.append(f"{crop.name} {stage} ({prog}%)")
                return " + ".join(infos)
            elif isinstance(crops, Crop):
                prog = int(crops.growth_progress * 100)
                stage = crops.get_growth_stage()
                return f"{crops.name} {stage} ({prog}%)"
        return None

    def update_crops(self):
        """Update growth progress of all planted crops based on time."""
        time_delta_hours = self.time_system.get_time_delta_in_hours()
        logging.info(f"[update_crops] Time delta: {time_delta_hours:.2f} hours. Current time: {self.time_system.current_time.strftime('%I:%M %p')}")
        
        if time_delta_hours == 0: 
            logging.debug("[update_crops] No time passed, skipping crop updates")
            return # No update needed if no time passed

        weather_multiplier = self.weather.get_crop_growth_multiplier()
        logging.info(f"[update_crops] Weather multiplier: {weather_multiplier}")
        
        crop_count = 0
        updated_count = 0
        positions_to_clear = []

        for pos, crop_obj_or_list in list(self.planted_crops.items()): # Iterate on copy
            level, row, col = pos
            updated_crops = [] # For multi-crop tiles

            if isinstance(crop_obj_or_list, list):
                crop_count += len(crop_obj_or_list)
                for crop in crop_obj_or_list:
                    old_progress = crop.growth_progress
                    if crop.growth_progress < 1.0:
                        # Calculate growth increment
                        growth_increment = (time_delta_hours / crop.growth_time) * weather_multiplier
                        crop.growth_progress = min(1.0, crop.growth_progress + growth_increment)
                        if old_progress != crop.growth_progress:
                            updated_count += 1
                            logging.debug(f"[update_crops] Crop at {pos} ({crop.name}) grew: {old_progress:.2f} -> {crop.growth_progress:.2f}")
                    updated_crops.append(crop) # Keep the crop (updated or already mature)
                self.planted_crops[pos] = updated_crops # Update the list
                # Update grid symbol based on the most grown crop in the list
                if updated_crops:
                    most_grown = max(updated_crops, key=lambda c: c.growth_progress)
                    old_symbol = self.grid[level][row][col]
                    new_symbol = most_grown.get_growth_stage()
                    self.grid[level][row][col] = new_symbol
                    if old_symbol != new_symbol:
                        logging.info(f"[update_crops] Crop visual at {pos} changed: {old_symbol} -> {new_symbol}")
                else: # Should not happen if logic is right, but defensively clear
                    positions_to_clear.append(pos)
            elif isinstance(crop_obj_or_list, Crop):
                crop_count += 1
                crop = crop_obj_or_list
                old_progress = crop.growth_progress
                if crop.growth_progress < 1.0:
                    growth_increment = (time_delta_hours / crop.growth_time) * weather_multiplier
                    crop.growth_progress = min(1.0, crop.growth_progress + growth_increment)
                    if old_progress != crop.growth_progress:
                        updated_count += 1
                        logging.debug(f"[update_crops] Crop at {pos} ({crop.name}) grew: {old_progress:.2f} -> {crop.growth_progress:.2f}")
                # Update grid symbol directly for single crop
                old_symbol = self.grid[level][row][col]
                new_symbol = crop.get_growth_stage()
                self.grid[level][row][col] = new_symbol
                if old_symbol != new_symbol:
                    logging.info(f"[update_crops] Crop visual at {pos} changed: {old_symbol} -> {new_symbol}")
            else: # Should not happen
                logging.warning(f"Invalid crop data type at {pos}: {type(crop_obj_or_list)}")
                positions_to_clear.append(pos) # Mark for removal if invalid data found

        # Clear grid for positions where all crops were removed (e.g., invalid data)
        for pos in positions_to_clear:
            if pos in self.planted_crops: # Check if not already removed by harvest
                del self.planted_crops[pos]
            level, row, col = pos
            self.grid[level][row][col] = ' '
            
        logging.info(f"[update_crops] Updated {updated_count}/{crop_count} crops")

    # --- Save/Load --- #
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire game state to a dictionary for saving."""
        metadata = {
            'save_time': datetime.now().isoformat(),
            'player_name': self.player.name,
            'player_level': self.player.level if hasattr(self.player, 'level') else 1,
        }
        npcs_data = [{'position': pos, 'npc_data': npc.to_dict()} for pos, npc in self.npcs]
        
        # --- New Crop Saving Format --- #
        saved_crops_list = []
        for pos_tuple, crop_obj_or_list in self.planted_crops.items():
             crop_entry = {"position": list(pos_tuple)}
             if isinstance(crop_obj_or_list, list):
                 crop_entry["crops"] = [c.to_dict() for c in crop_obj_or_list]
             else: # Single crop
                 crop_entry["crops"] = [crop_obj_or_list.to_dict()] # Store as list even if single
             saved_crops_list.append(crop_entry)
        # --- End New Crop Saving Format --- #

        state = {
            '__metadata__': metadata,
            'grid_width': self.grid_width, 'grid_height': self.grid_height, 'grid_depth': self.grid_depth,
            'player_pos': self.player_pos, 'portal_pos': self.portal_pos, 'store_pos': self.store_pos,
            'player': self.player.to_dict(),
            'npcs': npcs_data,
            'planted_crops': saved_crops_list,
            'time_system': self.time_system.to_dict(),
            'weather': self.weather.to_dict(),
            'is_survival_mode': self.is_survival_mode,
            'farming_stats': self.farming_stats,
            'survival_stats': self.survival_stats,
            'game_stats': self.game_stats,
            'battle_history': self.battle_history,
        }
        return state

    def save_game(self, slot: int) -> bool:
        """Save the current game state to a specific slot."""
        try:
            filename = GridGame.get_save_filename(slot)
            save_data = self.to_dict()
            filepath = Path(filename)
            with filepath.open('w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4)
            logging.info(f"Game saved successfully to {filename}")
            return True
        except Exception as e:
            logging.exception(f"Error saving game to slot {slot}")
            return False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GridGame':
        """Create a GridGame instance from a dictionary (loaded from JSON)."""
        game = cls() # Calls __init__ to set defaults and structure

        # Load simple attributes, overwriting __init__ defaults
        game.grid_width = data.get('grid_width', game.grid_width)
        game.grid_height = data.get('grid_height', game.grid_height)
        game.grid_depth = data.get('grid_depth', game.grid_depth)
        game.max_level = game.grid_depth - 1
        game.is_survival_mode = data.get('is_survival_mode', False)
        game.farming_stats = data.get('farming_stats', game.farming_stats)
        game.survival_stats = data.get('survival_stats', game.survival_stats)
        game.game_stats = data.get('game_stats', game.game_stats)
        game.player_pos = data.get('player_pos', game.player_pos)
        game.portal_pos = data.get('portal_pos', None)
        game.store_pos = data.get('store_pos', [])
        game.battle_history = data.get('battle_history', [])

        player_data = data.get('player')
        if player_data: game.player = Player.from_dict(player_data)
        else: logging.warning("Player data missing in save file.")

        time_data = data.get('time_system')
        if time_data: game.time_system = TimeSystem.from_dict(time_data)

        weather_data = data.get('weather')
        if weather_data: game.weather = WeatherSystem.from_dict(weather_data)
        
        # Load NPCs
        game.npcs = []
        npc_data_list = data.get('npcs', [])
        for npc_entry in npc_data_list:
            try:
                if isinstance(npc_entry, dict) and 'position' in npc_entry and 'npc_data' in npc_entry:
                    pos = npc_entry['position']
                    npc_data = npc_entry['npc_data']
                    npc_obj = NPC.from_dict(npc_data)
                    game.npcs.append((pos, npc_obj))
            except Exception as e:
                logging.warning(f"Skipping invalid NPC entry format in save file: {npc_entry}")

        # Load Crops (keys are JSON strings representing lists)
        game.planted_crops = {}
        saved_crops_list = data.get('planted_crops', [])
        if isinstance(saved_crops_list, list): # Check if it's the new list format
            for crop_entry in saved_crops_list:
                try:
                    pos_list = crop_entry.get('position')
                    crop_data_list = crop_entry.get('crops', [])
                    if not pos_list or not isinstance(pos_list, list) or len(pos_list) != 3:
                        logging.warning(f"Skipping invalid crop entry position in save file: {crop_entry}")
                        continue

                    pos_tuple = tuple(pos_list)
                    loaded_crops = []
                    for crop_data in crop_data_list:
                        try:
                            crop_obj = Crop.from_dict(crop_data)
                            loaded_crops.append(crop_obj)
                        except Exception as e_inner:
                            logging.error(f"Error instantiating crop object from data {crop_data} at pos {pos_tuple}: {e_inner}")
                    
                    if loaded_crops: # Only add if crops were successfully loaded
                        game.planted_crops[pos_tuple] = loaded_crops[0] if len(loaded_crops) == 1 else loaded_crops
                except Exception as e:
                    logging.error(f"Error processing crop entry {crop_entry}: {e}")
        elif isinstance(saved_crops_list, dict): # Handle old dictionary format (attempt basic compatibility? or just warn)
            logging.warning("Loading old save format for crops. Errors may occur. Please re-save the game.")
            # (Optional: Could add code here to attempt loading the old format)

        # NOTE: self.grid is NOT loaded here, it will be populated by load_game after this returns.
        return game

    @staticmethod
    def load_game(slot: int) -> Optional['GridGame']:
        """Load game state from a specific slot."""
        filename = GridGame.get_save_filename(slot)
        filepath = Path(filename)
        if not filepath.exists():
            logging.warning(f"No save file found for slot {slot} ({filename})")
            return None
        try:
            with filepath.open('r', encoding='utf-8') as f:
                save_data = json.load(f)
            logging.info(f"Loading game from {filename}...")
            game_instance = GridGame.from_dict(save_data)

            if game_instance:
                # --- Populate grid AFTER loading all state ---
                logging.info(f"Populating grid for loaded level {game_instance.player_pos[0]}")
                game_instance.populate_grid_for_level(game_instance.player_pos[0])
            else:
                logging.error("Failed to create game instance from loaded data.")

            return game_instance
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding save file {filename}: {e}")
            return None
        except Exception as e:
            logging.exception(f"Unexpected error loading game from slot {slot}")
            return None

    # --- Save Slot Management Helpers --- #
    @staticmethod
    def get_save_filename(slot: int) -> str:
        """Get the filename for a specific save slot."""
        if not 1 <= slot <= 5: raise ValueError("Save slot must be between 1 and 5.")
        return f"savegame_{slot}.json"

    @staticmethod
    def get_save_metadata(slot: int) -> Optional[Dict[str, Any]]:
        """Read metadata from a specific save slot file without loading the whole game."""
        try:
            filename = GridGame.get_save_filename(slot)
            filepath = Path(filename)
            if not filepath.exists(): return None
            with filepath.open('r', encoding='utf-8') as f:
                save_data = json.load(f)
                metadata = save_data.get('__metadata__')
                if metadata:
                    metadata['slot'] = slot
                    metadata['last_modified'] = filepath.stat().st_mtime
                    return metadata
                else: # Handle older saves without metadata?
                    return {'slot': slot, 'player_name': 'Unknown', 'save_time': None, 'last_modified': filepath.stat().st_mtime}
        except (json.JSONDecodeError, ValueError, OSError, KeyError) as e:
            logging.warning(f"Error reading metadata for slot {slot} ({filename}): {e}")
            return {'slot': slot, 'player_name': '[Read Error]', 'save_time': None, 'last_modified': None}

    @staticmethod
    def get_all_save_metadata() -> List[Optional[Dict[str, Any]]]:
        """Get metadata for all 5 save slots."""
        return [GridGame.get_save_metadata(slot) for slot in range(1, 6)]

    @staticmethod
    def find_most_recent_save_slot() -> Optional[int]:
        """Find the slot number of the most recently modified save file."""
        all_metadata = GridGame.get_all_save_metadata()
        valid_saves = [m for m in all_metadata if m and m.get('last_modified') is not None]
        if not valid_saves: return None
        valid_saves.sort(key=lambda m: m['last_modified'], reverse=True)
        return valid_saves[0]['slot']

    # --- Other Helpers --- #
    def check_win_condition(self):
        # Define win condition, e.g., reach max level and defeat a boss
        pass

    # --- Player Actions ---
    def move_player(self, dx, dy):
        # ... existing move_player code ...
        pass

    def record_battle(self, npc_name, player_won, turns, credits_gained, dropped_items):
        """Records the outcome of a battle."""
        record = {
            "npc_name": npc_name,
            "player_won": player_won,
            "turns": turns,
            "credits_gained": credits_gained,
            "items_gained": dropped_items,
            "timestamp": datetime.now().isoformat()
        }
        self.battle_history.append(record)
        # Keep only the last N records if desired
        # max_history = 10
        # if len(self.battle_history) > max_history:
        #     self.battle_history = self.battle_history[-max_history:]

        # Update game stats
        if player_won:
            self.game_stats["battles_won"] += 1
            self.game_stats["total_credits_earned"] += credits_gained
            self.game_stats["monsters_killed"] += 1
            if self.player_pos[0] > self.game_stats["highest_level"]:
                self.game_stats["highest_level"] = self.player_pos[0]
            if self.player_pos[0] == self.max_level:
                self.game_stats["portal_bosses_defeated"] += 1
        else:
            self.game_stats["battles_lost"] += 1

    # --- Game State ---
    def get_current_level_grid(self):
        # ... existing get_current_level_grid code ...
        pass

    # --- ADDED: Find empty spot for respawn --- #
    def find_random_empty_spot(self, level):
        """Finds a random empty (' ') coordinate [level, r, c] on the specified level."""
        if not (0 <= level < len(self.grid)):
            logging.error(f"find_random_empty_spot: Invalid level {level}")
            return None # Or raise an error

        attempts = 0
        max_attempts = self.grid_height * self.grid_width * 2 # Generous attempt limit

        while attempts < max_attempts:
            r = random.randint(0, self.grid_height - 1)
            c = random.randint(0, self.grid_width - 1)
            pos = [level, r, c]

            # Check if the spot is empty in the grid
            if self.grid[level][r][c] == ' ':
                # Double check it's not player/portal/store/npc positions (in case grid is stale)
                is_player = (pos == self.player_pos)
                is_portal = (self.portal_pos and pos == self.portal_pos)
                is_store = any(pos == store_p for store_p in self.store_pos)
                is_npc = any(pos == npc_p for npc_p, _ in self.npcs)
                is_crop = any(pos == list(crop_p) for crop_p in self.planted_crops.keys() if crop_p[0] == level)

                if not is_player and not is_portal and not is_store and not is_npc and not is_crop:
                    logging.debug(f"find_random_empty_spot: Found empty spot at {pos}")
                    return pos
            
            attempts += 1

        logging.warning(f"find_random_empty_spot: Could not find empty spot on level {level} after {max_attempts} attempts.")
        return None # Indicate failure
    # --- END find_random_empty_spot --- #

    def _initialize_grid(self):
        """Initializes the grid structure for all levels."""

# --- End of GridGame Class --- #

