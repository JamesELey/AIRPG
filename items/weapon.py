from .item import Item


class Weapon(Item):
    """Weapon class for combat items"""
    def __init__(self, name, description, attack, value=20):
        super().__init__(name, description, effect=None, value=value)
        self.attack = attack
        
    def use(self, character):
        """Equip the weapon to a character"""
        if character.weapon == self:
            return False, "Already equipped this weapon!"
            
        old_weapon = character.weapon
        character.weapon = self
        return True, f"Equipped {self.name}!" + (f" Unequipped {old_weapon.name}." if old_weapon else "")
        
    def __str__(self):
        return f"{self.name} (+{self.attack} ATK, {self.value} credits)"

    def __eq__(self, other):
        if not isinstance(other, Weapon):
            return False
        return (self.name == other.name and
                self.attack == other.attack and
                self.value == other.value)

    @classmethod
    def create_level_weapon(cls, level):
        """Create a weapon appropriate for the given level"""
        weapon_types = {
            1: ("Wooden Sword", "A basic training weapon", 50, 5),
            2: ("Iron Sword", "A sturdy iron blade", 100, 10),
            3: ("Steel Sword", "A well-crafted steel sword", 200, 15),
            4: ("Silver Sword", "A finely crafted silver blade", 400, 20),
            5: ("Mythril Blade", "A legendary sword of mythril", 800, 25)
        }

        # Use the highest tier weapon available for the level
        weapon_level = min(level, max(weapon_types.keys()))
        name, desc, value, attack = weapon_types[weapon_level]
        return cls(name, desc, attack, value)  # value is used as durability

    # Serialization
    def to_dict(self):
        """Convert Weapon state to dictionary."""
        data = super().to_dict() # Get base Item data
        data.update({
            'attack': self.attack
        })
        return data

    @classmethod
    def from_dict(cls, data):
        """Create a Weapon instance from dictionary data."""
        # Assumes base Item attributes (name, description, value) are present
        return cls(
            name=data['name'],
            description=data['description'],
            attack=data['attack'],
            value=data['value']
        )
