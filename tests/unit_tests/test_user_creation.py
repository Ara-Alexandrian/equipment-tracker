"""
Test user creation functionality
"""
import sys
import os
from app.models.json_checkout import JsonCheckoutManager

def test_user_creation():
    """Test creating a new user"""
    
    # Initialize checkout manager with test data directory
    data_dir = "app/data"
    checkout_manager = JsonCheckoutManager(data_dir)
    
    # Print existing users
    print("Existing users:")
    for username, user in checkout_manager.users.items():
        print(f" - {username}: {user.get('name')} ({user.get('role')})")
    
    # Test creating a new user
    test_username = "test_user_" + str(hash(str(os.times())))[-6:]  # Unique username
    admin_user = "admin"  # Assuming "admin" user exists
    
    print(f"\nAttempting to create test user '{test_username}' as admin '{admin_user}'")
    
    try:
        result = checkout_manager.add_user(
            username=test_username,
            name="Test User",
            email="test@example.com",
            role="user",
            password="test123",
            admin_user=admin_user
        )
        
        if result:
            print(f"SUCCESS: Created user {test_username}")
            
            # Verify user was saved
            if test_username in checkout_manager.users:
                print(f"User found in users dictionary: {checkout_manager.users[test_username]}")
            else:
                print(f"ERROR: User not found in users dictionary after creation")
        else:
            print(f"FAILED: Could not create user {test_username}")
            
            # Check common errors
            if admin_user not in checkout_manager.users:
                print(f"Admin user '{admin_user}' not found in users")
            elif checkout_manager.users[admin_user].get("role") != "admin":
                print(f"Admin user '{admin_user}' is not an admin (role: {checkout_manager.users[admin_user].get('role')})")
            elif test_username in checkout_manager.users:
                print(f"Username '{test_username}' already exists")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: Exception occurred: {str(e)}")
    
    print("\nUsers after test:")
    for username, user in checkout_manager.users.items():
        print(f" - {username}: {user.get('name')} ({user.get('role')})")

if __name__ == "__main__":
    print("Starting user creation test")
    test_user_creation()
    print("Test completed")