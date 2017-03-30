from __future__ import absolute_import, unicode_literals

import csv
from tabulate import tabulate
from ._commands import ReportCommand


class Command(ReportCommand):
    help = "Shows registered, activated and active users"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--csv', action='store_true',
                            help="output csv instead of table")

    def handle(self, *args, **options):
        headers, rows = super(Command, self).handle(*args, **options)

        if options['csv']:
            writer = csv.writer(self.stdout)
            writer.writerow(headers)
            writer.writerows(rows)
        else:
            return tabulate(rows, headers)  # prints on stdout
