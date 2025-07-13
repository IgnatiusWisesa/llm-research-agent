import hashlib
import json
import redis

# Connect to Redis (assumes service name is "redis" in Docker or localhost setup)
r = redis.Redis(host="redis", port=6379, decode_responses=True)

# Max number of cached items to retain
MAX_CACHE = 50

# Redis key prefix to avoid collisions with other keys
KEY_PREFIX = "llm_cache:"

def _hash_key(key: str) -> str:
    """
    Create a hashed key using SHA-256 to avoid overly long or unsafe keys.
    """
    return KEY_PREFIX + hashlib.sha256(key.encode()).hexdigest()

def get_from_cache(query: str) -> dict | None:
    """
    Retrieve a cached result (if available) from Redis using the hashed query key.
    """
    key = _hash_key(query)
    data = r.get(key)
    return json.loads(data) if data else None

def save_to_cache(query: str, answer: dict):
    """
    Save an answer to Redis cache under a hashed key.
    Also maintain an LRU-like list of recent keys with a max size limit.
    """
    key = _hash_key(query)
    r.set(key, json.dumps(answer))

    # Track recent keys in a Redis list (like LRU queue)
    r.lpush(KEY_PREFIX + "keys", key)
    r.ltrim(KEY_PREFIX + "keys", 0, MAX_CACHE - 1)

    # Delete old entries if over limit
    current_keys = r.lrange(KEY_PREFIX + "keys", MAX_CACHE, -1)
    for old_key in current_keys:
        r.delete(old_key)
