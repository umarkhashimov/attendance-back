from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017"

# Create client
client = AsyncIOMotorClient(MONGO_URI)
db = client["auth"]
users_collection = db["users"]


async def add_user(contact, user) -> bool:

    try:
        data = {
            "first_name": contact['first_name'],
            "last_name": contact['last_name'],
            "username": user.username,
            "phone_number": contact['phone_number'],
            "tg_id": contact['user_id'],
            "created_at": datetime.utcnow(),
        }

        await users_collection.update_one(
            {"tg_id": contact['user_id']},
            {"$set": data},
            upsert=True
        )
    except Exception as error:
        return False
    else:
        return True



async def get_user(tg_id):

    user = await db['users'].find_one({"tg_id": tg_id})
    return user