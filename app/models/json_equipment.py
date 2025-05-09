"""
JSON-based equipment data manager for the application.
This module handles loading, processing, and accessing equipment data from JSON files.
"""
import os
import json
import pandas as pd
from datetime import datetime
from app.models.json_utils import save_json

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
    
    def get_equipment_by_id(self, equipment_id):
        """Get a specific piece of equipment by ID.
        
        Args:
            equipment_id: Unique ID of the equipment
            
        Returns:
            Dictionary representing the equipment, or None if not found
        """
        if equipment_id in self.equipment_by_id:
            item_dict = self.equipment_by_id[equipment_id].copy()
            item_dict['id'] = equipment_id
            return item_dict
        return None
    
    def get_equipment_by_category(self, category):
        """Get equipment filtered by category.
        
        Args:
            category: Category of equipment ('Chamber', 'Electrometer', 'Survey Meter')
            
        Returns:
            List of dictionaries, each representing one piece of equipment
        """
        if self.all_equipment_df is None or self.all_equipment_df.empty:
            return []
        
        filtered_df = self.all_equipment_df[self.all_equipment_df['category'] == category]
        
        # Convert filtered DataFrame to list of dictionaries
        result = []
        for idx, row in filtered_df.iterrows():
            item_dict = row.to_dict()
            item_dict['id'] = idx
            result.append(item_dict)
        
        return result
    
    def get_equipment_by_location(self, location):
        """Get equipment filtered by location.
        
        Args:
            location: Location to filter by
            
        Returns:
            List of dictionaries, each representing one piece of equipment
        """
        if self.all_equipment_df is None or self.all_equipment_df.empty:
            return []
        
        # Check if location is contained within location field
        filtered_df = self.all_equipment_df[
            self.all_equipment_df['location'].str.contains(location, case=False, na=False)
        ]
        
        # Convert filtered DataFrame to list of dictionaries
        result = []
        for idx, row in filtered_df.iterrows():
            item_dict = row.to_dict()
            item_dict['id'] = idx
            result.append(item_dict)
        
        return result
    
    def search_equipment(self, query):
        """Search equipment by keyword across multiple fields.
        
        Args:
            query: Search query string
            
        Returns:
            List of dictionaries, each representing one piece of equipment
        """
        if self.all_equipment_df is None or self.all_equipment_df.empty or not query:
            return []
        
        # Convert query to lowercase for case-insensitive search
        query = str(query).lower()
        
        # Search across multiple columns
        mask = False
        for col in ['manufacturer', 'model', 'serial_number', 'location', 'notes', 'equipment_type']:
            if col in self.all_equipment_df.columns:
                # Add conditions with OR (|) operator
                col_mask = self.all_equipment_df[col].astype(str).str.lower().str.contains(query, na=False)
                mask = mask | col_mask
        
        filtered_df = self.all_equipment_df[mask]
        
        # Convert filtered DataFrame to list of dictionaries
        result = []
        for idx, row in filtered_df.iterrows():
            item_dict = row.to_dict()
            item_dict['id'] = idx
            result.append(item_dict)
        
        return result
    
    def _parse_calibration_date(self, date_str):
        """Parse a calibration date string in various formats into a datetime object.
        
        Args:
            date_str: String representation of a date
            
        Returns:
            datetime object or None if parsing fails
        """
        if not date_str or not isinstance(date_str, str):
            return None
            
        # List of common date formats to try
        date_formats = [
            '%m/%Y',        # 05/2025
            '%m/%d/%Y',     # 05/15/2025
            '%B %Y',        # May 2025
            '%b %Y',        # May 2025
            '%Y-%m-%d',     # 2025-05-15
            '%d-%m-%Y',     # 15-05-2025
            '%m-%d-%Y',     # 05-15-2025
        ]
        
        # Try to extract the date part if there's additional text
        # Example: "05/2025 - repaired"
        if ' - ' in date_str:
            date_str = date_str.split(' - ')[0].strip()
        
        # Try each format
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def get_calibration_due_soon(self, days=30):
        """Get equipment where calibration is due soon.
        
        Args:
            days: Number of days to consider "due soon"
            
        Returns:
            List of dictionaries, each representing one piece of equipment
        """
        current_date = datetime.now()
        due_soon_items = []
        
        for item in self.get_all_equipment():
            if not item.get('calibration_due_date'):
                continue
                
            date_str = str(item.get('calibration_due_date'))
            
            # Check for known status indicators in the text
            if 'overdue' in date_str.lower():
                # Already overdue
                item['calibration_status'] = 'overdue'
                due_soon_items.append(item)
                continue
                
            if 'due soon' in date_str.lower():
                # Already marked as due soon
                item['calibration_status'] = 'due_soon'
                due_soon_items.append(item)
                continue
            
            # Try to parse the date
            cal_date = self._parse_calibration_date(date_str)
            if not cal_date:
                continue
                
            # Calculate difference in days
            delta = cal_date - current_date
            
            if delta.days < 0:
                # Overdue
                item['calibration_status'] = 'overdue'
                item['days_overdue'] = abs(delta.days)
                due_soon_items.append(item)
            elif delta.days <= days:
                # Due soon
                item['calibration_status'] = 'due_soon'
                item['days_until_due'] = delta.days
                due_soon_items.append(item)
        
        return due_soon_items
        
    def filter_by_calibration_date(self, start_date=None, end_date=None, status=None):
        """Filter equipment by calibration date range or status.
        
        Args:
            start_date: Optional datetime object for start of date range
            end_date: Optional datetime object for end of date range
            status: Optional status filter ('current', 'due_soon', 'overdue', 'unknown')
            
        Returns:
            List of dictionaries, each representing one piece of equipment
        """
        all_equipment = self.get_all_equipment()
        filtered_items = []
        current_date = datetime.now()
        
        for item in all_equipment:
            # Skip items without calibration date if filtering by date
            if not item.get('calibration_due_date') and (start_date or end_date or status):
                if status == 'unknown':
                    # Include items with unknown status when explicitly filtering for it
                    item['calibration_status'] = 'unknown'
                    filtered_items.append(item)
                continue
            
            date_str = str(item.get('calibration_due_date', ''))
                
            # Parse calibration date
            cal_date = self._parse_calibration_date(date_str)
            
            # Determine calibration status
            if not cal_date:
                item['calibration_status'] = 'unknown'
                if status == 'unknown':
                    filtered_items.append(item)
                continue
                
            # Calculate time until calibration
            delta = cal_date - current_date
            
            # Assign status
            if delta.days < 0:
                item['calibration_status'] = 'overdue'
                item['days_overdue'] = abs(delta.days)
            elif delta.days <= 30:
                item['calibration_status'] = 'due_soon'
                item['days_until_due'] = delta.days
            else:
                item['calibration_status'] = 'current'
                item['days_until_due'] = delta.days
                
            # Apply date range filter if specified
            date_in_range = True
            if start_date and cal_date < start_date:
                date_in_range = False
            if end_date and cal_date > end_date:
                date_in_range = False
                
            # Apply status filter if specified
            status_matches = True
            if status and item['calibration_status'] != status:
                status_matches = False
                
            # Add to filtered list if it passes all filters
            if date_in_range and (not status or status_matches):
                filtered_items.append(item)
                
        return filtered_items
    
    def get_unique_locations(self):
        """Get a list of unique locations from all equipment.
        
        Returns:
            List of unique location strings
        """
        if self.all_equipment_df is None or self.all_equipment_df.empty:
            return []
        
        if 'location' not in self.all_equipment_df.columns:
            return []
        
        return sorted(self.all_equipment_df['location'].dropna().unique().tolist())
    
    def get_unique_manufacturers(self):
        """Get a list of unique manufacturers from all equipment.
        
        Returns:
            List of unique manufacturer strings
        """
        if self.all_equipment_df is None or self.all_equipment_df.empty:
            return []
        
        if 'manufacturer' not in self.all_equipment_df.columns:
            return []
        
        return sorted(self.all_equipment_df['manufacturer'].dropna().unique().tolist())
    
    def get_equipment_stats(self):
        """Get equipment statistics.
        
        Returns:
            Dictionary with equipment statistics
        """
        stats = {
            'total_equipment': len(self.all_equipment_df) if self.all_equipment_df is not None else 0,
            'chambers_count': len(self.chambers_df) if self.chambers_df is not None else 0,
            'electrometers_count': len(self.electrometers_df) if self.electrometers_df is not None else 0,
            'survey_meters_count': len(self.survey_meters_df) if self.survey_meters_df is not None else 0,
            'locations_count': len(self.get_unique_locations()),
            'manufacturers_count': len(self.get_unique_manufacturers()),
        }
        return stats