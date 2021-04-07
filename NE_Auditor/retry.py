"""
v1.0
"""

import logging
import os
import time

# import traceback
from functools import wraps
from typing import Union, Type, Tuple, Optional, Callable, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


def f_message(messtext: str) -> str:
    return str(messtext + " " + "*" * (os.get_terminal_size()[0] - len(messtext) - 10))


def retry(
    v_pbar,  # custom parameter
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]],
    max_retries: int = 2,
    delay: int = 1,
    delay_multiplier: int = 2,
    exc_retry_condition: Optional[Callable[[Exception], bool]] = None,
    exc_retry_bypass_action_log: bool = True,
    exc_retry_bypass_action_raise: bool = True,
) -> Callable[[T], T]:
    """
    Retry calling the decorated function using an exponential backoff.
    Args:
        v_pbar: A progress bar used by main scrypt. Custom variable.
        exceptions: A single or a tuple of Exceptions to trigger retry
        max_retries: Number of times to retry before failing.
        delay: Initial delay between retries in seconds.
        delay_multiplier: Delay multiplier (e.g. value of 2 will double the delay
            each retry).
        exc_retry_condition: A function where a raised exception will be passed
            as an argument. It checks if the retry mechanism should be bypassed
        exc_retry_bypass_action_log: when the exception retry condition is
            set but not satisfied, where a log message should be emitted
        exc_retry_bypass_action_raise: when the exception retry condition is
            set but not satisfied, where an exception should be emitted
    """

    def _retry_deco(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            attempt_num = 0
            mdelay = delay
            while attempt_num < max_retries:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    if exc_retry_condition is not None and not exc_retry_condition(e):
                        if exc_retry_bypass_action_log:
                            logger.error(
                                "Exception occurred for which retry is bypassed:",
                                exc_info=True,
                            )
                        if exc_retry_bypass_action_raise:
                            raise
                        else:
                            return
                    attempt_num += 1
                    ip: str = args[1]["ip"]
                    messtext: str = f" WARNING [ {ip} : Retry attempt #{attempt_num}/{max_retries} in {mdelay} seconds ]"
                    logger.warning(f_message(messtext))
                    time.sleep(mdelay)
                    mdelay *= delay_multiplier

            v_pbar.update()  # update pbar only after all attempts
            return f(*args, **kwargs)

        return f_retry

    return _retry_deco
