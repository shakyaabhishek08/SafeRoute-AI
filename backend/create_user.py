import asyncio
import getpass

from app.auth import hash_password
from app.database import users_collection


# -------------------------------------------------------
# Create User
# -------------------------------------------------------

async def create_user():
    print("\n==============================")
    print("   SafeRoute AI - Create User")
    print("==============================\n")

    name = input("Enter name: ").strip()
    email = input("Enter email: ").strip().lower()
    password = getpass.getpass("Enter password: ")

    if not name:
        print("Error: Name cannot be empty.")
        return

    if not email:
        print("Error: Email cannot be empty.")
        return

    if not password:
        print("Error: Password cannot be empty.")
        return

    # Check whether user already exists
    existing_user = await users_collection.find_one(
        {"email": email}
    )

    if existing_user:
        print("Error: User with this email already exists.")
        return

    # Create user
    user = {
        "name": name,
        "email": email,
        "password": hash_password(password),
        "role": "user",
        "emergency_contacts": []
    }

    result = await users_collection.insert_one(user)

    print("\nUser created successfully.")
    print(f"User ID: {result.inserted_id}")
    print(f"Email: {email}")
    print("Role: user")


# -------------------------------------------------------
# Run Script
# -------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(create_user())