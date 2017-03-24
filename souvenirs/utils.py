from __future__ import absolute_import, unicode_literals

import calendar
from datetime import datetime


def adjust_to_calendar_month(dt):
    """
    Return dt normalized to the start of the calendar month (day reset to 1,
    time reset to 00:00:00 local time).
    """
    return datetime(dt.year, dt.month, 1, tzinfo=dt.tzinfo)


def adjust_to_subscription_start(dt, ss):
    """
    Return dt adjusted back to the day, time and tzinfo matching ss.
    """
    new_dt = datetime.combine(
        dt.date().replace(day=nearest_dom(dt.year, dt.month, ss.day)),
        ss.timetz()
    )
    if new_dt > dt:
        new_dt = next_month(new_dt, preferred_dom=ss.day, delta=-1)
    return new_dt


def iter_months(start, end):
    """
    Generate a sequence of tuples representing the span of a month
    (month_start, month_end) where starts are inclusive and ends are exclusive
    (the end of one month is the same as the start of the next month).
    """
    preferred_dom = start.day
    while start < end:
        next_start = min(next_month(start, preferred_dom), end)
        yield start, next_start
        start = next_start


def next_month(dt, preferred_dom=None, delta=1):
    """
    Return dt adjusted to the next month, like dt + timedelta(months=delta) if
    timedelta supported that. If the current day (or preferred_dom) doesn't
    exist in the next month then the day will be adjusted to the closest
    available (for example Jan 31 -> Feb 28).
    """
    if delta == 0:
        raise ValueError("delta must be non-zero")

    # adjust month forward/backward according to delta
    next_year, next_month = dt.year, dt.month
    while delta < 0:
        next_year -= (next_month == 1)
        next_month = next_month - 1 or 12
        delta += 1
    while delta > 0:
        next_year += (next_month == 12)
        next_month = next_month % 12 + 1
        delta -= 1

    return dt.replace(
        year=next_year,
        month=next_month,
        day=nearest_dom(next_year, next_month, preferred_dom or dt.day)
    )


def nearest_dom(year, month, day):
    """
    Return day adjusted as necessary to fit within the days available in
    year/month. For example:

        nearest_dom(2017, 2, 30)  #=> 28

    """
    return min(calendar.monthrange(year, month)[1], day)
