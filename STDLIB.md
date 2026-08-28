# Python Standard Library Architecture & Reference

## Overview

The **Zero-Deps Storage Engine** is built strictly using the **Python Standard Library**. It requires no external third-party dependencies (`pip install`), binary wheels, or native C/C++ compiler toolchains.

This document details:
1. Conventional third-party packages versus standard library alternatives.
2. Standard library modules utilized in the implementation.
3. The design rationale for a zero-dependency architecture.
4. Core API, WAL record specification, crash recovery, and TTL behaviors.

---

## 1. External Dependencies vs. Standard Library Alternatives

In typical production ecosystems, projects rely on heavy third-party packages for persistence, caching, and scheduling. This project replaces them entirely with lightweight, native standard library constructs:

| Domain | Typical External Libraries | Zero-Deps Standard Library Alternative | Rationale & Trade-offs |
| :--- | :--- | :--- | :--- |
| **Persistent Key-Value Storage** | `plyvel` (LevelDB), `rocksdb`, `lmdb`, `pydantic` | In-memory `dict` + Append-Only **Write-Ahead Log (WAL)** via `open()`, `pathlib`, `os` | Avoids C-extension compilation, platform-dependent binaries, and complex native dependencies while achieving full crash durability. |
| **Disk-Backed Caching** | `diskcache`, `redis-py`, `shelve` / `dbm` | JSON Lines WAL (`json` + `os.fsync`) with in-memory active cache | Zero-install portability, human-readable log auditing, and immediate `fsync` persistence without database server daemons. |
| **Background / Scheduled Expiry** | `APScheduler`, `schedule`, `celery` | **Deterministic Lazy Expiration** on access via `time.time()` | Eliminates background daemon thread overhead, timer resource leaks, and lock contention. Expirations evaluate on-demand during reads and key queries. |

---

## 2. Python Standard Library Modules Used

### `os` & `pathlib` (File I/O, Paths, and Durability)
- **`pathlib.Path`**: Cross-platform path resolution, directory validation, and file creation.
- **`os.fsync(fileno)`**: Forces OS buffer flushes to physical disk immediately after every WAL write, ensuring true durability (ACID write-ahead logging).

### `json` (WAL Record Serialization)
- **`json.dumps` / `json.loads`**: Encodes and decodes state mutations in **JSON Lines (`.jsonl`)** format.
- Structured, append-friendly, and interoperable for easy auditing and parsing.

### `threading` (`threading.RLock`)
- **`threading.RLock`**: Re-entrant mutual exclusion lock ensuring strict thread-safety across concurrent reader and writer threads.
- Enables safe composite operations (e.g., checking expiry and mutating internal dictionaries within the same locked context).

### `time` (`time.time()`)
- **`time.time()`**: Provides high-resolution Unix timestamps for:
  - Storing absolute expiration deadlines ($T_{\text{expire}} = \text{ts} + \text{ttl}$).
  - Calculating exact remaining TTL values dynamically.
  - Recording event timestamps in WAL entries.

### Expiration Strategy: Lazy Expiration (No Background Timers)
- **Design Choice**: Rather than spawning `threading.Timer` objects or maintaining background scavenger threads—which introduce thread-lifecycle management issues and locking contention—the engine uses **lazy eviction**.
- **Mechanics**:
  - Keys are evaluated against `time.time()` whenever `get()`, `exists()`, `expire()`, `ttl()`, or `delete()` is called.
  - When `keys()` is invoked, expired entries are purged dynamically before returning the active set.
  - During WAL recovery, expired keys are identified and excluded during startup replay.

---

## 3. Why Zero External Dependencies?

1. **Total Portability**: Runs out-of-the-box on standard Python 3.8+ across Windows, macOS, Linux, BSD, and resource-constrained environments (e.g., Alpine containers, AWS Lambda, microVMs) without compilation errors.
2. **Zero Supply-Chain Risk**: Eliminates third-party vulnerability surfaces, dependency conflicts, package deprecations, and transitive dependency bloat.
3. **Instant Startup & Minimal Footprint**: Zero import overhead from heavy packages, ensuring sub-millisecond cold starts and minimal memory usage.
4. **Auditability & Simplicity**: The entire storage and durability subsystem is self-contained, transparent, and easy to inspect.

