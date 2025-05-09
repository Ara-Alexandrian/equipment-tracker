"""
JSON-based equipment data manager for the application.
This module handles loading, processing, and accessing equipment data from JSON files.
"""
import os
import json
import pandas as pd
from datetime import datetime
import traceback
from app.models.json_utils import save_json, DateTimeEncoder

class JsonEquipmentDataManager:
    """Manages equipment data, loading from JSON and providing access methods."""
    
    def __init__(self, data_dir='app/data'):
        """Initialize the equipment data manager.
        
        Args:
            data_dir: Directory containing the JSON data files
        """
        self.data_dir = data_dir
        
        # JSON file paths
        self.equipment_json = os.path.join(data_dir, 'equipment.json')
        
        # DataFrames to store equipment data
        self.all_equipment_df = None
        self.chambers_df = None
        self.electrometers_df = None
        self.survey_meters_df = None
        
        # Cache of equipment by ID for quicker lookups
        self.equipment_by_id = {}
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load and process equipment data from JSON files."""
        try:
            # Check if JSON file exists
            if not os.path.exists(self.equipment_json):
                print(f"Warning: Equipment JSON file not found at {self.equipment_json}")
                # Initialize empty DataFrames
                self.all_equipment_df = pd.DataFrame()
                self.chambers_df = pd.DataFrame()
                self.electrometers_df = pd.DataFrame()
                self.survey_meters_df = pd.DataFrame()
                return
                
            # Load equipment data from JSON
            with open(self.equipment_json, 'r') as f:
                equipment_data = json.load(f)
            
            # Convert to DataFrame
            self.all_equipment_df = pd.DataFrame(equipment_data)
            
            # Set index to the ID field if it exists
            if 'id' in self.all_equipment_df.columns:
                self.all_equipment_df = self.all_equipment_df.set_index('id')
            
            # Split into category-specific DataFrames
            if 'category' in self.all_equipment_df.columns:
                self.chambers_df = self.all_equipment_df[self.all_equipment_df['category'] == 'Chamber']
                self.electrometers_df = self.all_equipment_df[self.all_equipment_df['category'] == 'Electrometer']
                self.survey_meters_df = self.all_equipment_df[self.all_equipment_df['category'] == 'Survey Meter']
            
            # Build the equipment_by_id cache
            self.equipment_by_id = self.all_equipment_df.to_dict('index')
            
            print(f"Loaded {len(self.chambers_df)} chambers, {len(self.electrometers_df)} electrometers, {len(self.survey_meters_df)} survey meters")
            
        except Exception as e:
            print(f"Error loading equipment data: {e}")
            traceback.print_exc()  # Print the full traceback to help debug the issue
            # Initialize empty DataFrames in case of error
            self.all_equipment_df = pd.DataFrame()
            self.chambers_df = pd.DataFrame()
            self.electrometers_df = pd.DataFrame()
            self.survey_meters_df = pd.DataFrame()
    
    def get_all_equipment(self):
        """Get all equipment as a list of dictionaries.
        
        Returns:
            List of dictionaries, each representing one piece of equipment
        """
        if self.all_equipment_df is None or self.all_equipment_df.empty:
            return []
        
        # Convert DataFrame to list of dictionaries, including the index as 'id'
        result = []
        for idx, row in self.all_equipment_df.iterrows():
            item_dict = row.to_dict()
            item_dict['id'] = idx
            result.append(item_dict)
        
        return result