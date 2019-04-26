import os
import random
import time
from pprint import pprint

__all__ = ['RateLimiter', 'RateLimitExceeded']

class RateLimitExceeded(Exception):
    pass

class RateLimiter(object):
    """Adds a limit() method to a class
    """

    BATCH_SIZE = 1024
    BATCH_WINDOW = 60
    BATCH_PAUSE = 2.50
    BATCH_RANDOM = True

    def __init__(self, *args,
                 batch_size=BATCH_SIZE,
                 batch_window=BATCH_WINDOW,
                 batch_pause=BATCH_PAUSE,
                 batch_random=BATCH_RANDOM,
                 except_on_limit=False,
                 **kwargs):
        setattr(self, 'batch_size', batch_size)
        setattr(self, 'batch_window', batch_window)
        setattr(self, 'batch_pause', batch_pause)
        setattr(self, 'batch_random', batch_random)
        setattr(self, 'start_time', None)
        setattr(self, 'current_time', None)
        setattr(self, 'count', 0)
        setattr(self, 'except_on_limit', except_on_limit)

    def limit(self, increment=True):
        """Enforce a rate limit

        Args:
            increment (bool, optional): Whether to increase the usage count

        Raises:
            RateLimitExceeded: This is raised when the usage rate is exceeded
                and ``except_on_limit`` is True

        Returns:
            bool: Always returns True

        """
        count = getattr(self, 'count')
        current_time = time.time()
        start_time = getattr(self, 'start_time')
        if start_time is None:
            setattr(self, 'start_time', current_time)
        setattr(self, 'current_time', current_time)
        if increment:
            count = count + 1
        setattr(self, 'count', count)

        # if count is smaller than batch_size
        # then it's always OK to return True
        if count <= getattr(self, 'batch_size'):
            # print('RATELIMITER: OK ({})'.format(self.remaining))
            return True
        # If sufficient time has passed, it's OK to return True
        # but make sure to reset the timer/counter
        elif (current_time - getattr(self, 'start_time')) > getattr(self, 'batch_window'):
            self.reset_limit()
            return True
        # Sleep for a bit, randomizing if needed. Reset counter, then proceed
        else:
            if self.except_on_limit:
                raise RateLimitExceeded(
                    'Rate limit of {} calls/{} sec. exceeded. Try again in {} sec.'.format(self.batch_size, self.batch_window, self.remaining_time))
            else:
                sleep_seconds = getattr(self, 'batch_pause', 0)
                if getattr(self, 'batch_random'):
                    sleep_seconds = random.random() * sleep_seconds
                # print('RATELIMITER: SLEEP for {} sec'.format(sleep_seconds))
                time.sleep(sleep_seconds)
                self.reset_limit()
                return True

    @property
    def elapsed(self):
        """Time in seconds elapsed in current rate-limiting window
        """
        return self.current_time - self.start_time

    @property
    def remaining(self):
        """A tuple of time and calls remaining
        """
        return self.remaining_time, self.remaining_calls

    @property
    def remaining_calls(self):
        """How many metered calls remain
        """
        return self.batch_size - self.count

    @property
    def remaining_time(self):
        """How long until the current limiting window expires
        """
        return self.batch_window - self.elapsed

    def reset_limit(self):
        """Reset rate limiter to default state
        """
        setattr(self, 'start_time', time.time())
        setattr(self, 'current_time', time.time())
        setattr(self, 'count', 0)

