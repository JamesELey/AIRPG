from .character import Character
import random
import logging


class NPC(Character):
    def __init__(self, name, health, attack, defense, agility, level=1, is_boss=False):
        super().__init__(name, health, attack, defense, agility, symbol='E')
        self.level = level
        self.is_boss = is_boss
        self.drops = []  # Items that can be dropped when defeated
        self.inventory = []
        self.weapon = None
        self.credits = random.randint(
            50, 200) * level  # Credits scale with level

    @classmethod
    def generate_random(cls, level=1, is_boss=False):
        """Generate a random NPC with stats appropriate for the given level"""
        # --- Ensure minimum level is 1 ---
        actual_level = max(1, level)
        # ---------------------------------

        # Base stats
        base_health = random.randint(60, 90)
        base_attack = random.randint(8, 15)
        base_defense = random.randint(5, 8)
        base_agility = random.randint(5, 8)

        # Level multiplier (15% increase per level)
        # Use actual_level for calculation
        level_multiplier = 1 + (0.15 * (actual_level - 1))

        # Apply multiplier to stats
        health = int(base_health * level_multiplier)
        attack = int(base_attack * level_multiplier)
        defense = int(base_defense * level_multiplier)
        agility = int(base_agility * level_multiplier)

        # Apply boss multiplier if this is a boss
        if is_boss:
            health = int(health * 2)
            attack = int(attack * 2)
            defense = int(defense * 2)
            agility = int(agility * 2)

        # Generate name
        adjectives = ['Fierce', 'Mighty', 'Swift',
                      'Cunning', 'Ancient', 'Dark', 'Wild']
        types = ['Warrior', 'Hunter', 'Rogue', 'Brute', 'Knight', 'Guard']
        prefix = "Boss" if is_boss else "Level"
        # Use actual_level in the name
        name = f"{prefix} {actual_level} {random.choice(adjectives)} {random.choice(types)}"

        # Create instance without drops/inventory initially
        # Pass actual_level to the constructor
        npc = cls(name, health, attack, defense, agility, actual_level, is_boss)
        
        # Add default drops based on level/type?
        # npc.add_drop(Item(...), drop_chance=0.1)
        
        # Give a random weapon based on level?
        # if random.random() < 0.5: # 50% chance to have a weapon
        #    npc.weapon = Weapon.create_level_weapon(level)

        return npc

    def add_to_inventory(self, item):
        """Add an item to the NPC's inventory"""
        self.inventory.append(item)

    def remove_from_inventory(self, item):
        if item in self.inventory:
            self.inventory.remove(item)

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage

    def get_total_attack(self):
        weapon_attack = self.weapon.attack if self.weapon else 0
        return self.attack + weapon_attack

    def add_drop(self, item, drop_chance):
        """Add an item that can be dropped when the NPC is defeated"""
        self.drops.append((item, drop_chance))

    def get_drops(self):
        """Return a list of items that were successfully rolled for dropping"""
        dropped_items = []
        for item, chance in self.drops:
            if random.random() < chance:
                dropped_items.append(item)
        return dropped_items

    def get_experience_value(self):
        """Calculate experience value when defeated"""
        # Base experience value based on stats and level
        base_exp = (
            self.max_health * 0.2 +  # Health contribution
            self.attack * 2 +        # Attack contribution
            self.defense * 2 +       # Defense contribution
            self.agility * 1         # Agility contribution
        )

        # Scale with level
        base_exp *= (1 + (self.level - 1) * 0.1)  # 10% increase per level

        # Ensure minimum experience
        base_exp = max(20 * self.level, base_exp)

        # Bonus for boss NPCs
        if self.is_boss:
            base_exp *= 2  # Double experience for bosses

        return int(base_exp)  # Return as integer

    def get_credit_value(self):
        """Calculate credits granted when defeated"""
        base_credits = 10 * self.level
        if self.is_boss:
            base_credits *= 2
        # --- Ensure minimum 1 credit --- #
        return max(1, base_credits)
        # ----------------------------- #

    def to_dict(self):
        """Convert NPC to dictionary for saving"""
        data = super().to_dict() # Get base Character data
        data.update({
            'npc_class': self.__class__.__name__, # Identify as NPC
            'level': self.level,
            'is_boss': self.is_boss,
            # 'drops': [item.to_dict() for item, chance in self.drops], # Drops might need custom handling
            # Drops serialization needs thought: just save item data + chance?
        })
        # Ensure inventory and weapon are handled correctly (using their to_dict)
        data['inventory'] = [item.to_dict() for item in self.inventory if hasattr(item, 'to_dict')]
        data['weapon'] = self.weapon.to_dict() if self.weapon and hasattr(self.weapon, 'to_dict') else None
        return data

    @classmethod
    def from_dict(cls, data):
        """Create NPC from dictionary data"""
        # --- Ensure minimum level 1 even from save --- #
        loaded_level = data.get('level', 1) # Default level if missing
        actual_level = max(1, loaded_level)
        # ------------------------------------------ #

        npc = cls(
            name=data['name'],
            health=data['health'],
            attack=data['attack'],
            defense=data['defense'],
            agility=data['agility'],
            # Use actual_level here
            level=actual_level,
            is_boss=data.get('is_boss', False) # Default boss status
        )

        # Populate remaining Character attributes
        npc.max_health = data['max_health']
        npc.symbol = data.get('symbol', 'E') # Default symbol
        npc.credits = data.get('credits', 0)
        npc.energy = data.get('energy', 0)
        npc.max_energy = data.get('max_energy', 0)
        npc.level_keys = data.get('level_keys', [])

        # Deserialize weapon and inventory using ItemFactory
        from items.item_factory import ItemFactory # Import here

        if data.get('weapon'):
            try:
                npc.weapon = ItemFactory.create_item(data['weapon'])
            except (ValueError, NotImplementedError, TypeError) as e:
                print(f"Warning: Could not load NPC weapon: {e}")
                npc.weapon = None

        npc.inventory = []
        if data.get('inventory'):
            for item_data in data['inventory']:
                try:
                    item = ItemFactory.create_item(item_data)
                    npc.inventory.append(item)
                except (ValueError, NotImplementedError, TypeError) as e:
                    print(f"Warning: Could not load NPC item {item_data.get('name')}: {e}")

        # Deserialize drops (if saved)
        # npc.drops = []
        # if data.get('drops'):
        #     for drop_data in data['drops']:
        #         # Recreate item and pair with chance (needs drop saving format)
        #         pass

        return npc

    def respawn(self):
        """Respawn the NPC with full health, 10% more max_hp, and +1 to a random stat"""
        # --- CORRECTION: Increase max_hp by 10% --- #
        original_max_hp = self.max_health
        self.max_health = round(self.max_health * 1.10)
        logging.debug(f"NPC '{self.name}' respawn: max_hp increased from {original_max_hp} to {self.max_health}")
        # ------------------------------------------ #

        # Restore full health (to the new max_hp)
        self.health = self.max_health

        # Randomly increase one stat by 1
        stats = ['attack', 'defense', 'agility']
        increased_stat = random.choice(stats)
        setattr(self, increased_stat, getattr(self, increased_stat) + 1)
        logging.debug(f"NPC '{self.name}' respawn: Increased stat '{increased_stat}'")

        return increased_stat
