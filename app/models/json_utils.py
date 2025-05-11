"""
JSON utilities for handling JSON serialization with custom types like datetime.
"""
import json
import os
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects by converting them to ISO format strings."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Handle other special types as needed
        return super().default(obj)

class DateTimeDecoder(json.JSONDecoder):
    """Custom JSON decoder for datetime objects in ISO format"""
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        for key, value in obj.items():
            if isinstance(value, str):
                try:
                    # Try to parse ISO format datetime strings
                    if 'T' in value and ('+' in value or 'Z' in value or '-' in value[10:]):
                        obj[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    # If it's not a datetime string, keep it as is
                    pass
        return obj

def save_json(data, file_path, indent=2):
    """Save data to a JSON file, handling datetime objects.

    Args:
        data: Data to save (dict, list, etc.)
        file_path: Path to the JSON file
        indent: Indentation level for pretty printing
    """
    try:
        # Convert datetime objects to strings to avoid serialization issues
        data_copy = json_safe_copy(data)

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(data_copy, f, cls=DateTimeEncoder, indent=indent)

        return True
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")
        return False

def load_json(file_path):
    """Load data from a JSON file using the DateTimeDecoder

    Args:
        file_path: Path to the JSON file

    Returns:
        Loaded data with datetime objects properly deserialized,
        or empty dict/list if file doesn't exist or has errors
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f, cls=DateTimeDecoder)
        except Exception as e:
            print(f"Error loading JSON from {file_path}: {e}")

            # Return appropriate empty structure (list or dict)
            if file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    first_char = f.read(1).strip()
                    if first_char == '[':
                        return []
                    return {}
            return {}
    return {}

def json_safe_copy(data):
    """Create a copy of the data that can be safely serialized to JSON.

    This function:
    1. Converts datetime objects to strings
    2. Handles nested dictionaries, lists and other structures

    Args:
        data: The data to convert

    Returns:
        A copy of the data with all values as JSON serializable types
    """
    if isinstance(data, dict):
        # Handle dict
        result = {}
        for key, value in data.items():
            result[key] = json_safe_copy(value)
        return result
    elif isinstance(data, list):
        # Handle list
        return [json_safe_copy(item) for item in data]
    elif isinstance(data, tuple):
        # Handle tuple by converting to list
        return [json_safe_copy(item) for item in data]
    elif isinstance(data, datetime):
        # Convert datetime to string
        return data.isoformat()
    elif isinstance(data, (int, float, str, bool, type(None))):
        # These types are already JSON serializable
        return data
    else:
        # Convert other types to string (may not be ideal, but better than failing)
        return str(data)