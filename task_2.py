import time
import random
from typing import Dict

class ThrottlingRateLimiter:
    """
    Throttling rate limiter that enforces a fixed minimum interval between
    consecutive messages from each user.

    Attributes:
        min_interval (float): Minimum number of seconds required between messages.
        user_last_timestamp (Dict[str, float]): Maps user IDs to the timestamp
            of their last sent message.
    """
    def __init__(self, min_interval: float = 10.0):
        """
        Initialize the throttling rate limiter.

        Args:
            min_interval (float): Minimum seconds required between two messages
                from the same user.
        """
        self.min_interval = min_interval
        self.user_last_timestamp: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        """
        Check whether the given user is allowed to send a message at the
        current time based on the throttling interval.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            bool: True if the user can send a message now, False otherwise.
        """
        now = time.time()
        # If user has never sent a message, allow immediately
        if user_id not in self.user_last_timestamp:
            return True
        # Calculate time since last message
        elapsed = now - self.user_last_timestamp[user_id]
        return elapsed >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        """
        Attempt to record a new message for the user. If the user is allowed
        (per can_send_message), update their last-message timestamp.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            bool: True if the message was allowed and recorded, False if
                  the user is still within the throttling interval.
        """
        if self.can_send_message(user_id):
            # Update timestamp of last message
            self.user_last_timestamp[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Compute how many seconds remain until the user may send their next message.

        Args:
            user_id (str): Unique identifier for the user.

        Returns:
            float: Number of seconds to wait before sending is allowed again.
                   Returns 0.0 if the user can send immediately.
        """
        now = time.time()
        if user_id not in self.user_last_timestamp:
            return 0.0
        elapsed = now - self.user_last_timestamp[user_id]
        remaining = self.min_interval - elapsed
        return max(remaining, 0.0)


def test_throttling_limiter():
    """
    Demonstrate the ThrottlingRateLimiter with simulated message traffic.
    """
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\n=== Simulating message stream (Throttling) ===")
    # First burst of 10 messages from users 1–5
    for message_id in range(1, 11):
        user_id = str(message_id % 5 + 1)
        allowed = limiter.record_message(user_id)
        wait = limiter.time_until_next_allowed(user_id)
        status = "✓" if allowed else f"× (wait {wait:.1f}s)"
        print(f"Message {message_id:2d} | User {user_id} | {status}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nWaiting 10 seconds...\n")
    time.sleep(10)

    print("=== New message series after wait ===")
    for message_id in range(11, 21):
        user_id = str(message_id % 5 + 1)
        allowed = limiter.record_message(user_id)
        wait = limiter.time_until_next_allowed(user_id)
        status = "✓" if allowed else f"× (wait {wait:.1f}s)"
        print(f"Message {message_id:2d} | User {user_id} | {status}")
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_throttling_limiter()
