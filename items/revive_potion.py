from .potion import Potion


class RevivePotion(Potion):
    """Potion that can revive fallen characters"""
    def __init__(self, name="Phoenix Down", description="Revives fallen characters", value=50):
        super().__init__(name, description, effect=None, value=value)

    def use(self, character):
        """Use the revive potion on a character"""
        if character.is_alive():
            return False, "Character is already alive!"
            
        character.health = character.max_health
        return True, f"Revived {character.name} with full health!"

    def __str__(self):
        return f"{self.name} (Revive, {self.value} credits)"

    @classmethod
    def create_phoenix_down(cls):
        return cls()

    def __eq__(self, other):
        if not isinstance(other, RevivePotion):
            return False
        return self.name == other.name

    # Serialization (Handled by base Potion class)
    # Since RevivePotion doesn't add new state beyond what Potion/Item store,
    # the base to_dict/from_dict should suffice.
    # If it had unique properties, we would override:
    # def to_dict(self):
    #     data = super().to_dict()
    #     # Add RevivePotion specific fields
    #     return data
    #
    # @classmethod
    # def from_dict(cls, data):
    #     instance = cls(name=data['name'], description=data['description'], value=data['value'])
    #     # Populate RevivePotion specific fields if any
    #     return instance
