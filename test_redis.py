import redis

r = redis.Redis(
    host="prompt-wahoo-125619.upstash.io",
    port=6379,
    password="gQAAAAAAAeqzAAIgcDJhY2MzZTFiMDMzMzI0NDk3OTY1OWRmOWRiMDM3ZjU0Zg",
    ssl=True,
    decode_responses=True
)

print(r.ping())