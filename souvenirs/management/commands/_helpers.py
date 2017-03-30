from __future__ import absolute_import, unicode_literals

import argparse
import dateutil.parser
from django.core.management.base import CommandError
from django.utils import timezone


class DateAction(argparse.Action):
    """
    argparse action that parses its argument into a timezone-aware datetime
    """
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            dt = dateutil.parser.parse(values)
        except ValueError:
            raise CommandError("can't parse date: {}".format(values))
        if dt.tzinfo is None:
            dt = timezone.make_aware(dt)
        setattr(namespace, self.dest, dt)
