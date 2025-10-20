import redis

from app import config

_global_redis_obj = None


def init() -> None:
    global _global_redis_obj

    _global_redis_obj = redis.from_url(config.config["redis"]["db_url"])


def get(key: str) -> str | None:
    global _global_redis_obj

    try:
        return _global_redis_obj.get(key).decode()
    except:
        return None


def set(key: str, value: str | int | float, ex: int = None) -> bool:
    global _global_redis_obj

    try:
        return _global_redis_obj.set(key, value, ex=ex)
    except:
        return False


def exists(key: str) -> bool:
    global _global_redis_obj

    return _global_redis_obj.exists(key) > 0


def delete(key: str) -> None:
    global _global_redis_obj

    _global_redis_obj.delete(key)
