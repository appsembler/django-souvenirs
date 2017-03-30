from __future__ import absolute_import, unicode_literals

from datetime import timedelta
import logging
from django.conf import settings
from django.core.cache import caches
from django.utils import timezone
from .models import Souvenir


logger = logging.getLogger(__name__)


def souvenez(user, when=None, ratelimit=True, check_duplicate=False):
    """
    Save a Souvenir to the DB, rate-limited by default to once per hour.
    Returns a string: "added", "rate-limited" or "duplicated".
    """
    # user can be a User object or PK (for backfill script)
    user_id = getattr(user, 'id', user)
    username = getattr(user, 'username', user)  # just for logging

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


def count_active_users(start=None, end=None, qs=None):
    """
    Return the number of active users between start and end datetimes,
    inclusive and exclusive respectively.
    """
    if qs is None:
        qs = Souvenir.objects.all()
    if start:
        qs = qs.filter(when__gte=start)  # inclusive
    if end:
        qs = qs.filter(when__lt=end)     # exclusive
    return qs.values('user').distinct().count()
