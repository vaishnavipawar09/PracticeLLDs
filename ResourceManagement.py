# 🔍 Clarifying Questions:
# 1. How many assets do we hold in memory at once? (cache capacity)
# 2. What eviction policy should we use? (e.g. LRU, FIFO)
# 3. Should asset loading be synchronous or asynchronous? (blocking get vs. background load)
# 4. Do we need to prioritize some assets? (e.g. critical ones never evict)
# 5. Is thread safety required? (concurrent requests for assets)

# ✅ Verbal Design Pitch:
# We need a simple in-memory Resource Management system that:
#  - Loads and unloads Asset objects on demand
#  - Caches up to N assets using a pluggable eviction strategy (e.g. LRU)
#  - Ensures that repeated requests for the same asset hit the cache
#  - Unloads assets when they’re evicted or explicitly released
#  - Is thread-safe for concurrent gets/releases
#
# Core Classes:
# 1. Asset               — holds id, path, size; knows how to load() and unload()
# 2. CacheStrategy       — abstract interface with cache(asset) & evict()
# 3. LRUCacheStrategy    — concrete LRU via OrderedDict
# 4. AssetManager        — singleton managing the asset cache and loading logic
from abc import ABC, abstractmethod
from collections import OrderedDict
from threading import Lock
from typing import Dict, Optional

class Asset:
    """Represents a resource (e.g., texture, file) that can be loaded/unloaded."""
    def __init__(self, asset_id: str, path: str, size: int):
        self.id = asset_id
        self.path = path
        self.size = size
        self._loaded = False

    def load(self):
        """Synchronous load from disk or network."""
        if not self._loaded:
            # (imagine disk/network I/O here)
            self._loaded = True
            print(f"[Load]   Asset {self.id} loaded from {self.path}")

    def unload(self):
        """Free up memory."""
        if self._loaded:
            self._loaded = False
            print(f"[Unload] Asset {self.id} unloaded")


class CacheStrategy(ABC):
    """Abstract interface for cache eviction strategies."""
    @abstractmethod
    def cache(self, asset: Asset):
        pass

    @abstractmethod
    def evict(self) -> Asset:
        pass


class LRUCachingStrategy(CacheStrategy):
    """LRU eviction using an OrderedDict."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict[str, Asset] = OrderedDict()

    def cache(self, asset: Asset):
        # If already cached, bump it to most-recent
        if asset.id in self.cache:
            self.cache.move_to_end(asset.id)
        else:
            # Evict if at capacity
            if len(self.cache) >= self.capacity:
                self.evict()
            self.cache[asset.id] = asset
        print(f"[Cache]  Asset {asset.id} cached ({len(self.cache)}/{self.capacity})")

    def evict(self) -> Asset:
        # Pop the oldest entry
        evicted_id, evicted_asset = self.cache.popitem(last=False)
        evicted_asset.unload()
        print(f"[Evict]  Asset {evicted_id} evicted from cache")
        return evicted_asset


class AssetManager:
    """Singleton that loads, caches, and releases assets thread‐safely."""
    _instance: Optional["AssetManager"] = None
    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init()
        return cls._instance

    def _init(self):
        self._assets: Dict[str, Asset] = {}
        self._cache_strategy: Optional[CacheStrategy] = None
        self._lock = Lock()

    def set_cache_strategy(self, strategy: CacheStrategy):
        """Configure eviction policy before any gets."""
        self._cache_strategy = strategy

    def get_asset(self, asset_id: str, path: str, size: int) -> Asset:
        """
        Returns the requested asset, loading and caching it if necessary.
        Blocks until load completes.
        """
        with self._lock:
            if asset_id in self._assets:
                asset = self._assets[asset_id]
                print(f"[Hit]    Asset {asset_id} retrieved from cache")
            else:
                asset = Asset(asset_id, path, size)
                asset.load()
                self._assets[asset_id] = asset

                if not self._cache_strategy:
                    raise RuntimeError("Cache strategy not configured")

                self._cache_strategy.cache(asset)
            return asset

    def release_asset(self, asset_id: str):
        """
        Explicitly remove an asset from cache (and unload it).
        """
        with self._lock:
            asset = self._assets.pop(asset_id, None)
            if asset:
                asset.unload()
                print(f"[Release] Asset {asset_id} released")


if __name__ == "__main__":
    manager = AssetManager()
    manager.set_cache_strategy(LRUCachingStrategy(capacity=2))

    # Load and cache three assets; capacity is 2 so the first will be evicted
    a1 = manager.get_asset("A1", "/path/to/A1", 10)
    a2 = manager.get_asset("A2", "/path/to/A2", 20)
    a3 = manager.get_asset("A3", "/path/to/A3", 15)

    # Re-access A2 to bump its recency, then load a fourth to evict A1
    a2 = manager.get_asset("A2", "/path/to/A2", 20)
    a4 = manager.get_asset("A4", "/path/to/A4", 25)

    # Explicitly release A2
    manager.release_asset("A2")
