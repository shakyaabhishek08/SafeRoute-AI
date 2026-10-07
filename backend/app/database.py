from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os


# -------------------------------------------------------
# Load Environment Variables
# -------------------------------------------------------

load_dotenv()


# -------------------------------------------------------
# MongoDB Configuration
# -------------------------------------------------------

MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise ValueError(
        "MONGO_URL not found in .env"
    )


# -------------------------------------------------------
# MongoDB Client
# -------------------------------------------------------

client = AsyncIOMotorClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
)


# -------------------------------------------------------
# Database
# -------------------------------------------------------

db = client["saferoute"]


# -------------------------------------------------------
# Collections
# -------------------------------------------------------

users_collection = db["users"]

incidents_collection = db["incidents"]

journeys_collection = db["journeys"]

chat_collection = db["chat_history"]

emergency_contacts_collection = db["emergency_contacts"]
