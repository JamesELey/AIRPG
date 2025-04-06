from items.item import Item
from items.potion import Potion, SmallPotion, MediumPotion, LargePotion
from items.energy_potion import EnergyPotion
from items.weapon import Weapon
from items.revive_potion import RevivePotion
from items.sick_note import SickNote
# Crop is not usually in inventory, so not needed in ITEM_CLASS_MAP
# from items.crop import Crop

# Define ITEM_CLASS_MAP BEFORE ItemFactory uses it
ITEM_CLASS_MAP = {
    # Potions
    'Potion': Potion,
    'SmallPotion': SmallPotion,
    'MediumPotion': MediumPotion,
    'LargePotion': LargePotion,
    'RevivePotion': RevivePotion,
    'EnergyPotion': EnergyPotion,
    # Weapons
    'Weapon': Weapon,
    # Special
    'SickNote': SickNote,
    # Add other item subclasses here as needed
}

class ItemFactory:
    @staticmethod
    def create_item(data: dict) -> 'Item':
        """Create an Item instance from dictionary data using the class name."""
        item_class_name = data.get('item_class')
        if not item_class_name:
            raise ValueError("Item data is missing 'item_class' key")

        item_class = ITEM_CLASS_MAP.get(item_class_name)
        if not item_class:
            error_msg = f"Unknown item class: {item_class_name}"
            raise ValueError(error_msg)

        # Use the class's specific from_dict method if available, otherwise fallback
        if hasattr(item_class, 'from_dict') and callable(getattr(item_class, 'from_dict')):
            # We assume from_dict is a @classmethod or can handle being called on the class
            return item_class.from_dict(data)
        else:
            # Basic fallback if from_dict isn't implemented on the specific class
            # This might be insufficient for complex items
            print(f"Warning: Using basic instantiation for {item_class_name}.")
            # Attempt generic instantiation (might fail if __init__ args don't match)
            try:
                # Assumes basic Item constructor args; subclasses might need specific handling
                return item_class(name=data['name'], description=data['description'], value=data['value'])
            except TypeError as e:
                error_msg = f"Could not instantiate {item_class_name} from data: {e}"
                raise ValueError(error_msg)

    @staticmethod
    def get_class(class_name: str):
        """Get the class object from its name string."""
        return ITEM_CLASS_MAP.get(class_name)