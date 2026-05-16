import redis
import threading

r = redis.Redis(
    host="prompt-wahoo-125619.upstash.io",
    port=6379,
    password="gQAAAAAAAeqzAAIgcDJhY2MzZTFiMDMzMzI0NDk3OTY1OWRmOWRiMDM3ZjU0Zg",
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