import os
import time

import psutil


def time_measure(func):
    def timed_function_wrapper(*args, **kwargs):
        start_time = time.time()  # Start time
        result = func(*args, **kwargs)
        end_time = time.time()  # End time
        execution_time = end_time - start_time  # Calculate execution time
        print(f"\n%%%%%%%%%%%%%%%\nExecution Time of {func.__module__}.{func.__name__}: {execution_time} seconds\n%%%%%%%%%%%%%%%\n")
        return result
    return timed_function_wrapper


def get_ram_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024**2  # MB


def ram_measure(func):
    def mem_tracked_function_wrapper(*args, **kwargs):
        func_info = f"{func.__module__}.{func.__name__}"
        print(f"RAM Before {func_info}: {get_ram_usage()}MB")
        result = func(*args, **kwargs)
        print(f"RAM After {func_info}: {get_ram_usage()}MB")
        return result
    return mem_tracked_function_wrapper
