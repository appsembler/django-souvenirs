from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Souvenir(models.Model):
    """
    One instance of seeing an active user
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    when = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-when']

    def __str__(self):
        return 'user={} when={}'.format(self.user_id, self.when)
