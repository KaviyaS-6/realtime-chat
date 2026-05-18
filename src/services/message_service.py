from datetime import datetime
from bson import ObjectId

from src.db.mongo import messages_collection


# ---------------- SAVE MESSAGE ----------------
def save_message(
    room_id,
    user_id,
    message,
    seen=False
):

    data = {

        "room_id": room_id,

        "user_id": user_id,

        "message": message,

        "seen": seen,

        "timestamp": datetime.utcnow()
    }

    result = messages_collection.insert_one(data)

    return str(result.inserted_id)


# ---------------- GET OLD MESSAGES ----------------
def get_messages(room_id):

    messages = messages_collection.find(
        {
            "room_id": room_id
        }
    ).sort("timestamp", 1)

    result = []

    for msg in messages:

        result.append({

            "message_id": str(msg["_id"]),

            "room_id": msg["room_id"],

            "user_id": msg["user_id"],

            "message": msg["message"],

            "seen": msg.get("seen", False),

            "timestamp": str(
                msg.get("timestamp", "")
            )
        })

    return result


# ---------------- MARK SINGLE MESSAGE AS SEEN ----------------
def mark_message_seen(message_id):

    if not message_id:
        return

    try:

        messages_collection.update_one(
            {
                "_id": ObjectId(message_id)
            },
            {
                "$set": {
                    "seen": True
                }
            }
        )

    except Exception as e:

        print("SEEN UPDATE ERROR:", e)


# ---------------- MARK ALL ROOM MESSAGES AS SEEN ----------------
def mark_messages_seen(
    room_id,
    user_id
):

    messages_collection.update_many(
        {
            "room_id": room_id,

            "user_id": {
                "$ne": user_id
            },

            "seen": False
        },
        {
            "$set": {
                "seen": True
            }
        }
    )