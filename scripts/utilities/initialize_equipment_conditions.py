#!/usr/bin/env python3
"""
Script to initialize equipment conditions to "normal" (green) status
"""
import os
import json
import sys
from app import equipment_manager
from app.models.ticket import EquipmentCondition
from app.models.json_utils import save_json

# Configuration
DATA_DIR = 'app/data'
CONDITIONS_FILE = os.path.join(DATA_DIR, 'equipment_conditions.json')

def main():
    """Initialize all equipment to normal condition"""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Get all equipment IDs
    all_equipment = equipment_manager.get_all_equipment()
    equipment_ids = [equip.get('id') for equip in all_equipment]
    
    # Create a dictionary of equipment IDs with normal condition
    conditions = {}
    for equipment_id in equipment_ids:
        conditions[equipment_id] = EquipmentCondition.NORMAL
    
    # Save the conditions to file
    try:
        save_json(conditions, CONDITIONS_FILE)
        print(f"Successfully initialized {len(equipment_ids)} equipment items to NORMAL condition")
    except Exception as e:
        print(f"Error saving equipment conditions: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()