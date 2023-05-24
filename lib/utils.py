"""Utility functions for dataset creation."""

import functools
import logging
import math
import os
import time
import re
import requests


def retry(tries: int = 2):
    """Try a function multiple times before failing."""
    def retry_decorator(func):
        @functools.wraps
        def retryable(*args, **kwargs):
            nonlocal tries
            errors = []
            result = None
            while tries > 0:
                try:
                    tries -= 1
                    result = func(*args, **kwargs)
                    break
                except Exception as e:
                    errors.append(e)
            if errors:
                return None, Exception("\n\n".join("\t" + str(e) for e in errors))
            return result, None

        return retryable(func)

    return retry_decorator


def float_to_timestamp(ts: float) -> str:
    """Convert milliseconds to a timestamp."""
    _, whole = math.modf(ts)
    time_fmt = time.strftime("%H:%M:%S", time.gmtime(whole))
    return time_fmt


def download_blob(url: str, path: str):
    """Downloads a blob of data from a url to a file path."""
    assert os.path.exists(os.path.dirname(path))
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r:
                f.write(chunk)
    else:
        print('Failed to fetch keyframe from', url, 'with status', r.status_code)


def short_yt_url(video_id: str) -> str:
    return f"http://youtu.be/{video_id}"


def sanitize(s: str):
    return re.sub(r'[\[\]/{}.,\'\"\!\?\;]+', '', s.strip().lower()).replace(' ', '_')


def make_path(*args):
    path = os.path.join(*args)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    return path


def get_logger():
    logger = logging.getLogger('msmo')
    logger.setLevel(logging.INFO)
    return logger


def parse_time(timestamp: str):
    if not re.match(r"^\d\d+\:\d{2}\:\d{2}$", timestamp):
        raise ValueError(f"Timestamp `{timestamp}` is not in expected format HH:MM:SS")
    return tuple(map(int, timestamp.split(':')))