class Character:
    def __init__(self, name, health, attack, defense, agility, symbol, weapon=None, credits=0):
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
        """Add an item to the character's inventory"""
        self.inventory.append(item)

    # Serialization methods
    def to_dict(self):
        """Convert Character state to a dictionary for saving."""
        return {
            'name': self.name,
            'health': self.health,
            'max_health': self.max_health,
            'attack': self.attack,
            'defense': self.defense,
            'agility': self.agility,
            'symbol': self.symbol,
            'weapon': self.weapon.to_dict() if self.weapon else None, # Assuming weapon has to_dict
            'credits': self.credits,
            'energy': self.energy,
            'max_energy': self.max_energy,
            'inventory': [item.to_dict() for item in self.inventory], # Assuming items have to_dict
            'level_keys': self.level_keys,
            # Subclasses should add their specific attributes
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Character instance from dictionary data."""
        # Note: This base method is likely not used directly, as Player/NPC have their own from_dict
        # It's here for completeness or potential future use.
        character = cls(
            name=data['name'],
            health=data['health'],
            attack=data['attack'],
            defense=data['defense'],
            agility=data['agility'],
            symbol=data['symbol'],
            credits=data['credits']
        )
        character.max_health = data['max_health']
        character.energy = data['energy']
        character.max_energy = data['max_energy']
        character.level_keys = data['level_keys']

        # Deserialize weapon and inventory (requires Weapon/Item classes to have from_dict)
        # This part needs to be handled carefully, maybe in subclasses or with a factory pattern
        # Example:
        # if data['weapon']:
        #     character.weapon = Weapon.from_dict(data['weapon'])
        # character.inventory = [ItemFactory.create_item(item_data) for item_data in data['inventory']]

        return character
