import functools
import time


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        begin_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - begin_time
        print('{} 共用时：{} s'.format(func.__name__, run_time))
        return value

    return wrapper
