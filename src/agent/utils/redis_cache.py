import hashlib
import json
import redis

r = redis.Redis(host="redis", port=6379, decode_responses=True)

MAX_CACHE = 50
KEY_PREFIX = "llm_cache:"

def _hash_key(key: str) -> str:
    return KEY_PREFIX + hashlib.sha256(key.encode()).hexdigest()

def get_from_cache(query: str) -> dict | None:
    key = _hash_key(query)
    data = r.get(key)
    return json.loads(data) if data else None

def save_to_cache(query: str, answer: dict):
    key = _hash_key(query)
    r.set(key, json.dumps(answer))
    # Trim to MAX_CACHE length
    r.lpush(KEY_PREFIX + "keys", key)
    r.ltrim(KEY_PREFIX + "keys", 0, MAX_CACHE - 1)

    # Delete older keys if too many
    current_keys = r.lrange(KEY_PREFIX + "keys", MAX_CACHE, -1)
    for old_key in current_keys:
        r.delete(old_key)
