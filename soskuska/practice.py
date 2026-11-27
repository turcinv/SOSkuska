"""Practice rules and UTC deadlines, independent of desktop widgets."""
from datetime import datetime, timezone
from content import DIFFICULTIES


class MissingPracticeError(ValueError):
    """An attempt was removed; retrying completion cannot recover it."""


class PracticeChangedError(ValueError):
    """Another window changed answers after a submit/discard confirmation opened."""


def utc_now():
    return datetime.now(timezone.utc)


def practice_settings(count, minutes, difficulty):
    if type(count) is not int or not 1 <= count <= 100:
        raise ValueError("Choose between 1 and 100 questions.")
    if minutes is not None and (type(minutes) is not int or not 1 <= minutes <= 180):
        raise ValueError("Choose an untimed test or a limit of 1–180 minutes.")
    if difficulty is not None and difficulty not in DIFFICULTIES:
        raise ValueError("Choose Easy, Medium, Hard or all difficulties.")


def expired(deadline, now=None):
    return deadline is not None and (now or utc_now()) >= datetime.fromisoformat(deadline)


def seconds_left(deadline, now=None):
    if deadline is None:
        return None
    import math
    return max(0, math.ceil((datetime.fromisoformat(deadline) - (now or utc_now())).total_seconds()))