---

## 4. Storage Engine Architecture & Specification

### Public API Reference

The `StorageEngine` exposes the following thread-safe public API:

```python
from storage_engine import StorageEngine

# In-memory only:
engine = StorageEngine()

# With persistent Write-Ahead Log (WAL) & recovery:
engine = StorageEngine(wal_path="data/store.wal")
```

| Method | Signature | Return Value | Description |
| :--- | :--- | :--- | :--- |
| `set` | `set(key: str, value: Any, ttl: Optional[float] = None) -> bool` | `True` | Stores key-value pair with optional TTL (seconds). |
| `get` | `get(key: str) -> Optional[Any]` | `value` or `None` | Retrieves stored value if present and unexpired; otherwise `None`. |
| `delete` | `delete(key: str) -> bool` | `True` / `False` | Deletes key; returns `True` if key existed, `False` if missing/expired. |
| `exists` | `exists(key: str) -> bool` | `True` / `False` | Checks if key exists and is unexpired. |
| `expire` | `expire(key: str, ttl: float) -> bool` | `True` / `False` | Updates TTL on existing key; returns `False` if missing/expired. |
| `ttl` | `ttl(key: str) -> Optional[float]` | `float`, `-1`, or `None` | Returns remaining seconds (`> 0`), `-1` if no TTL, or `None` if missing/expired. |
| `keys` | `keys() -> List[str]` | `list` of strings | Returns all non-expired active keys. |
| `flush` | `flush() -> bool` | `True` | Clears all data and expiry entries. |
| `close` | `close() -> None` | `None` | Flushes, syncs, and closes the underlying WAL handle. |

---

### WAL Record Format (JSON Lines)

Each write-ahead log record is appended as a single JSON object terminated by a newline (`\n`):

```jsonl
{"op":"SET","key":"user:100","value":{"name":"Alice"},"ttl":3600.0,"ts":1756414950.123}
{"op":"EXPIRE","key":"user:100","ttl":600.0,"ts":1756414952.456}
{"op":"DELETE","key":"user:100","ts":1756414954.789}
{"op":"FLUSH","ts":1756414955.012}
```

- **`op`**: State mutation operation (`SET`, `DELETE`, `EXPIRE`, `FLUSH`).
- **`key`**: String key target.
- **`value`**: Serializable payload (for `SET`).
- **`ttl`**: Optional expiration time in seconds (for `SET` and `EXPIRE`).
- **`ts`**: Unix timestamp when the operation was committed.

---

### Crash Recovery & Replay Semantics

When `StorageEngine(wal_path=...)` initializes with an existing WAL file:
1. **Strict Sequential Replay**: Replays records in file order from top to bottom.
2. **TTL Reconstruction**: Calculates absolute expiration time as $T_{\text{expire}} = \text{ts} + \text{ttl}$. If $T_{\text{expire}} \le T_{\text{recovery}}$, the expired key is dropped.
3. **No Double-Logging**: Replay populates in-memory state directly without writing duplicate entries back to the WAL.
4. **Torn-Write Resilience**: If an uncommitted / truncated record exists at EOF due to an interrupted write, recovery safely discards the partial tail and cleans the file boundary.
5. **Corruption Detection**: Malformed records prior to the final record raise a `ValueError` to prevent loading corrupted logs.
6. **Seamless Continuity**: Subsequent write operations continue appending to the active log.

---

### TTL & Expiration Behavior

- **Relative to Absolute**: TTL arguments (seconds from now) are converted to absolute timestamps internally (`time.time() + ttl`).
- **Passive Eviction**: Expired keys are evicted on-demand when queried (`get`, `exists`, `ttl`, `delete`, `expire`).
- **Full Sweep on Query**: Calling `keys()` sweeps and evicts all expired keys before returning active keys.
- **Immediate Eviction on Non-Positive TTL**: Setting `ttl <= 0` in `set()` or `expire()` evicts the key immediately.
