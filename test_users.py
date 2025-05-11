"""
Test user loading for dropdowns
"""
from app.models.json_checkout import JsonCheckoutManager

def test_user_loading():
    """Test loading users for dropdowns"""
    # Initialize checkout manager with data directory
    data_dir = "app/data"
    checkout_manager = JsonCheckoutManager(data_dir)
    
    # First, try the method used in the routes
    print("Method 1: Filtering out users with password field")
    users = {username: info for username, info in checkout_manager.users.items() 
             if 'password' not in info}
    
    print(f"Found {len(users)} users with Method 1")
    if users:
        print("First few users found:")
        for i, (username, user) in enumerate(users.items()):
            if i < 5:  # Just print up to 5 users
                print(f" - {username}: {user.get('name', 'No name')}")
    else:
        print("No users found with Method 1 - this would explain empty dropdowns")
    
    # Try a different method - copying without the password field
    print("\nMethod 2: Copying users without password field")
    users2 = {}
    for username, info in checkout_manager.users.items():
        user_info = info.copy()
        if 'password' in user_info:
            user_info.pop('password')
        users2[username] = user_info
    
    print(f"Found {len(users2)} users with Method 2")
    if users2:
        print("First few users found:")
        for i, (username, user) in enumerate(users2.items()):
            if i < 5:  # Just print up to 5 users
                print(f" - {username}: {user.get('name', 'No name')}")
    
    # Check if the user dictionary has the expected structure
    print("\nChecking raw user data structure:")
    for i, (username, user_data) in enumerate(checkout_manager.users.items()):
        if i < 3:  # Just check a few users
            print(f"User: {username}")
            print(f"Keys in user data: {list(user_data.keys())}")
            print(f"Has password field: {'password' in user_data}")
            print()

if __name__ == "__main__":
    print("Testing user loading for dropdowns")
    test_user_loading()
    print("Test completed")