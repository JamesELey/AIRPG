from .item import Item
from .potion import Potion


def energy_potion_effect(character):
    restore_amount = 50
    if character.energy < character.max_energy:
        old_energy = character.energy
        character.energy = min(
            character.energy + restore_amount, character.max_energy)
        print(
            f"⚡ Used Energy Potion. Restored {character.energy - old_energy} Energy.")
        return True
    else:
        print(f"❌ {character.name} already has full energy!")
        return False


class EnergyPotion(Potion):
    """Energy restoration potion"""
    def __init__(self, name, description, energy_restore, value=15):
        # Treat energy_restore as the 'effect' amount for consistency with Potion base
        super().__init__(name, description, effect=energy_restore, value=value)
        # Rename self.effect to self.energy_amount for clarity?
        # self.energy_amount = energy_restore
        
    def use(self, character):
        """Use the energy potion on a character"""
        if character.energy >= character.max_energy:
            return False, "Energy is already full!"
            
        old_energy = character.energy
        # Use self.heal_amount from base Potion which stores the effect value
        restore_amount = self.heal_amount
        character.energy = min(character.max_energy, 
                             character.energy + restore_amount)
        actual_restore = character.energy - old_energy
        return True, f"Restored {actual_restore} energy!"
        
    def __str__(self):
        # Use heal_amount from base class for the displayed amount
        return f"{self.name} (+{self.heal_amount} Energy, {self.value} credits)"

    @classmethod
    def create_small_energy(cls):
        return cls("Small Energy Potion", "A weak energy potion", 25)

    @classmethod
    def create_medium_energy(cls):
        return cls("Medium Energy Potion", "A standard energy potion", 50)

    @classmethod
    def create_large_energy(cls):
        return cls("Large Energy Potion", "A powerful energy potion", 100)

    @classmethod
    def create_max_energy(cls):
        return cls("Max Energy Potion", "Fully restores energy", 999)
