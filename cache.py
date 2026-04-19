import redis
import json
import hashlib
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class RedisCache:
    """
    Production-ready Redis caching layer for the RAG system.
    Stores and retrieves query responses with TTL support.
    """

    def __init__(self):
        """
        Initializes Redis connection using environment variables.
        Tests connection with ping on startup.
        """
        try:
            logger.info(json.dumps({
                "event": "redis_connecting",
                "host": os.getenv("REDIS_HOST"),
                "port": os.getenv("REDIS_PORT")
            }))
            self.redis = redis.Redis(
                host=os.getenv("REDIS_HOST"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                password=os.getenv("REDIS_PASSWORD"),
                decode_responses=True
            )
            # Validate connection immediately
            self.redis.ping()
            logger.info(json.dumps({"event": "redis_connected", "status": "success"}))
        except Exception as e:
            logger.error(json.dumps({"event": "redis_connection_failed", "error": str(e)}))
            raise e

    def generate_key(self, query: str) -> str:
        """
        Generates a deterministic MD5-based cache key from the query string.
        Normalizes query to lowercase and strips whitespace before hashing.
        """
        hash_key = hashlib.md5(query.lower().strip().encode()).hexdigest()
        return f"rag:{hash_key}"

    def get(self, key: str):
        """
        Retrieves a cached response by key.
        Returns the deserialized dict on hit, or None on miss/error.
        """
        try:
            data = self.redis.get(key)

            if data:
                logger.info(json.dumps({
                    "event": "cache_hit",
                    "key": key
                }))
                return json.loads(data)

            logger.info(json.dumps({
                "event": "cache_miss",
                "key": key
            }))
            return None

        except Exception as e:
            logger.error(json.dumps({
                "event": "cache_error",
                "error": str(e)
            }))
            return None

    def set(self, key: str, value: dict, ttl: int = 3600):
        """
        Serializes and stores a response dict in Redis with a TTL.
        Default TTL is 3600 seconds (1 hour).
        """
        try:
            self.redis.setex(
                key,
                ttl,
                json.dumps(value)
            )
            logger.info(json.dumps({
                "event": "cache_store",
                "key": key,
                "ttl": ttl
            }))
        except Exception as e:
            logger.error(json.dumps({
                "event": "cache_store_error",
                "error": str(e)
            }))

    def delete(self, key: str):
        """
        Deletes a specific key from the cache.
        """
        try:
            self.redis.delete(key)
            logger.info(json.dumps({
                "event": "cache_delete",
                "key": key
            }))
        except Exception as e:
            logger.error(json.dumps({
                "event": "cache_delete_error",
                "error": str(e)
            }))


if __name__ == "__main__":
    cache = RedisCache()

    query = "What is leave policy?"
    key = cache.generate_key(query)
    print(f"Generated Key: {key}")

    # Try to retrieve
    cached = cache.get(key)

    if not cached:
        # Store on miss
        cache.set(key, {"answer": "Employees are entitled to 20 days of annual leave."})
        print("Stored response in cache.")
    else:
        print("Retrieved from cache:", cached)