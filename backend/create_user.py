import asyncio
from passlib.context import CryptContext

from app.database import users_collection

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False
)

ADMIN_EMAIL = "demosaferoute@gmail.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_NAME = "SafeRoute Admin"


async def create_admin():

    existing = await users_collection.find_one(
        {
            "email": ADMIN_EMAIL
        }
    )

    if existing:
        print("Admin already exists")
        return

    admin = {

        "name": ADMIN_NAME,

        "email": ADMIN_EMAIL,

        "password": pwd_context.hash(ADMIN_PASSWORD),

        "role": "admin",

        "emergency_contacts": [],

        "created_at": None

    }

    await users_collection.insert_one(admin)

    print("Admin account created successfully")


asyncio.run(create_admin())