#Clarifying Questions

#Per-client or global? (per client/IP)
#Rate & burst: e.g. 5 rps with burst up to 10?
#Single process vs. distributed? (single-node in-memory OK)
#Precision: milliseconds or seconds?
#Error handling: queue or reject immediately? (we’ll reject when no tokens)

"""
We implement a classic Token-Bucket: each client has a bucket with a max capacity (burst) and a refill rate (tokens/sec).
On each request, we refill tokens based on elapsed time, then consume one if available—otherwise reject.
Our RateLimiter holds a thread-safe map of <clientId → TokenBucket>, so concurrency is safe and per-client usage is isolated.
It’s O(1) per request, easy to test, and you can swap in a Redis-backed store in future.”
"""

#TokenBucket

import threading
import time
from collections import defaultdict

class TokenBucket:
    """Tracks tokens for a single client."""
    def __init__(self, rate: float, capacity: float):
        """
        rate: tokens added per second
        capacity: max tokens in bucket (burst size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()

    def allow_request(self) -> bool:
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            # Refill tokens based on elapsed time
            refill_amount = elapsed * self.rate
            if refill_amount > 0:
                self.tokens = min(self.capacity, self.tokens + refill_amount)
                self.last_refill = now
             # If we have at least one token, consume it and allow
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False        # Otherwise, reject the request

class RateLimiter:
    """Manages TokenBuckets for all clients. (In-memory, per-key token-bucket rate limiter.
    Defaults to the same rate/capacity for all clients.)"""
    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self.buckets = defaultdict(lambda: TokenBucket(rate, capacity))
        self.lock = threading.Lock()

    def allow_request(self, client_id: str) -> bool:
        """
        Returns True if the request from client_id is allowed,
        otherwise False (rate limit exceeded).
        """
        # ensure thread‐safe access to the bucket map
        with self.lock:
            bucket = self.buckets[client_id]
            if bucket is None:
                bucket = TokenBucket(self.rate, self.capacity)
                self.buckets[client_id] = bucket
        return bucket.allow_request()

# --- Example usage ---

if __name__ == "__main__":
    rl = RateLimiter(rate=5, capacity=10)   # 5 tokens/sec, burst up to 10

    client = "user-123"
    # simulate 12 immediate requests:
    for i in range(12):
        ok = rl.allow_request(client)
        print(f"Req {i+1}: {'Allowed' if ok else 'Rejected'}")
        time.sleep(0.1)  # small delay so refill can happen slowly


        """
How it works (interview-style summary):

TokenBucket: 
    Tracks tokens and last refill timestamp.
    On each allow_request(), it first “refills” tokens at rate tokens/sec (capped at capacity), then consumes one if available.

RateLimiter:
    Maintains a map of client-ID → TokenBucket.
    On each incoming request, it looks up (or creates) the bucket for that client and asks it if a token can be consumed.

Why Token Bucket & not fixed window?
    Allows short bursts up to capacity, then smooths over time at the configured rate.

Thread Safety:
    Each bucket has its own lock for refill/consume.
    The top-level map is also locked when creating new buckets.

This simple design is easily extended to per-endpoint limits, different rates per client, or persisting state for a distributed system.
        """