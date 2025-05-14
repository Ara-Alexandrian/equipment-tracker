"""
JSON-based checkout system for tracking equipment location and status.
"""
import os
import json
from datetime import datetime, timedelta
import uuid
from app.models.json_utils import save_json
try:
    # Import werkzeug for password hashing (safer than trying inside functions)
    from werkzeug.security import generate_password_hash, check_password_hash
    WERKZEUG_AVAILABLE = True
except ImportError:
    # Define a fallback if werkzeug is not available
    WERKZEUG_AVAILABLE = False
    print("Warning: werkzeug not available - password hashing disabled")

class JsonCheckoutManager:
    """Manages equipment checkout, location tracking, and status using JSON files."""
    
    # Status options for equipment
    STATUS_OPTIONS = [
        'In Storage',  # Default status - in primary location
        'Checked Out',  # Temporarily relocated
        'In Calibration',  # Sent for calibration
        'Under Repair',  # Being repaired
        'Out of Service'  # Not usable
    ]
    
    def __init__(self, data_dir='app/data'):
        """Initialize the checkout manager.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        
        # Create the data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Checkout history file
        self.checkout_history_file = os.path.join(data_dir, 'checkout_history.json')
        
        # Equipment status file
        self.equipment_status_file = os.path.join(data_dir, 'equipment_status.json')
        
        # Users file
        self.users_file = os.path.join(data_dir, 'users.json')
        
        # Load data
        self.checkout_history = self._load_checkout_history()
        self.equipment_status = self._load_equipment_status()
        self.users = self._load_users()
    
    def _load_checkout_history(self):
        """Load checkout history from file.
        
        Returns:
            List of checkout records
        """
        if os.path.exists(self.checkout_history_file):
            try:
                with open(self.checkout_history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_checkout_history(self):
        """Save checkout history to file."""
        save_json(self.checkout_history, self.checkout_history_file)
    
    def _load_equipment_status(self):
        """Load equipment status from file.
        
        Returns:
            Dictionary mapping equipment IDs to status information
        """
        if os.path.exists(self.equipment_status_file):
            try:
                with open(self.equipment_status_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_equipment_status(self):
        """Save equipment status to file."""
        save_json(self.equipment_status, self.equipment_status_file)
    
    def _load_users(self):
        """Load users from file.
        
        Returns:
            Dictionary mapping usernames to user information
        """
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except:
                return self._create_default_users()
        return self._create_default_users()
    
    def _create_default_users(self):
        """Create default users if no users exist.
        
        Returns:
            Dictionary with default users
        """
        default_users = {
            "admin": {
                "name": "Administrator",
                "email": "admin@example.com",
                "role": "admin",
                "password": "admin123"  # In a real application, use hashed passwords
            },
            "physicist": {
                "name": "Clinical Physicist",
                "email": "physicist@example.com",
                "role": "physicist",
                "password": "physicist123"
            }
            # Regular user role has been removed as per requirements
        }
        
        # Save default users
        save_json(default_users, self.users_file)
        
        return default_users
    
    def _save_users(self):
        """Save users to file."""
        try:
            # First make a copy to ensure it's serializable
            serializable_users = {}

            # Create a clean copy without any potential non-serializable objects
            for username, user_data in self.users.items():
                serializable_users[username] = {
                    key: value for key, value in user_data.items()
                    if key != '_temp' and not callable(value)
                }

            # Save to file
            save_json(serializable_users, self.users_file)
            print(f"Users saved successfully to {self.users_file}")
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error saving users to {self.users_file}: {str(e)}")
            return False
    
    def get_equipment_status(self, equipment_id):
        """Get the current status of a piece of equipment.
        
        Args:
            equipment_id: ID of the equipment to check
            
        Returns:
            Dictionary with status information, or a default status if not found
        """
        if equipment_id in self.equipment_status:
            return self.equipment_status[equipment_id]
        
        # Default status if not found
        return {
            "status": "In Storage",
            "location": "Default Location",
            "checked_out_by": None,
            "checked_out_time": None,
            "expected_return": None,
            "notes": ""
        }
    
    def update_equipment_status(self, equipment_id, status, location=None, checked_out_by=None, 
                                expected_return=None, notes=None, user=None):
        """Update the status of a piece of equipment.
        
        Args:
            equipment_id: ID of the equipment to update
            status: New status from STATUS_OPTIONS
            location: Current location of the equipment
            checked_out_by: Username of person who checked out the equipment
            expected_return: Expected return date (ISO format string)
            notes: Additional notes
            user: Username of the user making the update
            
        Returns:
            Boolean indicating success
        """
        if status not in self.STATUS_OPTIONS:
            return False
        
        # Get current status
        current_status = self.get_equipment_status(equipment_id)
        
        # Update status
        new_status = {
            "status": status,
            "location": location if location is not None else current_status.get("location", "Default Location"),
            "checked_out_by": checked_out_by if status == "Checked Out" else None,
            "checked_out_time": datetime.now().isoformat() if status == "Checked Out" else None,
            "expected_return": expected_return if status == "Checked Out" else None,
            "notes": notes if notes is not None else current_status.get("notes", ""),
            "last_updated": datetime.now().isoformat(),
            "updated_by": user
        }
        
        # Store status
        self.equipment_status[equipment_id] = new_status
        self._save_equipment_status()
        
        # Add to history if status changed or location changed
        if (status != current_status.get("status") or 
            new_status["location"] != current_status.get("location")):
            
            history_entry = {
                "id": str(uuid.uuid4()),
                "equipment_id": equipment_id,
                "timestamp": datetime.now().isoformat(),
                "previous_status": current_status.get("status"),
                "new_status": status,
                "previous_location": current_status.get("location"),
                "new_location": new_status["location"],
                "user": user,
                "notes": notes
            }
            
            self.checkout_history.append(history_entry)
            self._save_checkout_history()
        
        return True
    
    def checkout_equipment(self, equipment_id, user, location, expected_return_days=1, notes=None):
        """Check out a piece of equipment.
        
        Args:
            equipment_id: ID of the equipment to check out
            user: Username of the person checking out
            location: Temporary location
            expected_return_days: Number of days until expected return
            notes: Additional notes
            
        Returns:
            Boolean indicating success
        """
        # Calculate expected return date
        expected_return = (datetime.now() + timedelta(days=expected_return_days)).isoformat()
        
        return self.update_equipment_status(
            equipment_id=equipment_id,
            status="Checked Out",
            location=location,
            checked_out_by=user,
            expected_return=expected_return,
            notes=notes,
            user=user
        )
    
    def return_equipment(self, equipment_id, user, return_location=None, notes=None):
        """Return a piece of equipment.
        
        Args:
            equipment_id: ID of the equipment to return
            user: Username of the person returning
            return_location: Location to return to (if None, uses the default location)
            notes: Additional notes
            
        Returns:
            Boolean indicating success
        """
        current_status = self.get_equipment_status(equipment_id)
        
        # If return location is not specified, revert to default location
        if return_location is None:
            # In a real application, you would look up the default location from the equipment record
            return_location = "Default Location"
        
        return self.update_equipment_status(
            equipment_id=equipment_id,
            status="In Storage",
            location=return_location,
            checked_out_by=None,
            expected_return=None,
            notes=notes,
            user=user
        )
    
    def get_checked_out_equipment(self):
        """Get all currently checked out equipment.
        
        Returns:
            List of dictionaries with checked out equipment details
        """
        checked_out = []
        
        for equipment_id, status in self.equipment_status.items():
            if status.get("status") == "Checked Out":
                item = status.copy()
                item["id"] = equipment_id
                checked_out.append(item)
        
        return checked_out
    
    def get_equipment_by_status(self, status):
        """Get all equipment with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of dictionaries with equipment details
        """
        filtered_equipment = []
        
        for equipment_id, equipment_status in self.equipment_status.items():
            if equipment_status.get("status") == status:
                item = equipment_status.copy()
                item["id"] = equipment_id
                filtered_equipment.append(item)
        
        return filtered_equipment
    
    def get_checkout_history(self, equipment_id=None, user=None, limit=None):
        """Get checkout history, optionally filtered by equipment ID or user.
        
        Args:
            equipment_id: Optional equipment ID to filter by
            user: Optional username to filter by
            limit: Optional limit on number of records to return
            
        Returns:
            List of checkout history records
        """
        history = self.checkout_history
        
        # Filter by equipment ID if specified
        if equipment_id:
            history = [record for record in history if record.get("equipment_id") == equipment_id]
        
        # Filter by user if specified
        if user:
            history = [record for record in history if record.get("user") == user]
        
        # Sort by timestamp (newest first)
        history = sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limit number of records if specified
        if limit and isinstance(limit, int) and limit > 0:
            history = history[:limit]
        
        return history
    
    def get_overdue_equipment(self):
        """Get equipment that is overdue for return.
        
        Returns:
            List of dictionaries with overdue equipment details
        """
        now = datetime.now()
        overdue = []
        
        for equipment_id, status in self.equipment_status.items():
            if status.get("status") != "Checked Out":
                continue
                
            expected_return = status.get("expected_return")
            if not expected_return:
                continue
                
            try:
                return_date = datetime.fromisoformat(expected_return)
                if return_date < now:
                    item = status.copy()
                    item["id"] = equipment_id
                    item["days_overdue"] = (now - return_date).days
                    overdue.append(item)
            except:
                # Skip if date parsing fails
                continue
        
        return overdue
    
    def authenticate_user(self, username, password):
        """Authenticate a user with username and password.

        Args:
            username: Username to authenticate
            password: Password to authenticate

        Returns:
            User dictionary if authentication succeeds, None otherwise
        """
        if username in self.users:
            user = self.users[username]
            stored_password = user.get("password", "")

            # Check if the password is stored as a hash
            if stored_password and stored_password.startswith('scrypt:'):
                if WERKZEUG_AVAILABLE:
                    try:
                        if check_password_hash(stored_password, password):
                            # Return user without password
                            user_info = user.copy()
                            user_info.pop("password", None)
                            # Add username to the user info
                            user_info["username"] = username
                            return user_info
                    except Exception as e:
                        print(f"Error checking password hash: {str(e)}")
                        # Fall back to plain text comparison
                        pass
                else:
                    # If werkzeug is not available, log a warning
                    print("Warning: Cannot verify scrypt hash without werkzeug")

            # Fall back to plain text comparison for backward compatibility
            if stored_password == password:
                # Return user without password
                user_info = user.copy()
                user_info.pop("password", None)
                # Add username to the user info
                user_info["username"] = username
                return user_info

        return None
    
    def get_user(self, username):
        """Get a user by username.
        
        Args:
            username: Username to look up
            
        Returns:
            User dictionary without password if found, None otherwise
        """
        if username in self.users:
            user_info = self.users[username].copy()
            user_info.pop("password", None)
            # Add username to the user info
            user_info["username"] = username
            return user_info
        
        return None
    
    def add_user(self, username, name, email, role, password, admin_user):
        """Add a new user.

        Args:
            username: Username for the new user
            name: Full name of the new user
            email: Email address of the new user
            role: Role of the new user ('admin', 'physicist', or 'user')
            password: Password for the new user
            admin_user: Username of the admin performing this action

        Returns:
            Boolean indicating success
        """
        # Check if admin_user is an admin
        if admin_user not in self.users or self.users[admin_user].get("role") != "admin":
            return False

        # Check if username already exists
        if username in self.users:
            return False

        # Check if role is valid - only admin and physicist roles are allowed
        if role not in ["admin", "physicist"]:
            return False

        # Hash the password if it's not already hashed
        hashed_password = password
        if password and not str(password).startswith('scrypt:'):
            if WERKZEUG_AVAILABLE:
                try:
                    hashed_password = generate_password_hash(password)
                    print(f"Password hashed successfully")
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Error hashing password: {str(e)}")
            else:
                print("Warning: Using plain text password as werkzeug is not available")

        # Add new user with notification preferences matching existing users
        if any(user.get("notification_preferences", {}).get("email_enabled") is not None for user in self.users.values()):
            # Use modern notification preference format like existing custom users
            notification_prefs = {
                "email_enabled": True,
                "calibration_due_days": 30
            }
        else:
            # Use legacy notification preference format like default users
            notification_prefs = {
                "receive_due_soon": True,
                "receive_overdue": True,
                "days_before_due": 30,
                "email_format": "html"
            }

        # Create the user entry
        self.users[username] = {
            "name": name,
            "email": email,
            "role": role,
            "password": hashed_password,
            "created_by": admin_user,
            "created_at": datetime.now().isoformat(),
            "notification_preferences": notification_prefs
        }

        # Save users
        self._save_users()

        return True
    
    def update_user(self, username, name=None, email=None, role=None, password=None, admin_user=None):
        """Update an existing user.

        Args:
            username: Username of the user to update
            name: New name (optional)
            email: New email (optional)
            role: New role (optional)
            password: New password (optional)
            admin_user: Username of the admin performing this action

        Returns:
            Boolean indicating success
        """
        # Check if admin_user is an admin (only needed for role changes)
        if role is not None and (admin_user not in self.users or self.users[admin_user].get("role") != "admin"):
            return False

        # Check if username exists
        if username not in self.users:
            return False

        # Update user
        user = self.users[username]

        if name is not None:
            user["name"] = name

        if email is not None:
            user["email"] = email

        if role is not None and role in ["admin", "physicist"]:
            user["role"] = role

        if password is not None and password.strip():
            # Hash the password if it's not already hashed
            hashed_password = password
            if not str(password).startswith('scrypt:'):
                if WERKZEUG_AVAILABLE:
                    try:
                        hashed_password = generate_password_hash(password)
                    except Exception as e:
                        print(f"Error hashing password during update: {str(e)}")
                else:
                    print("Warning: Using plain text password as werkzeug is not available")
            user["password"] = hashed_password

        user["updated_by"] = admin_user
        user["updated_at"] = datetime.now().isoformat()

        # Ensure notification preferences exist
        if "notification_preferences" not in user:
            user["notification_preferences"] = {
                "email_enabled": True,
                "calibration_due_days": 30
            }

        # Save users
        self._save_users()

        return True
    
    def delete_user(self, username, admin_user):
        """Delete a user.
        
        Args:
            username: Username of the user to delete
            admin_user: Username of the admin performing this action
            
        Returns:
            Boolean indicating success
        """
        # Check if admin_user is an admin
        if admin_user not in self.users or self.users[admin_user].get("role") != "admin":
            return False
        
        # Check if username exists
        if username not in self.users:
            return False
        
        # Don't allow deleting the last admin
        if self.users[username].get("role") == "admin":
            # Count admins
            admin_count = sum(1 for user in self.users.values() if user.get("role") == "admin")
            if admin_count <= 1:
                return False
        
        # Delete user
        del self.users[username]
        
        # Save users
        self._save_users()
        
        return True