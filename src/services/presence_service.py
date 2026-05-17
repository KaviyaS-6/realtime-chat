import redis
import os

# ---------------- REDIS CONNECTION ----------------

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=True,
    decode_responses=True
)

# ==================================================
# REDIS ONLINE USERS
# ==================================================

# ---------------- ADD ONLINE USER ----------------
def add_online_user(room_id, user_id):

    redis_client.sadd(
        f"online_users:{room_id}",
        user_id
    )


# ---------------- REMOVE ONLINE USER ----------------
def remove_online_user(room_id, user_id):

    redis_client.srem(
        f"online_users:{room_id}",
        user_id
    )


# ---------------- GET ONLINE USERS ----------------
def get_online_users(room_id):

    return list(
        redis_client.smembers(
            f"online_users:{room_id}"
        )
    )


# ==================================================
# IN-MEMORY ACTIVE USERS
# ==================================================

active_users = {}


# ---------------- USER JOIN ----------------
def user_join(room_id, user_id):

    if room_id not in active_users:

        active_users[room_id] = set()

    active_users[room_id].add(user_id)


# ---------------- USER LEAVE ----------------
def user_leave(room_id, user_id):

    if room_id in active_users:

        active_users[room_id].discard(user_id)

        # remove empty room
        if not active_users[room_id]:

            del active_users[room_id]


# ---------------- GET USERS ----------------
def get_users(room_id):

    return list(
        active_users.get(room_id, [])
    )