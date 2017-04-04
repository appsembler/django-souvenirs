from __future__ import absolute_import, unicode_literals

from django.core.management.base import CommandError
from django.core.management.base import BaseCommand, CommandError
from souvenirs.reports import (daily_usage, customer_monthly_usage,
                               customer_quarterly_usage, customer_yearly_usage)
from ._helpers import DateAction


class ReportCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--subscription-start', metavar='DATE', action=DateAction,
                            help="customer subscription start or renewal date")
        parser.add_argument('--after', metavar='DATE', action=DateAction,
                            help="include lines starting at (inclusive)")
        parser.add_argument('--before', metavar='DATE', action=DateAction,
                            help="include lines ending at (exclusive)")

        parser.add_argument('--daily', action='store_const', dest='report', const='daily',
                            help="report on daily activity")
        parser.add_argument('--monthly', action='store_const', dest='report', const='monthly',
                            help="report on monthly activity (default)")
        parser.add_argument('--quarterly', action='store_const', dest='report', const='quarterly',
                            help="report on quarterly activity")
        parser.add_argument('--yearly', action='store_const', dest='report', const='yearly',
                            help="report on yearly activity")

        parser.add_argument('--recent', nargs='?', const=1, type=int, metavar='NUM',
                            help="show only the most recent N (1) entries")
        parser.add_argument('--ascending', action='store_true',
                            help="output in date-ascending order (default: descending)")
        parser.add_argument('--datefmt', default='%Y-%m-%d',
                            help="strftime for date columns (default: %%Y-%%m-%%d)")

    def handle(self, *args, **options):
        report = options['report'] or 'monthly'

        if (report in ['daily', 'monthly', 'quarterly', 'yearly'] and
            options['subscription_start'] is None
        ):
            raise CommandError("{} report requires --subscription-start"
                               .format(report))

        report_method = getattr(self, '{}_report'.format(report))
        headers, rows = report_method(options)

        if options['recent']:
            rows = rows[-options['recent']:]

        # reports are chronologically ascending by default (mainly because of
        # enumerations), but for display we prefer reversed by default.
        if not options['ascending']:
            rows = reversed(rows)

        return headers, rows

    def daily_report(self, options):
        headers = ['date', 'registered', 'activated', 'active']
        usage = daily_usage(
            subscription_start=options['subscription_start'],
            start=options['after'],
            end=options['before'],
        )
        rows = [
            [d['period']['end'].strftime(options['datefmt']),
             d['usage']['registered_users'],
             d['usage']['activated_users'],
             d['usage']['active_users'],
            ] for d in usage
        ]
        return headers, rows

    def monthly_report(self, options):
        headers = ['month', 'start', 'end', 'registered', 'activated', 'active']
        usage = customer_monthly_usage(
            subscription_start=options['subscription_start'],
            start=options['after'],
            end=options['before'],
        )
        rows = [
            [d['labels']['year_month'],
             d['period']['start'].strftime(options['datefmt']),
             d['period']['end'].strftime(options['datefmt']),
             d['usage']['registered_users'],
             d['usage']['activated_users'],
             d['usage']['active_users'],
            ] for d in usage
        ]
        return headers, rows

    def quarterly_report(self, options):
        headers = ['quarter', 'start', 'end', 'registered', 'activated', 'active']
        usage = customer_quarterly_usage(
            subscription_start=options['subscription_start'],
            start=options['after'],
            end=options['before'],
        )
        rows = [
            [d['labels']['year_quarter'],
             d['period']['start'].strftime(options['datefmt']),
             d['period']['end'].strftime(options['datefmt']),
             d['usage']['registered_users'],
             d['usage']['activated_users'],
             d['usage']['active_users'],
            ] for d in usage
        ]
        return headers, rows

    def yearly_report(self, options):
        headers = ['year', 'start', 'end', 'registered', 'activated', 'active']
        usage = customer_yearly_usage(
            subscription_start=options['subscription_start'],
            start=options['after'],
            end=options['before'],
        )
        rows = [
            [d['labels']['year'],
             d['period']['start'].strftime(options['datefmt']),
             d['period']['end'].strftime(options['datefmt']),
             d['usage']['registered_users'],
             d['usage']['activated_users'],
             d['usage']['active_users'],
            ] for d in usage
        ]
        return headers, rows
