import time


def time_measure(func):
    def timed_function_wrapper(*args, **kwargs):
        start_time = time.time()  # Start time
        result = func(*args, **kwargs)
        end_time = time.time()  # End time
        execution_time = end_time - start_time  # Calculate execution time
        print(f"%%%%%%%%%%%%%%%\nExecution Time: {execution_time} seconds\n%%%%%%%%%%%%%%%")
        return result
    return timed_function_wrapper
