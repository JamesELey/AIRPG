from .item import Item, small_potion_effect, medium_potion_effect, large_potion_effect, phoenix_down_effect


class Potion(Item):
    """Base class for all potions"""
    def __init__(self, name, description, effect, value=10):
        # Note: The 'effect' argument here seems to store the heal amount, not a function
        # Let's assume effect is the amount for serialization.
        super().__init__(name, description, effect=None, value=value) # Pass effect=None to base Item
        self.heal_amount = effect # Store the heal amount separately

    def use(self, target):
        if target.health >= target.max_health:
            return False, "Health is already full!"

        old_health = target.health
        target.health = min(target.max_health,
                            target.health + self.heal_amount)
        actual_heal = target.health - old_health
        return True, f"Healed for {actual_heal} HP!"

    def __str__(self):
        return f"{self.name} ({self.description})"

    def __eq__(self, other):
        if not isinstance(other, Potion):
            return False
        return (self.name == other.name and
                self.description == other.description and
                self.heal_amount == other.heal_amount) # Compare heal_amount

    # Serialization
    def to_dict(self):
        """Convert Potion state to dictionary."""
        data = super().to_dict() # Get base Item data
        data.update({
            'heal_amount': self.heal_amount # Use heal_amount instead of effect
        })
        return data

    @classmethod
    def from_dict(cls, data):
        """Create a Potion instance from dictionary data."""
        item_class_name = data.get('item_class')
        item_class = None

        # Try to find the specific class from the map
        if item_class_name:
            # Import necessary classes locally to handle potential circular dependencies
            from items.item_factory import ITEM_CLASS_MAP
            from items.energy_potion import EnergyPotion
            from items.revive_potion import RevivePotion # Ensure RevivePotion is imported
            item_class = ITEM_CLASS_MAP.get(item_class_name)

        # Determine the correct class to instantiate (fallback to base Potion if needed)
        target_cls = item_class if item_class and issubclass(item_class, Potion) else cls

        if not item_class: # Log if we couldn't find the specific class
             print(f"Warning: Could not find specific Potion subclass for {item_class_name}, using base {cls.__name__}.")

        # Instantiate the target class directly with saved data, handling specific cases
        try:
            if target_cls == RevivePotion:
                 # RevivePotion: name, description, value
                 instance = target_cls(name=data['name'], description=data['description'], value=data['value'])
            elif target_cls == EnergyPotion:
                 # EnergyPotion: name, description, energy_restore, value
                 instance = target_cls(
                     name=data['name'],
                     description=data['description'],
                     energy_restore=data['heal_amount'], # Pass heal_amount as energy_restore
                     value=data['value']
                 )
                 instance.heal_amount = data['heal_amount'] # Still set heal_amount attribute if needed
            else:
                 # Other Potions (Small, Medium, Large, or base Potion fallback):
                 # Use name, description, effect (heal_amount), value
                 instance = target_cls(
                     name=data['name'],
                     description=data['description'],
                     effect=data['heal_amount'], # Pass heal_amount as effect arg
                     value=data['value']
                 )
                 instance.heal_amount = data['heal_amount'] # Ensure heal_amount attribute matches

        except KeyError as e:
            raise ValueError(f"Missing required key {e} in potion data for {item_class_name or 'Potion'}") from e
        except TypeError as e:
             # Catch potential mismatches between args and __init__ signature
            raise ValueError(f"Error instantiating {target_cls.__name__} from data: {e}") from e

        return instance

    @classmethod
    def create_small_potion(cls):
        return cls("Small Potion", "Restores 20 HP", 20)

    @classmethod
    def create_medium_potion(cls):
        return cls("Medium Potion", "Restores 50 HP", 50)

    @classmethod
    def create_large_potion(cls):
        return cls("Large Potion", "Restores 100 HP", 100)

    @classmethod
    def create_max_potion(cls):
        return cls("Max Potion", "Fully restores health", 200)


class SmallPotion(Potion):
    def __init__(self, *args, **kwargs):
        # Ensure base init is called correctly, even if specific args aren't used here
        super().__init__(
            name="Small Potion",
            description="Restores 20 HP",
            effect=20, # This is the heal_amount
            value=kwargs.get('value', 10) # Use default value or from kwargs if provided
        )


class MediumPotion(Potion):
    def __init__(self, *args, **kwargs):
        # Ensure base init is called correctly
        super().__init__(
            name="Medium Potion",
            description="Restores 50 HP",
            effect=50, # This is the heal_amount
            value=kwargs.get('value', 25)
        )


class LargePotion(Potion):
    def __init__(self, *args, **kwargs):
        # Ensure base init is called correctly
        super().__init__(
            name="Large Potion",
            description="Restores 100 HP",
            effect=100, # This is the heal_amount
            value=kwargs.get('value', 50)
        )


class RevivePotion(Potion):
    def __init__(self, name="Phoenix Down", description="Revives a fallen character with full HP", value=150):
        # Updated init to accept args for consistency with from_dict
        super().__init__(
            name=name,
            description=description,
            effect=0, # Base effect is 0
            value=value
        )
        # heal_amount is not relevant for RevivePotion logic

    def use(self, character):
        """Revives the character to full health."""
        if character.is_alive():
            return False, f"{character.name} is still alive!"
        else:
            character.health = character.max_health
            return True, f"{character.name} was revived to full health!"

    # Add from_dict if needed
    # @classmethod
    # def from_dict(cls, data):
    #     return cls()

    def __str__(self):
        return f"{self.name} ({self.description}, {self.value} credits)"

    # Override to_dict for RevivePotion if necessary (e.g., if it had unique state)
    # def to_dict(self):
    #     data = super().to_dict()
    #     # Add/modify RevivePotion specific data
    #     return data
