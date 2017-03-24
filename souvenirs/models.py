from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone


class Souvenir(models.Model):
    """
    One instance of seeing an active user
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    when = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-when']

    def __repr__(self):
        return '<{} user={} when={!r}>'.format(
            self.__class__.__name__, self.user.username, self.when)
