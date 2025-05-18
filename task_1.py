import time
import random
from collections import deque
from typing import Dict

class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter for chat messages.

    Attributes:
        window_size (int): Size of the time window in seconds.
        max_requests (int): Maximum number of messages allowed per window.
        user_records (Dict[str, deque]): Mapping of user IDs to a deque of message timestamps.
    """
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        """
        Initialize the rate limiter.

        Args:
            window_size (int): Time window size in seconds.
            max_requests (int): Max messages allowed within the time window.
        """
        self.window_size = window_size
        self.max_requests = max_requests
        # Stores timestamps of messages per user
        self.user_records: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Remove timestamps outside the current sliding window for a user.

        Args:
            user_id (str): The ID of the user.
            current_time (float): The current timestamp.
        """
        if user_id not in self.user_records:
            return

        window = self.user_records[user_id]
        # Pop from left while the oldest timestamp is outside the window
        while window and (current_time - window[0]) >= self.window_size:
            window.popleft()

        # If no timestamps remain, remove the user's record entirely
        if not window:
            del self.user_records[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        Check if a user can send a message at the current time.

        Args:
            user_id (str): The ID of the user.

        Returns:
            bool: True if the user can send a message, False otherwise.
        """
        now = time.time()
        self._cleanup_window(user_id, now)
        # If user not in records or under the limit, can send
        return (user_id not in self.user_records
                or len(self.user_records[user_id]) < self.max_requests)

    def record_message(self, user_id: str) -> bool:
        """
        Record a new message for the user if allowed.

        Args:
            user_id (str): The ID of the user.

        Returns:
            bool: True if the message was recorded (allowed), False if rate-limited.
        """
        now = time.time()
        self._cleanup_window(user_id, now)

        if user_id not in self.user_records:
            self.user_records[user_id] = deque()

        if len(self.user_records[user_id]) < self.max_requests:
            self.user_records[user_id].append(now)
            return True

        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Calculate how many seconds until the user can send their next message.

        Args:
            user_id (str): The ID of the user.

        Returns:
            float: Seconds until the next message is allowed. Zero if already allowed.
        """
        now = time.time()
        self._cleanup_window(user_id, now)

        if user_id not in self.user_records:
            return 0.0

        window = self.user_records[user_id]
        oldest = window[0]
        elapsed = now - oldest
        wait = self.window_size - elapsed
        return max(wait, 0.0)


def test_rate_limiter():
    """
    Demonstrate the SlidingWindowRateLimiter with simulated user messages.
    """
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\n=== Simulating message stream ===")
    # First burst of 10 messages from users 1-5
    for msg_id in range(1, 11):
        user_id = str(msg_id % 5 + 1)
        allowed = limiter.record_message(user_id)
        wait = limiter.time_until_next_allowed(user_id)
        status = '✓' if allowed else f'× (wait {wait:.1f}s)'
        print(f"Message {msg_id:2d} | User {user_id} | {status}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nWaiting 4 seconds...\n")
    time.sleep(4)

    print("=== New message series after wait ===")
    for msg_id in range(11, 21):
        user_id = str(msg_id % 5 + 1)
        allowed = limiter.record_message(user_id)
        wait = limiter.time_until_next_allowed(user_id)
        status = '✓' if allowed else f'× (wait {wait:.1f}s)'
        print(f"Message {msg_id:2d} | User {user_id} | {status}")
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
