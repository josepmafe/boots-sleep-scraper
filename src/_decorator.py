import logging
import functools
import time
import re

logger = logging.getLogger(__name__)

def retry(func = None, *, exceptions = Exception, n_tries = 3, delay = 1, max_delay = 5, backoff = 1):
    """
    Decorator to re-execute a function `func` if it raises any error up to `n_tries` times.
    It can be used in either of the following ways
    ```
        @retry                                                                  # as a decorator
        def dummy():
            pass

        @retry()                                                                # as a decorator factory
        def dummy():
            pass

        @retry(exceptions = (CustomException1, CustomException2), n_tries = 4)  # as a decorator with arguments
        def dummy():
            pass
    ```
    Parameters
    ----------
    func:
        the decorated function. one must NOT pass this parameter, but it is
        needed for the decorator to accept optional parameters with no 
        parenthesis with its current construction
    exceptions: exception or tuple
        an exception or a tuple of exceptions to catch. default: Exception.
    n_tries: int
        the maximum number of attempts. default: 3.
    delay: int or float
        initial delay between attempts. default: 1
    max_delay: int or float
        maximum value of delay between attemps. default: 5
    backoff: int or float
        multiplier applied to delay between attempts. default: 1 (no backoff)
          
    Raises
    ------
    Exception
        the catched exception (one of `exeptions`), if it is still raised after
        `n_tries` attemps 
    """
    if func is None:
        kwargs = dict(exceptions=exceptions, n_tries=n_tries, delay=delay, max_delay=max_delay, backoff=backoff)
        return functools.partial(retry, **kwargs)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        n = 1
        while n <= n_tries:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                err = e # store the error, just in case it need to be re-raised
                
                # selenium exceptions are extremely verbose, but its stacktrace
                # does not offer relevant information within the decorator
                if 'selenium' in str(e.__class__):
                    e_msg = f'{type(e).__name__}'
                else:
                    e_msg = f'{type(e).__name__}: {e}'

                sleep_time = min(delay*(backoff**n), max_delay)
                logger_msg = (
                    f'execution of {func.__name__!r} failed on retry #{n} due to '
                    f'{e_msg} ; retrying in {sleep_time} seconds'
                )
                logger.warning(re.sub(r'\s+', ' ', logger_msg))

                time.sleep(sleep_time)
                
                n += 1
        logger.error(f"max retries reached during the execution of {func.__name__!r}.")
        raise err # re-raise the error, to recover its traceback
    
    return wrapper
