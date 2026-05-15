import time

from django.core.cache import cache


LEATHER_JACKET_CACHE_VERSION_KEY = "albion_online:leather_jacket:version"
GATHERING_GEAR_CACHE_VERSION_KEY = "albion_online:gathering_gear:version"
ARTIFACT_SALVAGE_CACHE_VERSION_KEY = "albion_online:artifact_salvage:version"


def _invalidate_cache(cache_version_key: str):
    cache.set(cache_version_key, str(time.time()), None)


def invalidate_leather_jacket_cache():
    _invalidate_cache(LEATHER_JACKET_CACHE_VERSION_KEY)


def invalidate_gathering_gear_cache():
    _invalidate_cache(GATHERING_GEAR_CACHE_VERSION_KEY)


def invalidate_artifact_salvage_cache():
    _invalidate_cache(ARTIFACT_SALVAGE_CACHE_VERSION_KEY)
