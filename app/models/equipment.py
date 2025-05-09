"""
Equipment data models for the application.
This module handles loading, processing, and accessing equipment data.
"""
import os
import pandas as pd
from datetime import datetime
import json

class EquipmentDataManager:
    """Manages equipment data, including loading from Excel and providing access methods."""
    
    # Column mapping between Excel and our unified model
    COLUMN_MAPPING = {
        'chambers': {
            'Type': 'equipment_type',
            'Manufacturer': 'manufacturer',
            'Model': 'model', 
            'SN': 'serial_number',
            'Location': 'location',
            'Cal Due Date': 'calibration_due_date',
            'Comments': 'notes'
        },
        'electrometers': {
            'Type': 'equipment_type',
            'Manufacturer': 'manufacturer', 
            'Model': 'model',
            'SN': 'serial_number',
            'Location': 'location',
            'Cal Due Date': 'calibration_due_date',
            'Comments': 'notes'
        },
        'survey_meters': {
            'Type': 'equipment_type',
            'Manufacturer': 'manufacturer',
            'Model': 'model',
            'SN': 'serial_number',
            'Location': 'location',
            'Cal Due Date': 'calibration_due_date',
            'Comments': 'notes',
            'Chk Source': 'check_source'
        }
    }
    
    def __init__(self, data_dir='Resources'):
        """Initialize the equipment data manager.
        
        Args:
            data_dir: Directory containing the Excel files
        """
        self.data_dir = data_dir
        self.chambers_file = os.path.join(data_dir, '2025 Health Physics Equipment List_Chambers & Electrometers.xls')
        self.survey_meters_file = os.path.join(data_dir, '2025 Survey Meter Inventory & Calibration_updated 0425.xls')
        
        # DataFrames to store our equipment data
        self.chambers_df = None
        self.electrometers_df = None
        self.survey_meters_df = None
        
        # Combined and processed data
        self.all_equipment_df = None
        
        # Cache of equipment by ID for quicker lookups
        self.equipment_by_id = {}
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load and process all equipment data from Excel files."""
        
        try:
            # Load chambers data
            raw_chambers = pd.read_excel(self.chambers_file, sheet_name='Chambers')
            # Use row 1 as column names
            raw_chambers.columns = raw_chambers.iloc[1]
            # Skip the first 3 rows (0=header, 1=column names, 2=empty row)
            self.chambers_df = self._clean_dataframe(raw_chambers.iloc[3:].reset_index(drop=True), 'chambers')
            
            # Load electrometers data
            raw_electrometers = pd.read_excel(self.chambers_file, sheet_name='Electrometers')
            # Use row 1 as column names
            raw_electrometers.columns = raw_electrometers.iloc[1]
            # Skip the first 3 rows
            self.electrometers_df = self._clean_dataframe(raw_electrometers.iloc[3:].reset_index(drop=True), 'electrometers')
            
            # Load survey meters data
            raw_survey_meters = pd.read_excel(self.survey_meters_file, sheet_name='Survey Meters')
            # Use row 1 as column names
            raw_survey_meters.columns = raw_survey_meters.iloc[1]
            # Skip the first 3 rows
            self.survey_meters_df = self._clean_dataframe(raw_survey_meters.iloc[3:].reset_index(drop=True), 'survey_meters')
            
            # Combine all equipment into a single DataFrame
            self._combine_equipment_data()
            
            print(f"Loaded {len(self.chambers_df)} chambers, {len(self.electrometers_df)} electrometers, {len(self.survey_meters_df)} survey meters")
            
        except Exception as e:
            print(f"Error loading equipment data: {e}")
            # Initialize empty DataFrames in case of error
            self.chambers_df = pd.DataFrame()
            self.electrometers_df = pd.DataFrame()
            self.survey_meters_df = pd.DataFrame()
            self.all_equipment_df = pd.DataFrame()
    
    def _clean_dataframe(self, df, equipment_type):
        """Clean and standardize a DataFrame.
        
        Args:
            df: DataFrame to clean
            equipment_type: Type of equipment ('chambers', 'electrometers', 'survey_meters')
            
        Returns:
            Cleaned DataFrame with standardized column names
        """
        # Drop completely empty rows
        df = df.dropna(how='all')
        
        # Map columns to our standardized model
        column_mapping = self.COLUMN_MAPPING.get(equipment_type, {})
        
        # Create a new DataFrame with our standardized columns
        new_df = pd.DataFrame()
        
        # Add a category column
        if equipment_type == 'chambers':
            new_df['category'] = 'Chamber'
        elif equipment_type == 'electrometers':
            new_df['category'] = 'Electrometer'
        else:
            new_df['category'] = 'Survey Meter'
        
        # Map columns from original DataFrame
        for excel_col, model_col in column_mapping.items():
            if excel_col in df.columns:
                new_df[model_col] = df[excel_col]
            else:
                new_df[model_col] = None
        
        # Add unique ID for each piece of equipment
        # Using a composite of category + manufacturer + model + serial number
        new_df['id'] = new_df.apply(
            lambda row: f"{row['category']}-{str(row.get('manufacturer', '')).replace(' ', '_')}-{str(row.get('serial_number', '')).replace(' ', '_')}",
            axis=1
        )
        
        # Set index to the ID field
        new_df = new_df.set_index('id')
        
        # Add a raw_data column containing the original data
        new_df['raw_data'] = df.apply(lambda x: json.dumps(x.dropna().to_dict()), axis=1)
        
        return new_df
    
    def _combine_equipment_data(self):
        """Combine all equipment DataFrames into a single DataFrame."""
        # Concatenate all DataFrames
        self.all_equipment_df = pd.concat([
            self.chambers_df, 
            self.electrometers_df, 
            self.survey_meters_df
        ])
        
        # Build the equipment_by_id cache
        self.equipment_by_id = self.all_equipment_df.to_dict('index')
    
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
        for col in ['manufacturer', 'model', 'serial_number', 'location', 'notes']:
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