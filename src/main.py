from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Body
)

import asyncio
import json

from datetime import datetime

from src.websocket.connection_manager import (
    ConnectionManager
)

from src.services.message_service import (
    save_message,
    get_messages,
    mark_message_seen
)

from src.services.redis_pubsub import (
    publish,
    subscribe
)

from src.services.auth_service import (
    create_token,
    verify_token
)

# UPDATED IMPORTS
from src.services.presence_service import (
    add_online_user,
    remove_online_user,
    get_online_users
)

app = FastAPI()

manager = ConnectionManager()


# ---------------- LOGIN API ----------------
@app.post("/login")
async def login(username: str = Body(...)):

    token = create_token(username)

    return {
        "token": token
    }


# ---------------- STARTUP ----------------
@app.on_event("startup")
async def startup_event():

    loop = asyncio.get_running_loop()

    def handle_message(message):

        try:

            print("REDIS RECEIVED:", message)

            room_id, text = message.split("|", 1)

            print("ROOM:", room_id)
            print("TEXT:", text)

            asyncio.run_coroutine_threadsafe(
                manager.broadcast(room_id, text),
                loop
            )

            print("BROADCAST COMPLETE")

        except Exception as e:

            print("REDIS ERROR:", e)

    subscribe("chat", handle_message)


# ---------------- WEBSOCKET ----------------
@app.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str
):

    # ---------------- GET TOKEN ----------------
    token = websocket.query_params.get("token")

    if not token:

        print("NO TOKEN")

        await websocket.close()

        return

    # ---------------- VERIFY TOKEN ----------------
    user_id = verify_token(token)

    if not user_id:

        print("INVALID TOKEN")

        await websocket.close()

        return

    print(f"AUTHENTICATED USER: {user_id}")

    # ---------------- CONNECT ----------------
    await manager.connect(room_id, websocket)

    print(f"CONNECTED TO ROOM: {room_id}")

    # ---------------- ADD ONLINE USER ----------------
    add_online_user(room_id, user_id)

    print(f"{user_id} connected to {room_id}")

    # ---------------- SEND ONLINE USERS ----------------
    online_users = get_online_users(room_id)

    online_users_data = {
        "type": "online_users",
        "users": online_users
    }

    try:

        await websocket.send_text(
            json.dumps(online_users_data)
        )

    except Exception as e:

        print("SEND ERROR:", e)
    # ---------------- ONLINE EVENT ----------------
    online_event = {
        "type": "presence",
        "user": user_id,
        "status": "online"
    }

    publish(
        "chat",
        f"{room_id}|{json.dumps(online_event)}"
    )

    # ---------------- SEND OLD MESSAGES ----------------
    old_messages = get_messages(room_id)

    for msg in old_messages:

        old_message_data = {
            "type": "message",
            "message_id": msg["message_id"],
            "user": msg["user_id"],
            "text": msg["message"],
            "seen": msg["seen"],
            "timestamp": str(msg["timestamp"])
        }

        await websocket.send_text(
            json.dumps(old_message_data)
        )

    # ---------------- MAIN LOOP ----------------
    try:

        while True:

            data = await websocket.receive_text()

            print("RAW DATA:", data)

            parsed = json.loads(data)

            print("PARSED:", parsed)

            # ---------- TYPING ----------
            if parsed["type"] == "typing":

                print("Typing Event")

                typing_data = {
                    "type": "typing",
                    "user": user_id
                }

                publish(
                    "chat",
                    f"{room_id}|{json.dumps(typing_data)}"
                )

            # ---------- MESSAGE ----------
            elif parsed["type"] == "message":

                print("Message Event")

                message_id = save_message(
                    room_id,
                    user_id,
                    parsed["text"],
                    False
                )

                message_data = {
                    "type": "message",
                    "message_id": message_id,
                    "user": user_id,
                    "text": parsed["text"],
                    "seen": False,
                    "delivered": True,
                    "timestamp": str(datetime.utcnow())
                }

                publish(
                    "chat",
                    f"{room_id}|{json.dumps(message_data)}"
                )

            # ---------- SEEN ----------
            elif parsed["type"] == "seen":

                print("Seen Event")

                message_id = parsed.get("message_id")

                if not message_id:
                    continue

                mark_message_seen(message_id)

                seen_data = {
                    "type": "seen",
                    "message_id": message_id,
                    "seen_by": user_id
                }

                publish(
                    "chat",
                    f"{room_id}|{json.dumps(seen_data)}"
                )

    # ---------------- DISCONNECT ----------------
    except WebSocketDisconnect:

        print(f"{user_id} disconnected")

        manager.disconnect(
            room_id,
            websocket
        )

        # REMOVE ONLINE USER
        remove_online_user(room_id, user_id)

        offline_event = {
            "type": "presence",
            "user": user_id,
            "status": "offline"
        }

        publish(
            "chat",
            f"{room_id}|{json.dumps(offline_event)}"
        )

    # ---------------- OTHER ERRORS ----------------
    except Exception as e:

        print("WEBSOCKET ERROR:", e)

        manager.disconnect(
            room_id,
            websocket
        )

        # REMOVE ONLINE USER
        remove_online_user(room_id, user_id)

        error_event = {
            "type": "error",
            "message": str(e)
        }

        publish(
            "chat",
            f"{room_id}|{json.dumps(error_event)}"
        )