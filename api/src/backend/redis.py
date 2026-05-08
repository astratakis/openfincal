"""
This module provides a Redis client with connection pooling for efficient
interaction with a Redis server. It includes methods for setting, getting, and deleting
values in Redis, with error handling to raise a BadGatewayError in case of connection issues
or other exceptions.
"""

import json
import logging

import redis
from src.config import config
from src.exceptions import BadGatewayError


class RedisClient:
    """
    A Redis client that uses a connection pool for efficient resource management.
    """

    _pool = None

    @classmethod
    def _initialize_redis(cls):
        cls._pool = redis.ConnectionPool(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=2,
            decode_responses=True,
            max_connections=10,
        )
        logging.info("Initialized Redis connection pool")
        return cls._pool

    def set(self, key, value):
        """Set a value in Redis using a connection from the pool."""
        try:
            if self._pool is None:
                self._initialize_redis()
            conn = redis.Redis(connection_pool=self._pool)
            if isinstance(value, dict):
                conn.set(key, json.dumps(value))
            else:
                conn.set(key, value)
        except Exception as e:
            logging.error("Error setting key in Redis: %s", e)
            raise BadGatewayError(detail="Failed to connect to Redis") from e

    def get(self, key):
        """Get a value from Redis using a connection from the pool."""
        try:
            if self._pool is None:
                self._initialize_redis()
            conn = redis.Redis(connection_pool=self._pool)
            value = conn.get(key)
            try:
                return json.loads(value)  # Attempt to deserialize JSON string
            except (TypeError, json.JSONDecodeError):
                return value  # Return as-is if not JSON
        except Exception as e:
            logging.error("Error getting key from Redis: %s", e)
            raise BadGatewayError(detail="Failed to connect to Redis") from e

    def delete(self, key):
        """Delete a value from Redis using a connection from the pool."""
        try:
            if self._pool is None:
                self._initialize_redis()
            conn = redis.Redis(connection_pool=self._pool)
            conn.delete(key)
        except Exception as e:
            logging.error("Error deleting key from Redis: %s", e)
            raise BadGatewayError(detail="Failed to connect to Redis") from e


# Create a singleton instance of RedisClient
REDIS = RedisClient()
