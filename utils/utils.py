import time


def stopwatch(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        seconds = int(elapsed_time)
        milliseconds = round((elapsed_time - seconds) * 1000)
        print(f"Execution time of {func.__name__} is {f'{seconds} s. and ' if seconds > 0 else ''}{milliseconds} ms.")
        return result
    return wrapper


def dictify_list_with_ids(incoming_list: list) -> dict:
    return {d['id']: d for d in incoming_list}
