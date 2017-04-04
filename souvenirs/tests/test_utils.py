from __future__ import absolute_import, unicode_literals

from datetime import datetime
import types
from django.utils import timezone
import pytest
from souvenirs.utils import (adjust_to_calendar_month,
                             adjust_to_subscription_start,
                             iter_days, iter_months, iter_quarters, iter_years,
                             next_month, nearest_dom)


def test_adjust_to_calendar_month():
    dt = timezone.make_aware(datetime(2017, 3, 27, 10, 36))
    assert (adjust_to_calendar_month(dt) ==
            timezone.make_aware(datetime(2017, 3, 1, 0, 0, 0, 0)))


def test_adjust_to_subscription_start():
    ss = timezone.make_aware(datetime(2017, 1, 31, 23, 30))

    # if dt matches ss, go with it
    dt = timezone.make_aware(datetime(2017, 3, 31, 23, 30))
    assert adjust_to_subscription_start(dt, ss) == dt

    # if dt is after ss, simple adjust back to ss
    dt = timezone.make_aware(datetime(2017, 3, 31, 23, 31))
    assert (adjust_to_subscription_start(dt, ss) ==
            timezone.make_aware(datetime(2017, 3, 31, 23, 30)))

    # if dt is before ss, adjust back to previous month
    dt = timezone.make_aware(datetime(2017, 3, 27, 10, 41))
    assert (adjust_to_subscription_start(dt, ss) ==
            timezone.make_aware(datetime(2017, 2, 28, 23, 30)))

    # interesting scenario of dt matching adjusted ss
    ss = timezone.make_aware(datetime(2016, 12, 31, 12, 0))
    dt = timezone.make_aware(datetime(2017, 2, 28, 12, 0))
    assert adjust_to_subscription_start(dt, ss) == dt

    # interesting scenario of dt after adjusted ss
    ss = timezone.make_aware(datetime(2016, 12, 31, 12, 0))
    dt = timezone.make_aware(datetime(2017, 2, 28, 13, 0))
    assert (adjust_to_subscription_start(dt, ss) ==
            timezone.make_aware(datetime(2017, 2, 28, 12, 0)))


def test_iter_days():
    start = timezone.make_aware(datetime(2017, 3, 29, 1, 2, 3))
    end = timezone.make_aware(datetime(2017, 4, 7, 11, 22, 33))

    days = iter_days(start, end)

    assert type(days) is types.GeneratorType

    starts = [
        datetime.combine(datetime(year, month, day).date(), start.timetz())
        for year, month, day in [
                (2017, 3, 29),
                (2017, 3, 30),
                (2017, 3, 31),
                (2017, 4, 1),
                (2017, 4, 2),
                (2017, 4, 3),
                (2017, 4, 4),
                (2017, 4, 5),
                (2017, 4, 6),
                (2017, 4, 7),
        ]
    ]

    ends = starts[1:] + [end]

    assert list(days) == list(zip(starts, ends))


def test_iter_months():
    start = timezone.make_aware(datetime(2015, 12, 31, 1, 2, 3))
    end = timezone.make_aware(datetime(2018, 6, 10, 11, 22, 33))

    months = iter_months(start, end)

    assert type(months) is types.GeneratorType

    starts = [
        datetime.combine(datetime(year, month, day).date(), start.timetz())
        for year, month, day in [
                (2015, 12, 31),
                (2016, 1, 31),
                (2016, 2, 29),  # leap!
                (2016, 3, 31),
                (2016, 4, 30),
                (2016, 5, 31),
                (2016, 6, 30),
                (2016, 7, 31),
                (2016, 8, 31),
                (2016, 9, 30),
                (2016, 10, 31),
                (2016, 11, 30),
                (2016, 12, 31),
                (2017, 1, 31),
                (2017, 2, 28),
                (2017, 3, 31),
                (2017, 4, 30),
                (2017, 5, 31),
                (2017, 6, 30),
                (2017, 7, 31),
                (2017, 8, 31),
                (2017, 9, 30),
                (2017, 10, 31),
                (2017, 11, 30),
                (2017, 12, 31),
                (2018, 1, 31),
                (2018, 2, 28),
                (2018, 3, 31),
                (2018, 4, 30),
                (2018, 5, 31),
        ]
    ]

    ends = starts[1:] + [end]

    assert list(months) == list(zip(starts, ends))


def test_iter_quarters():
    start = timezone.make_aware(datetime(2015, 11, 30, 1, 2, 3))
    end = timezone.make_aware(datetime(2017, 2, 28, 11, 22, 33))

    quarters = iter_quarters(start, end)

    assert type(quarters) is types.GeneratorType

    starts = [
        datetime.combine(datetime(year, month, day).date(), start.timetz())
        for year, month, day in [
                (2015, 11, 30),
                (2016, 2, 29),  # leap!
                (2016, 5, 30),
                (2016, 8, 30),
                (2016, 11, 30),
                (2017, 2, 28),
        ]
    ]

    ends = starts[1:] + [end]

    assert list(quarters) == list(zip(starts, ends))


def test_iter_years():
    start = timezone.make_aware(datetime(2016, 2, 29, 1, 2, 3))
    end = timezone.make_aware(datetime(2019, 2, 28, 11, 22, 33))

    years = iter_years(start, end)

    assert type(years) is types.GeneratorType

    starts = [
        datetime.combine(datetime(year, month, day).date(), start.timetz())
        for year, month, day in [
                (2016, 2, 29),  # leap!
                (2017, 2, 28),
                (2018, 2, 28),
                (2019, 2, 28),
        ]
    ]

    ends = starts[1:] + [end]

    assert list(years) == list(zip(starts, ends))


def test_next_month():
    dt = timezone.make_aware(datetime(2017, 3, 30, 11, 5))

    assert next_month(dt) == timezone.make_aware(datetime(2017, 4, 30, 11, 5))
    assert next_month(dt, delta=2) == timezone.make_aware(datetime(2017, 5, 30, 11, 5))
    assert next_month(dt, delta=12) == timezone.make_aware(datetime(2018, 3, 30, 11, 5))
    assert next_month(dt, delta=-1) == timezone.make_aware(datetime(2017, 2, 28, 11, 5))
    assert next_month(dt, delta=-12) == timezone.make_aware(datetime(2016, 3, 30, 11, 5))

    assert (next_month(dt, preferred_dom=31) ==
            timezone.make_aware(datetime(2017, 4, 30, 11, 5)))
    assert (next_month(dt, preferred_dom=31, delta=2)
            == timezone.make_aware(datetime(2017, 5, 31, 11, 5)))
    assert (next_month(dt, preferred_dom=31, delta=12)
            == timezone.make_aware(datetime(2018, 3, 31, 11, 5)))
    assert (next_month(dt, preferred_dom=31, delta=-1)
            == timezone.make_aware(datetime(2017, 2, 28, 11, 5)))
    assert (next_month(dt, preferred_dom=31, delta=-12)
            == timezone.make_aware(datetime(2016, 3, 31, 11, 5)))

    with pytest.raises(ValueError):
        next_month(dt, delta=0)


def test_nearest_dom():
    assert nearest_dom(2017, 1, 1) == 1
    assert nearest_dom(2017, 1, 31) == 31
    assert nearest_dom(2017, 2, 27) == 27
    assert nearest_dom(2017, 2, 28) == 28
    assert nearest_dom(2017, 2, 29) == 28
    assert nearest_dom(2017, 2, 30) == 28
    assert nearest_dom(2017, 2, 31) == 28

