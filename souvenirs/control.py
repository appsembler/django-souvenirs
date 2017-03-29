from __future__ import absolute_import, unicode_literals

from datetime import timedelta
import logging
from django.conf import settings
from django.core.cache import caches
from django.utils import timezone
from .models import Souvenir
from .utils import adjust_to_calendar_month, adjust_to_subscription_start, iter_months


logger = logging.getLogger(__name__)


def count_active_users(start=None, end=None):
    """
    Return the number of active users between start and end datetimes,
    inclusive and exclusive respectively.
    """
    qs = Souvenir.objects.all()
    if start:
        qs = qs.filter(when__gte=start)  # inclusive
    if end:
        qs = qs.filter(when__lt=end)     # exclusive
    return qs.values('user').distinct().count()


def monthly_active_users(start=None, end=None, calendar=False,
                         subscription_start=None):
    """
    Generate a sequence of (month_start, month_end, active) tuples
    where month_start is inclusive and month_end is exclusive.

    start and end default to first and last Souvenir records in DB,
    respectively.

    calendar and subscription_start provide two ways to adjust start. If
    calendar is True, then adjust start to first day of the month, midnight
    local time (according to settings.TIME_ZONE). If subscription_start is
    provided, adjust start to the prior day and time matching
    subscription_start.

    For just one month:

        start, end, active = next(monthly_active_users(start))

    """
    if calendar and subscription_start:
        raise ValueError("specify either calendar or subscription_start, not both")

    # datetime values retrieved from the database are time zone aware, but
    # might be adjusted to UTC. Prepare to adjust them to the current time zone
    # so that the calendar month starts at midnight local time.
    tzinfo = (subscription_start.tzinfo
              if subscription_start and subscription_start.tzinfo else
              timezone.get_current_timezone())

    if start is None:
        first = Souvenir.objects.order_by('when').first()
        if first is None:
            return
        start = first.when.astimezone(tzinfo)
    elif not timezone.is_aware(start):
        start = timezone.make_aware(start, tzinfo)

    if calendar:
        start = adjust_to_calendar_month(start)
    elif subscription_start:
        start = adjust_to_subscription_start(start, subscription_start)

    if end is None:
        last = Souvenir.objects.order_by('when').last()
        if last is None:
            return
        # end is exclusive, so add a second to include the found record
        end = last.when.astimezone(tzinfo) + timedelta(seconds=1)
    elif not timezone.is_aware(end):
        end = timezone.make_aware(end, tzinfo)

    for month_start, month_end in iter_months(start, end):
        yield month_start, month_end, count_active_users(month_start, month_end)


def souvenez(user, when=None, ratelimit=True, check_duplicate=False):
    """
    Save a Souvenir to the DB, rate-limited by default to once per hour.
    Returns a string: "added", "rate-limited" or "duplicated".
    """
    # user can be a User object or PK (for backfill script)
    user_id = getattr(user, 'id', user)
    username = getattr(user, 'username', user)  # just for logging

    if not isinstance(user_id, int):
        raise TypeError("unexpected value for user: {!r}".format(user))

    if when is None:
        when = timezone.now()

    if ratelimit is True:
        ratelimit = getattr(settings, 'SOUVENIRS_RATELIMIT_SECONDS', 360)

    if ratelimit:
        name = getattr(settings, 'SOUVENIRS_CACHE_NAME', 'default')
        prefix = getattr(settings, 'SOUVENIRS_CACHE_PREFIX', 'souvenir.')
        key = '{}.{}'.format(prefix, user_id)
        cache = caches[name]
        value = cache.get(key)
        if value and when < value + timedelta(seconds=ratelimit):
            logger.debug("rate-limited %s (last seen %s)".format(username, value))
            return 'rate-limited'
        cache.set(key, when)

    if check_duplicate:
        if Souvenir.objects.filter(user_id=user_id, when=when).exists():
            logger.debug("ignoring duplicate souvenir for %s (%s)".format(username, when))
            return 'duplicated'

    Souvenir(user_id=user_id, when=when).save()
    logger.debug("saved souvenir for %s (%s)".format(username, when))
    return 'added'
