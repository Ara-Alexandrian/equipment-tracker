"""
Standard values manager for equipment fields
Manages standard values for dropdown lists to ensure consistency
"""
import os
import json


class StandardValuesManager:
    """Manages standard values for equipment fields."""
    
    def __init__(self, data_dir='app/data'):
        """Initialize the standard values manager.
        
        Args:
            data_dir: Directory containing the JSON data files
        """
        self.data_dir = data_dir
        self.values_file = os.path.join(data_dir, 'standard_values.json')
        
        # Initialize default values
        self.categories = []
        self.equipment_types = {}
        self.manufacturers = []
        self.locations = []
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load standard values from JSON file."""
        try:
            # Check if file exists
            if not os.path.exists(self.values_file):
                print(f"Warning: Standard values file not found at {self.values_file}")
                # Initialize with default values
                self._create_default_values()
                return
            
            # Load values from file
            with open(self.values_file, 'r') as f:
                values_data = json.load(f)
            
            # Set values
            self.categories = values_data.get('categories', [])
            self.equipment_types = values_data.get('equipment_types', {})
            self.manufacturers = values_data.get('manufacturers', [])
            self.locations = values_data.get('locations', [])
            
            print(f"Loaded standard values: {len(self.categories)} categories, {len(self.manufacturers)} manufacturers, {len(self.locations)} locations")
            
        except Exception as e:
            print(f"Error loading standard values: {str(e)}")
            # Initialize with default values on error
            self._create_default_values()
    
    def _create_default_values(self):
        """Create default standard values."""
        self.categories = ["Chamber", "Electrometer", "Survey Meter"]
        self.equipment_types = {
            "Chamber": ["ionization chamber"],
            "Electrometer": ["standard electrometer"],
            "Survey Meter": ["portable survey meter"]
        }
        self.manufacturers = ["CNMC", "PTW", "Standard Imaging"]
        self.locations = ["Main Facility"]
        
        # Save default values
        self.save_data()
    
    def save_data(self):
        """Save standard values to JSON file."""
        try:
            values_data = {
                'categories': self.categories,
                'equipment_types': self.equipment_types,
                'manufacturers': self.manufacturers,
                'locations': self.locations
            }
            
            with open(self.values_file, 'w') as f:
                json.dump(values_data, f, indent=2)
            
            print(f"Saved standard values to {self.values_file}")
            return True
            
        except Exception as e:
            print(f"Error saving standard values: {str(e)}")
            return False
    
    def get_categories(self):
        """Get list of equipment categories."""
        return sorted(self.categories)
    
    def get_equipment_types(self, category=None):
        """Get list of equipment types, optionally filtered by category."""
        if category and category in self.equipment_types:
            return sorted(self.equipment_types[category])
        else:
            # Combine all equipment types across categories
            all_types = []
            for types in self.equipment_types.values():
                all_types.extend(types)
            return sorted(set(all_types))
    
    def get_manufacturers(self):
        """Get list of equipment manufacturers."""
        return sorted(self.manufacturers)
    
    def get_locations(self):
        """Get list of equipment locations."""
        return sorted(self.locations)
    
    def add_category(self, category):
        """Add a new category."""
        if category not in self.categories:
            self.categories.append(category)
            # Initialize equipment types for this category if needed
            if category not in self.equipment_types:
                self.equipment_types[category] = []
            self.save_data()
            return True
        return False
    
    def add_equipment_type(self, equipment_type, category):
        """Add a new equipment type to a category."""
        if category not in self.categories:
            return False
        
        if category not in self.equipment_types:
            self.equipment_types[category] = []
        
        if equipment_type not in self.equipment_types[category]:
            self.equipment_types[category].append(equipment_type)
            self.save_data()
            return True
        return False
    
    def add_manufacturer(self, manufacturer):
        """Add a new manufacturer."""
        if manufacturer not in self.manufacturers:
            self.manufacturers.append(manufacturer)
            self.save_data()
            return True
        return False
    
    def add_location(self, location):
        """Add a new location."""
        if location not in self.locations:
            self.locations.append(location)
            self.save_data()
            return True
        return False
    
    def remove_category(self, category):
        """Remove a category."""
        if category in self.categories:
            self.categories.remove(category)
            # Also remove equipment types for this category
            if category in self.equipment_types:
                del self.equipment_types[category]
            self.save_data()
            return True
        return False
    
    def remove_equipment_type(self, equipment_type, category):
        """Remove an equipment type from a category."""
        if category in self.equipment_types and equipment_type in self.equipment_types[category]:
            self.equipment_types[category].remove(equipment_type)
            self.save_data()
            return True
        return False
    
    def remove_manufacturer(self, manufacturer):
        """Remove a manufacturer."""
        if manufacturer in self.manufacturers:
            self.manufacturers.remove(manufacturer)
            self.save_data()
            return True
        return False
    
    def remove_location(self, location):
        """Remove a location."""
        if location in self.locations:
            self.locations.remove(location)
            self.save_data()
            return True
        return False

    def edit_category(self, old_value, new_value):
        """Edit an existing category.

        Args:
            old_value: The current value to be changed
            new_value: The new value to replace it with

        Returns:
            bool: Whether the edit was successful
        """
        if old_value not in self.categories or new_value in self.categories:
            return False

        # Update the category in the list
        index = self.categories.index(old_value)
        self.categories[index] = new_value

        # Update the equipment types dictionary key
        if old_value in self.equipment_types:
            self.equipment_types[new_value] = self.equipment_types.pop(old_value)

        self.save_data()
        return True

    def edit_equipment_type(self, category, old_value, new_value):
        """Edit an existing equipment type.

        Args:
            category: The category the equipment type belongs to
            old_value: The current value to be changed
            new_value: The new value to replace it with

        Returns:
            bool: Whether the edit was successful
        """
        if (category not in self.equipment_types or
            old_value not in self.equipment_types[category] or
            new_value in self.equipment_types[category]):
            return False

        # Update the equipment type in the list
        index = self.equipment_types[category].index(old_value)
        self.equipment_types[category][index] = new_value

        self.save_data()
        return True

    def edit_manufacturer(self, old_value, new_value):
        """Edit an existing manufacturer.

        Args:
            old_value: The current value to be changed
            new_value: The new value to replace it with

        Returns:
            bool: Whether the edit was successful
        """
        if old_value not in self.manufacturers or new_value in self.manufacturers:
            return False

        # Update the manufacturer in the list
        index = self.manufacturers.index(old_value)
        self.manufacturers[index] = new_value

        self.save_data()
        return True

    def edit_location(self, old_value, new_value):
        """Edit an existing location.

        Args:
            old_value: The current value to be changed
            new_value: The new value to replace it with

        Returns:
            bool: Whether the edit was successful
        """
        if old_value not in self.locations or new_value in self.locations:
            return False

        # Update the location in the list
        index = self.locations.index(old_value)
        self.locations[index] = new_value

        self.save_data()
        return True