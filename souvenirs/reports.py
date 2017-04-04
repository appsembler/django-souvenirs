from __future__ import absolute_import, unicode_literals

import itertools
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.module_loading import import_string
from .control import count_active_users
from .utils import (iter_days, iter_quarters, iter_months, iter_years,
                    adjust_to_calendar_month)


izip = getattr(itertools, 'izip', zip)


def daily_usage(subscription_start, start=None, end=None):
    # labeling depends on having a month number, so defer to
    # customer_monthly_usage for that.
    for monthly_usage in customer_monthly_usage(subscription_start,
                                                start=start,
                                                end=end):
        periods = iter_days(monthly_usage['period']['start'],
                            monthly_usage['period']['end'])
        for daily_usage in usage_for_periods(periods):
            usage = dict(daily_usage,
                         labels=monthly_usage['labels'])
            yield usage


def customer_monthly_usage(subscription_start, start=None, end=None):
    if start is None:
        start = subscription_start

    # regardless of start, the monthly iterator must use subscription_start for
    # the sake of enumerating.
    periods = iter_months(start=subscription_start,
                          end=end or timezone.now())

    for m, usage in enumerate(usage_for_periods(periods), 1):
        if usage['period']['end'] <= start:
            continue
        usage.update(
            labels=dict(
                year_month=label_year_month_m(m),
                year_quarter=label_year_quarter_m(m),
                year=label_year_m(m),
            ),
        )
        yield usage


def customer_quarterly_usage(subscription_start, start=None, end=None):
    if start is None:
        start = subscription_start

    # regardless of start, the quarterly iterator must use subscription_start
    # for the sake of enumerating.
    periods = iter_quarters(start=subscription_start,
                            end=end or timezone.now())

    for q, usage in enumerate(usage_for_periods(periods), 1):
        if usage['period']['end'] <= start:
            continue
        usage.update(
            labels=dict(
                year_quarter=label_year_quarter_q(q),
                year=label_year_q(q),
            ),
        )
        yield usage


def customer_yearly_usage(subscription_start, start=None, end=None):
    if start is None:
        start = subscription_start

    # regardless of start, the yearly iterator must use subscription_start
    # for the sake of enumerating.
    periods = iter_years(start=subscription_start,
                         end=end or timezone.now())

    for y, usage in enumerate(usage_for_periods(periods), 1):
        if usage['period']['end'] <= start:
            continue
        usage.update(
            labels=dict(
                year=label_year_y(y)
            ),
        )
        yield usage


def calendar_monthly_usage(start, end=None):
    start = adjust_to_calendar_month(start)
    periods = iter_months(start, end or timezone.now())
    for usage in usage_for_periods(periods):
        usage.update(
            labels=dict(
                calendar_year_month=label_calendar_year_month(usage['period']['start']),
                calendar_year=label_calendar_year(usage['period']['start']),
            ),
        )
        yield usage


month_to_year = lambda m: (m - 1) // 12 + 1
month_to_month = lambda m: (m - 1) % 12 + 1
month_to_quarter = lambda m: ((m - 1) // 3) % 4 + 1
quarter_to_year = lambda q: (q - 1) // 4 + 1
quarter_to_quarter = lambda q: (q - 1) % 4 + 1
label_year_month_m = lambda m: 'Y{:02d} M{:02d}'.format(month_to_year(m), month_to_month(m))
label_year_quarter_q = lambda q: 'Y{:02d} Q{}'.format(quarter_to_year(q), quarter_to_quarter(q))
label_year_quarter_m = lambda m: 'Y{:02d} Q{}'.format(month_to_year(m), month_to_quarter(m))
label_year_y = lambda y: 'Y{:02d}'.format(y)
label_year_q = lambda q: 'Y{:02d}'.format(quarter_to_year(q))
label_year_m = lambda m: 'Y{:02d}'.format(month_to_year(m))
label_calendar_year_month = lambda d: d.strftime('%Y-%m')
label_calendar_year = lambda d: d.year  # int


def usage_for_periods(*args, **kwargs):
    name = getattr(settings, 'SOUVENIRS_USAGE_REPORTS_FUNCTION', None)
    func = import_string(name) if name else _usage_for_periods
    return func(*args, **kwargs)


def _usage_for_periods(periods):
    """
    Generate a sequence of dictionaries of usage data corresponding to periods,
    each of which should be a tuple of (start, end) datetimes, where start is
    inclusive and end is exclusive.

    Each dictionary in the generated sequence has this form:

        {
            period: {
                start: datetime,
                end: datetime,
            }
            usage: {
                registered_users: int,
                activated_users: int,
                active_users: int,
            }
        }

    """
    rp, ap, periods = itertools.tee(periods, 3)
    ir = (registered_users_as_of(end) for start, end in rp)
    ia = (count_active_users(*p) for p in ap)
    for p, r, active in izip(periods, ir, ia):
        start, end = p
        registered, activated = r
        yield dict(
            period=dict(
                start=start,
                end=end,
            ),
            usage=dict(
                registered_users=registered,
                activated_users=activated,
                active_users=active,
            ),
        )


def registered_users_as_of(date):
    """
    Return a tuple of the form (registered, activated) indicating the total
    registered and activated users for the given date.
    """
    User = get_user_model()
    users = User.objects.filter(date_joined__lt=date)
    return users.count(), users.filter(is_active=True).count()
