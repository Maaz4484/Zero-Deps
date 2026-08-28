"""
In-Memory Storage Engine Core
=============================
Zero-dependency, thread-safe in-memory key-value storage engine.

Features:
- Primary dictionary-based key-value store
- Dedicated TTL expiry tracking dictionary
- Lazy TTL expiration on access
- Thread safety via threading.RLock
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List, Optional


class StorageEngine:
    """
    In-memory key-value storage engine with TTL expiry support and thread-safety.
    """

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._lock = threading.RLock()

    def _is_expired(self, key: str, now: Optional[float] = None) -> bool:
        """Helper to check if a key has exceeded its expiration timestamp."""
        if key not in self._expiry:
            return False
        if now is None:
            now = time.time()
        return self._expiry[key] <= now

    def _purge_if_expired(self, key: str, now: Optional[float] = None) -> bool:
        """
        Lazily evicts key if expired.
        Returns True if evicted, False otherwise.
        """
        if self._is_expired(key, now):
            self._data.pop(key, None)
            self._expiry.pop(key, None)
            return True
        return False

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """
        Stores key-value pair with optional TTL in seconds.
        Returns True on success.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")

        with self._lock:
            if ttl is not None and ttl <= 0:
                # Setting with non-positive TTL expires/deletes the key immediately
                self._data.pop(key, None)
                self._expiry.pop(key, None)
                return True

            self._data[key] = value
            if ttl is not None:
                self._expiry[key] = time.time() + ttl
            else:
                self._expiry.pop(key, None)

            return True

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves the value for key.
        Returns None if key does not exist or has expired.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")

        with self._lock:
            if self._purge_if_expired(key):
                return None
            return self._data.get(key)

    def delete(self, key: str) -> bool:
        """
        Deletes key from storage.
        Returns True if the key was present and unexpired, False otherwise.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")

        with self._lock:
            if self._purge_if_expired(key):
                return False

            if key in self._data:
                self._data.pop(key, None)
                self._expiry.pop(key, None)
                return True

            return False

    def exists(self, key: str) -> bool:
        """
        Checks whether key exists and is unexpired.
        Returns True/False.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")

        with self._lock:
            if self._purge_if_expired(key):
                return False
            return key in self._data

    def expire(self, key: str, ttl: float) -> bool:
        """
        Sets or updates the TTL (in seconds) for an existing key.
        Returns True if key exists and was updated, False otherwise.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")

        with self._lock:
            if self._purge_if_expired(key) or key not in self._data:
                return False

            if ttl <= 0:
                self._data.pop(key, None)
                self._expiry.pop(key, None)
                return True

            self._expiry[key] = time.time() + ttl
            return True

    def ttl(self, key: str) -> Optional[float]:
        """
        Returns remaining TTL in seconds.
        - Returns float > 0 for remaining time
        - Returns -1 for key with no TTL
        - Returns None for missing or expired key
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be a string, got {type(key).__name__}")

        with self._lock:
            if self._purge_if_expired(key) or key not in self._data:
                return None

            if key not in self._expiry:
                return -1

            remaining = self._expiry[key] - time.time()
            return max(0.0, remaining)

    def keys(self) -> List[str]:
        """
        Returns a list of all active, unexpired keys.
        """
        with self._lock:
            now = time.time()
            expired_keys = [k for k, exp in self._expiry.items() if exp <= now]
            for k in expired_keys:
                self._data.pop(k, None)
                self._expiry.pop(k, None)

            return list(self._data.keys())

    def flush(self) -> bool:
        """
        Clears all data and expiry entries.
        Returns True.
        """
        with self._lock:
            self._data.clear()
            self._expiry.clear()
            return True
