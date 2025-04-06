from .character import Character
from items.potion import Potion
from items.revive_potion import RevivePotion
import time


class Player(Character):
    def __init__(self, name, health=100, attack=10, defense=5, agility=5):
        super().__init__(name, health, attack, defense, agility, symbol='@')
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        self.credits = 1000  # Start with 1000 credits
        self.inventory = []
        self.weapon = None
        self.max_energy = 50
        self.energy = 50
        self.level_keys = []
        self.battle_history = []
        self.items_used = []
        self.highest_level = 1
        
        # Initialize player statistics tracking
        self.stats = {
            "battles_won": 0,
            "battles_lost": 0,
            "items_used": 0,
            "distance_traveled": 0,
            "enemies_defeated": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "critical_hits": 0,
            "gold_earned": 0,
            "gold_spent": 0,
            "levels_gained": 0,
            "potions_used": 0,
            "weapons_found": 0,
            "death_count": 0,
            "play_time": 0,  # in seconds
        }
        self.start_time = time.time()

        # Remove starter items - they will be added based on difficulty selection
        # self.add_to_inventory(Potion("Small Potion", "Restores 20 HP", 20))
        # self.add_to_inventory(Potion("Small Potion", "Restores 20 HP", 20))
        # self.add_to_inventory(RevivePotion())

    def add_experience(self, amount):
        """Add experience points and handle level ups"""
        self.experience += amount
        self.increment_stat("experience_gained", amount)

        # Handle multiple level ups
        levels_gained = 0
        while self.experience >= self.experience_to_next_level:
            self.experience -= self.experience_to_next_level
            self.level_up()
            levels_gained += 1
            # Update experience needed for next level
            self.experience_to_next_level = self.level * 100
        
        if levels_gained > 0:
            self.increment_stat("levels_gained", levels_gained)

    def level_up(self):
        """Increase stats when leveling up"""
        self.level += 1
        self.max_health += 20
        self.health = self.max_health  # Heal to full on level up
        self.attack += 5
        self.defense += 3
        self.agility += 2
        self.max_energy += 10
        self.energy = self.max_energy  # Restore energy on level up
        
        # Update highest level reached
        if self.level > self.highest_level:
            self.highest_level = self.level

    def add_to_inventory(self, item):
        self.inventory.append(item)
        
        # Track weapon finds
        if hasattr(item, 'attack'):
            self.increment_stat("weapons_found")

    def remove_from_inventory(self, item):
        if item in self.inventory:
            self.inventory.remove(item)

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        self.increment_stat("damage_taken", actual_damage)
        
        # Track death if health reaches 0
        if self.health <= 0:
            self.increment_stat("death_count")
            
        return actual_damage

    def get_total_attack(self):
        weapon_attack = self.weapon.attack if self.weapon else 0
        return self.attack + weapon_attack

    def has_key_for_level(self, level):
        return level in self.level_keys

    def add_level_key(self, level):
        if level not in self.level_keys:
            self.level_keys.append(level)
            self.level_keys.sort()  # Keep keys sorted for display

    def record_battle(self, opponent_name, result, damage_dealt, damage_taken):
        battle_record = {
            'opponent': opponent_name,
            'result': result,
            'damage_dealt': damage_dealt,
            'damage_taken': damage_taken,
            'player_level': self.level
        }
        self.battle_history.append(battle_record)
        
        # Update battle statistics
        if result == "Victory":
            self.increment_stat("battles_won")
            self.increment_stat("enemies_defeated")
        elif result == "Defeat":
            self.increment_stat("battles_lost")
        
        self.increment_stat("damage_dealt", damage_dealt)

    def record_item_use(self, item_name):
        self.items_used.append(item_name)
        self.increment_stat("items_used")
        
        # Track potion usage specifically
        if "potion" in item_name.lower():
            self.increment_stat("potions_used")
    
    # Player statistics tracking methods
    
    def increment_stat(self, stat_name, amount=1):
        """Increment a player statistic by the specified amount"""
        if stat_name in self.stats:
            self.stats[stat_name] += amount
        else:
            # Create the stat if it doesn't exist
            self.stats[stat_name] = amount
    
    def get_stat(self, stat_name):
        """Get the value of a player statistic"""
        return self.stats.get(stat_name, 0)
    
    def reset_stats(self):
        """Reset all player statistics to zero"""
        for stat in self.stats:
            self.stats[stat] = 0
        self.start_time = time.time()
    
    def update_play_time(self, seconds=None):
        """Update the tracked play time"""
        if seconds is not None:
            # Add specified seconds (for testing)
            self.stats["play_time"] += seconds
        else:
            # Calculate elapsed time since start_time
            current_time = time.time()
            elapsed = int(current_time - self.start_time)
            self.stats["play_time"] = elapsed
            self.start_time = current_time  # Reset start time for next update
    
    def format_time(self, seconds):
        """Format seconds as HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_stats_summary(self, update_time=True):
        """Get a formatted summary of player statistics"""
        # Update play time before generating summary
        if update_time:
            self.update_play_time()
        
        # Format the summary
        summary = f"--- {self.name}'s Statistics ---\n"
        
        # Include the most interesting stats first
        key_stats = [
            "battles_won", "battles_lost", "enemies_defeated", 
            "damage_dealt", "damage_taken", "items_used",
            "gold_earned", "gold_spent", "levels_gained", 
            "critical_hits", "death_count"
        ]
        
        for stat in key_stats:
            if stat in self.stats:
                summary += f"{stat}: {self.stats[stat]}\n"
        
        # Format play time specially
        play_time = self.format_time(self.stats["play_time"])
        summary += f"play_time: {play_time}\n"
        
        # Include any other stats not in key_stats
        for stat, value in self.stats.items():
            if stat not in key_stats and stat != "play_time":
                summary += f"{stat}: {value}\n"
        
        return summary

    # Serialization
    def to_dict(self):
        """Convert Player state to dictionary."""
        # Ensure play time is up-to-date before saving
        self.update_play_time()

        data = super().to_dict() # Get base Character data
        data.update({
            'player_class': self.__class__.__name__, # Identify as Player
            'level': self.level,
            'experience': self.experience,
            'experience_to_next_level': self.experience_to_next_level,
            'battle_history': self.battle_history, # Assuming battle history is JSON-serializable
            'items_used': self.items_used, # Assuming this list is simple strings
            'highest_level': self.highest_level,
            'stats': self.stats, # Contains play_time
            # Note: start_time is not directly serializable, play_time is saved in stats
        })
        # Ensure inventory and weapon are handled correctly (using their to_dict)
        data['inventory'] = [item.to_dict() for item in self.inventory if hasattr(item, 'to_dict')]
        data['weapon'] = self.weapon.to_dict() if self.weapon and hasattr(self.weapon, 'to_dict') else None
        return data

    @classmethod
    def from_dict(cls, data):
        """Create a Player instance from dictionary data."""
        player = cls(name=data['name']) # Basic init with name

        # Populate attributes from Character base
        player.health = data['health']
        player.max_health = data['max_health']
        player.attack = data['attack']
        player.defense = data['defense']
        player.agility = data['agility']
        player.symbol = data.get('symbol', '@') # Use default if missing
        player.credits = data['credits']
        player.energy = data['energy']
        player.max_energy = data['max_energy']
        player.level_keys = data.get('level_keys', [])

        # Populate Player specific attributes
        player.level = data['level']
        player.experience = data['experience']
        player.experience_to_next_level = data['experience_to_next_level']
        player.battle_history = data.get('battle_history', [])
        player.items_used = data.get('items_used', [])
        player.highest_level = data.get('highest_level', 1)
        player.stats = data.get('stats', {}) # Load stats dictionary

        # Deserialize weapon and inventory using ItemFactory
        from items.item_factory import ItemFactory # Import here

        if data.get('weapon'):
            try:
                player.weapon = ItemFactory.create_item(data['weapon'])
            except (ValueError, NotImplementedError, TypeError) as e:
                print(f"Warning: Could not load weapon: {e}")
                player.weapon = None

        player.inventory = []
        if data.get('inventory'):
            for item_data in data['inventory']:
                try:
                    item = ItemFactory.create_item(item_data)
                    player.inventory.append(item)
                except (ValueError, NotImplementedError, TypeError) as e:
                    print(f"Warning: Could not load item {item_data.get('name')}: {e}")

        # Handle play time (load directly if saved, otherwise reset start_time)
        if 'play_time' in player.stats:
            player.start_time = time.time() # Reset start time, play_time is the source of truth
        else:
             player.stats['play_time'] = 0
             player.start_time = time.time()

        return player
