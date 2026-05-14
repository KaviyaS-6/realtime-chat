import redis
import threading

r = redis.Redis(
    host='localhost',
    port=6379,
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