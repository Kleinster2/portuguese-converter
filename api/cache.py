from typing import Optional, Any
import time
from collections import OrderedDict
import threading

class TTLCache:
    """Thread-safe cache with time-to-live for entries."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if it exists and hasn't expired."""
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp <= self.ttl:
                    # Move to end to mark as recently used
                    self._cache.move_to_end(key)
                    return value
                else:
                    # Remove expired entry
                    del self._cache[key]
            return None

    def put(self, key: str, value: Any) -> None:
        """Add value to cache with current timestamp."""
        with self._lock:
            # Remove oldest entry if at max size
            if len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
            self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all entries from cache."""
        with self._lock:
            self._cache.clear()

    def remove_expired(self) -> None:
        """Remove all expired entries from cache."""
        current_time = time.time()
        with self._lock:
            # Create list of expired keys
            expired = [
                k for k, (_, ts) in self._cache.items()
                if current_time - ts > self.ttl
            ]
            # Remove expired entries
            for k in expired:
                del self._cache[k]

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache and hasn't expired."""
        with self._lock:
            if key in self._cache:
                _, timestamp = self._cache[key]
                if time.time() - timestamp <= self.ttl:
                    return True
                else:
                    # Remove expired entry
                    del self._cache[key]
            return False
