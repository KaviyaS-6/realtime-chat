import redis
import threading
import os

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=True,
    decode_responses=True
)

def publish(channel, message):

    r.publish(channel, message)

def subscribe(channel, callback):

    pubsub = r.pubsub()

    pubsub.subscribe(channel)

    def listen():

        for msg in pubsub.listen():

            if msg["type"] == "message":

                callback(msg["data"])

    thread = threading.Thread(target=listen)

    thread.daemon = True

    thread.start()