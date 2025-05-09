"""
JSON utilities for handling JSON serialization with custom types like datetime.
"""
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects by converting them to ISO format strings."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def save_json(data, file_path, indent=2):
    """Save data to a JSON file, handling datetime objects.
    
    Args:
        data: Data to save (dict, list, etc.)
        file_path: Path to the JSON file
        indent: Indentation level for pretty printing
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, cls=DateTimeEncoder, indent=indent)