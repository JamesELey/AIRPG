from .item import Item # Import the base Item class

class SickNote(Item): # Inherit from Item
    def __init__(self):
        # Initialize using the base Item class constructor
        super().__init__(
            name="Sick Note",
            description="Allows you to escape from battle",
            value=50 # Give it a value
        )

    def use(self, target):
        return True  # Always succeeds in escaping

    def __str__(self):
        return f"{self.name} ({self.description})"

    def __eq__(self, other):
        if not isinstance(other, SickNote):
            return False
        return self.name == other.name

    # Serialization (Uses base Item methods)
    def to_dict(self):
        """Convert SickNote state to dictionary."""
        # Use the base Item to_dict method
        return super().to_dict()

    @classmethod
    def from_dict(cls, data):
        """Create a SickNote instance from dictionary data."""
        # Simple instantiation as it has no unique state beyond Item
        return cls()
