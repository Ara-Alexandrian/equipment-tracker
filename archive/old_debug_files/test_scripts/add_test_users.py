#!/usr/bin/env python3
"""
Script to add test users to the Equipment Tracker system
"""
import os
import json
from werkzeug.security import generate_password_hash

# Configuration
DATA_DIR = 'app/data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Test users to add
TEST_USERS = [
    {
        'username': 'aalexandrian',
        'name': 'Ara Alexandrian',
        'email': 'aalexandrian@marybird.com',
        'role': 'admin',
        'password': 'password123'
    },
    {
        'username': 'echorniak',
        'name': 'Ericka Chorniak',
        'email': 'echorniak@marybird.com',
        'role': 'admin',
        'password': 'password123'
    },
    {
        'username': 'astam',
        'name': 'Angela Stam',
        'email': 'astam@marybird.com',
        'role': 'admin',
        'password': 'password123'
    },
    {
        'username': 'amcguffey',
        'name': 'Andrew McGuffey',
        'email': 'amcguffey@marybird.com',
        'role': 'admin',
        'password': 'password123'
    }
]

def main():
    """Add test users to the system"""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Load existing users
    users = {}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
            users = {}
    
    # Add or update test users
    for user in TEST_USERS:
        username = user['username']
        # Hash the password
        password_hash = generate_password_hash(user['password'])
        
        # Create user entry
        users[username] = {
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'password': password_hash,
            'notification_preferences': {
                'email_enabled': True,
                'calibration_due_days': 30
            }
        }
    
    # Save users back to file
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        print(f"Successfully saved {len(TEST_USERS)} test users to {USERS_FILE}")
    except Exception as e:
        print(f"Error saving users: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()