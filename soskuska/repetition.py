"""Transparent flashcard review rules, independent of Tk and SQLite.

Custom deterministic intervals, not an implementation of SM-2 or FSRS.
"""
import math
import unicodedata
from datetime import timedelta

RATINGS = ("Again", "Hard", "Good", "Easy")


def deck_fields(name, description=""):
    name = " ".join(name.split())
    description = description.strip()
    if not 1 <= len(name) <= 120:
        raise ValueError("Enter a deck name between 1 and 120 characters.")
    if len(description) > 1000:
        raise ValueError("Keep the description within 1,000 characters.")
    return name, unicodedata.normalize("NFKC", name).casefold(), description


def card_fields(front, back):
    front, back = front.strip(), back.strip()
    if not 1 <= len(front) <= 2000:
        raise ValueError("Enter a front between 1 and 2,000 characters.")
    if not 1 <= len(back) <= 4000:
        raise ValueError("Enter a back between 1 and 4,000 characters.")
    return front, back


def next_review(interval_days, rating, now):
    if type(interval_days) is not int or not 0 <= interval_days <= 365:
        raise ValueError("Invalid review interval.")
    if rating not in RATINGS:
        raise ValueError("Choose Again, Hard, Good or Easy.")
    if rating == "Again":
        return now + timedelta(minutes=10), 0, "10m"
    if rating == "Hard" and interval_days == 0:
        return now + timedelta(hours=1), 0, "1h"
    if interval_days == 0:
        days = 1 if rating == "Good" else 4
    else:
        factor = {"Hard": 1.2, "Good": 2.5, "Easy": 3.5}[rating]
        days = min(365, max(1, math.ceil(interval_days * factor)))
    return now + timedelta(days=days), days, f"{days}d"
