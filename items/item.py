from typing import Tuple, Union, Optional, Callable, TypeVar, Any
from abc import ABC, abstractmethod

# Define a type variable for character
T = TypeVar('T')  # Type for character objects

# Define ItemEffect type
ItemEffect = Callable[[T], Union[bool, Tuple[bool, str]]]

class Item(ABC):
    """Base class for all items in the game"""
    def __init__(self, name: str, description: str, effect: Optional[ItemEffect] = None, value: int = 0):
        """
        Initialize a game item
        
        Args:
            name: The name of the item
            description: A description of what the item does
            effect: An optional function representing the item's effect
            value: The value of the item in credits/gold
        """
        self.name = name
        self.description = description
        self.effect = effect
        self.value = value
    
    def use(self, character: T) -> Tuple[bool, str]:
        """
        Use the item on a character
        
        Args:
            character: The character to use the item on
            
        Returns:
            A tuple containing (success, message)
            - success: Whether the item was successfully used
            - message: A message describing what happened
        """
        if self.effect:
            result = self.effect(character)
            # Handle different return types for backward compatibility
            if isinstance(result, tuple) and len(result) >= 2:
                return result  # Already in the expected format
            elif isinstance(result, bool):
                message = f"Used {self.name}" if result else f"Failed to use {self.name}"
                return result, message
        return False, f"{self.name} has no effect."
    
    def __eq__(self, other: Any) -> bool:
        """Check if two items are equal"""
        if not isinstance(other, Item):
            return False
        return (self.name == other.name and
                self.description == other.description and
                self.value == other.value)
    
    def __str__(self) -> str:
        """String representation of the item"""
        return f"{self.name} ({self.description}, {self.value} credits)"

    # Serialization
    def to_dict(self):
        """Convert Item state to dictionary."""
        # Basic implementation, subclasses might override or extend
        # Note: Function effects (self.effect) cannot be directly serialized to JSON
        return {
            'item_class': self.__class__.__name__, # Store class name to help with deserialization
            'name': self.name,
            'description': self.description,
            'value': self.value,
            # Add other serializable attributes common to all items if any
        }

    @staticmethod
    def from_dict(data):
        """Create an Item instance from dictionary data."""
        # This requires a factory pattern or similar mechanism to instantiate the correct subclass
        item_class_name = data.get('item_class')
        if not item_class_name:
            raise ValueError("Item data is missing 'item_class' key")

        # Example: You'd need to map class names to actual classes
        # (This mapping needs to be defined elsewhere, e.g., in an ItemFactory)
        # item_class = ItemFactory.get_class(item_class_name)
        # if not item_class:
        #     raise ValueError(f"Unknown item class: {item_class_name}")
        # return item_class._from_dict_internal(data) # Internal method to handle class-specific loading

        # Placeholder: Raise error until factory is implemented
        raise NotImplementedError("Item.from_dict requires an ItemFactory or similar mechanism")


class ConsumableItem(Item):
    """Base class for items that are consumed on use"""
    def __init__(self, name: str, description: str, effect: Optional[ItemEffect] = None, value: int = 0):
        super().__init__(name, description, effect, value)
    
    @abstractmethod
    def use(self, character: T) -> Tuple[bool, str]:
        """
        Use the consumable item on a character.
        This method should be implemented by subclasses to define the specific behavior.
        
        Args:
            character: The character to use the item on
            
        Returns:
            A tuple containing (success, message)
        """
        pass


class EquippableItem(Item):
    """Base class for items that can be equipped"""
    def __init__(self, name: str, description: str, slot: str, value: int = 0):
        """
        Initialize an equippable item
        
        Args:
            name: The name of the item
            description: A description of what the item does
            slot: The equipment slot this item fits into
            value: The value of the item in credits/gold
        """
        super().__init__(name, description, None, value)
        self.slot = slot
    
    def equip(self, character: T) -> Tuple[bool, str]:
        """
        Equip the item to a character
        
        Args:
            character: The character to equip the item to
            
        Returns:
            A tuple containing (success, message)
        """
        if hasattr(character, 'equip_item'):
            return character.equip_item(self)
        return False, f"{character.name} cannot equip items."
    
    def use(self, character: T) -> Tuple[bool, str]:
        """
        Using an equippable item will attempt to equip it
        
        Args:
            character: The character to equip the item to
            
        Returns:
            A tuple containing (success, message)
        """
        return self.equip(character)


# Define pre-made item effects as functions
def sick_note_effect(character: T) -> Tuple[bool, str]:
    """Effect for the Sick Note item - allows skipping portal boss battles"""
    return True, "You present your Sick Note. The boss fight has been excused!"


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
