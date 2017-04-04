from __future__ import absolute_import, unicode_literals

from datetime import datetime
from django.utils import timezone
import pytest
from .factories import SouvenirFactory
from souvenirs.reports import (daily_usage,
                               customer_monthly_usage,
                               customer_quarterly_usage,
                               customer_yearly_usage,
                               calendar_monthly_usage,
                               usage_for_periods,
                               registered_users_as_of)


@pytest.mark.django_db
class TestSouvenir:

    @pytest.fixture(autouse=True)
    def setup(self, db, mocker):
        self.tzinfo = timezone.get_current_timezone()
        self.subscription_start = datetime(
            year=2010, month=1, day=24, hour=22, tzinfo=self.tzinfo)
        self.souvenirs = [
            SouvenirFactory(when=datetime(
                year=i, month=2, day=14, hour=12, tzinfo=self.tzinfo))
            for i in range(2010, 2018)
        ]
        self.souvenirs.append(
            SouvenirFactory(when=datetime(year=2015, month=10, day=17,
                                          hour=12, tzinfo=self.tzinfo))
        )
        mocked_now = mocker.patch('souvenirs.reports.timezone.now')
        mocked_now.return_value = self.now = datetime(
            year=2017, month=4, day=3, hour=23, tzinfo=self.tzinfo)

    def test_daily_usage(self):
        daus = list(daily_usage(self.subscription_start))
        assert len(daus) == 2627  # 7 years, 70 days, 2 leap days

        make_when = lambda y, m, **kw: datetime(
            year=2010, month=1, day=24, hour=22, tzinfo=self.tzinfo).replace(
                year=y, month=m, **kw)

        make_usage = lambda yn, mn, qn, usage, start, end: {
            'period': {
                'start': start,
                'end': end,
            },
            'labels': {
                'year_month': 'Y{:02d} M{:02d}'.format(yn, mn),
                'year_quarter': 'Y{:02d} Q{}'.format(yn, qn),
                'year': 'Y{:02d}'.format(yn),
            },
            'usage': {
                'registered_users': usage[0],
                'activated_users': usage[1],
                'active_users': usage[2],
            },
        }

        non_zero_daus = [dau for dau in daus if dau['usage']['active_users']]
        assert non_zero_daus == [
            make_usage(yn=1, mn=1, qn=1, usage=(1, 1, 1), start=make_when(2010, 2, day=13), end=make_when(2010, 2, day=14)),
            make_usage(yn=2, mn=1, qn=1, usage=(2, 2, 1), start=make_when(2011, 2, day=13), end=make_when(2011, 2, day=14)),
            make_usage(yn=3, mn=1, qn=1, usage=(3, 3, 1), start=make_when(2012, 2, day=13), end=make_when(2012, 2, day=14)),
            make_usage(yn=4, mn=1, qn=1, usage=(4, 4, 1), start=make_when(2013, 2, day=13), end=make_when(2013, 2, day=14)),
            make_usage(yn=5, mn=1, qn=1, usage=(5, 5, 1), start=make_when(2014, 2, day=13), end=make_when(2014, 2, day=14)),
            make_usage(yn=6, mn=1, qn=1, usage=(6, 6, 1), start=make_when(2015, 2, day=13), end=make_when(2015, 2, day=14)),
            make_usage(yn=6, mn=9, qn=3, usage=(7, 7, 1), start=make_when(2015, 10, day=16), end=make_when(2015, 10, day=17)),
            make_usage(yn=7, mn=1, qn=1, usage=(8, 8, 1), start=make_when(2016, 2, day=13), end=make_when(2016, 2, day=14)),
            make_usage(yn=8, mn=1, qn=1, usage=(9, 9, 1), start=make_when(2017, 2, day=13), end=make_when(2017, 2, day=14)),
        ]

        # test number of months returned with custom start/end dates
        when = make_when(2013, 2)
        assert len(list(daily_usage(self.subscription_start, start=when))) == 1500  # 4 years, 39 days, 1 leap day
        assert len(list(daily_usage(self.subscription_start, end=when))) == 1127  # 3 years, 31 days, 1 leap day
        assert len(list(daily_usage(self.subscription_start, start=when, end=when))) == 0

    def test_customer_monthly_usage(self):
        maus = list(customer_monthly_usage(self.subscription_start))
        assert len(maus) == 87  # 7 years, 3 months

        make_when = lambda y, m, **kw: datetime(
            year=2010, month=1, day=24, hour=22, tzinfo=self.tzinfo).replace(
                year=y, month=m, **kw)

        make_usage = lambda yn, mn, qn, usage, start, end: {
            'period': {
                'start': start,
                'end': end,
            },
            'labels': {
                'year_month': 'Y{:02d} M{:02d}'.format(yn, mn),
                'year_quarter': 'Y{:02d} Q{}'.format(yn, qn),
                'year': 'Y{:02d}'.format(yn),
            },
            'usage': {
                'registered_users': usage[0],
                'activated_users': usage[1],
                'active_users': usage[2],
            },
        }

        non_zero_maus = [mau for mau in maus if mau['usage']['active_users']]
        assert non_zero_maus == [
            make_usage(yn=1, mn=1, qn=1, usage=(1, 1, 1), start=make_when(2010, 1), end=make_when(2010, 2)),
            make_usage(yn=2, mn=1, qn=1, usage=(2, 2, 1), start=make_when(2011, 1), end=make_when(2011, 2)),
            make_usage(yn=3, mn=1, qn=1, usage=(3, 3, 1), start=make_when(2012, 1), end=make_when(2012, 2)),
            make_usage(yn=4, mn=1, qn=1, usage=(4, 4, 1), start=make_when(2013, 1), end=make_when(2013, 2)),
            make_usage(yn=5, mn=1, qn=1, usage=(5, 5, 1), start=make_when(2014, 1), end=make_when(2014, 2)),
            make_usage(yn=6, mn=1, qn=1, usage=(6, 6, 1), start=make_when(2015, 1), end=make_when(2015, 2)),
            make_usage(yn=6, mn=9, qn=3, usage=(7, 7, 1), start=make_when(2015, 9), end=make_when(2015, 10)),
            make_usage(yn=7, mn=1, qn=1, usage=(8, 8, 1), start=make_when(2016, 1), end=make_when(2016, 2)),
            make_usage(yn=8, mn=1, qn=1, usage=(9, 9, 1), start=make_when(2017, 1), end=make_when(2017, 2)),
        ]

        # test number of months returned with custom start/end dates
        when = make_when(2013, 2)
        assert len(list(customer_monthly_usage(self.subscription_start, start=when))) == 50  # 4 years, 2 months
        assert len(list(customer_monthly_usage(self.subscription_start, end=when))) == 37  # 3 years, 1 month
        assert len(list(customer_monthly_usage(self.subscription_start, start=when, end=when))) == 0

    def test_customer_quarterly_usage(self):
        qaus = list(customer_quarterly_usage(self.subscription_start))
        assert len(qaus) == 29  # 7 years, 3 months

        make_when = lambda y, m, **kw: datetime(
            year=2010, month=1, day=24, hour=22, tzinfo=self.tzinfo).replace(
                year=y, month=m, **kw)

        make_usage = lambda yn, qn, usage, start, end: {
            'period': {
                'start': start,
                'end': end,
            },
            'labels': {
                'year_quarter': 'Y{:02d} Q{}'.format(yn, qn),
                'year': 'Y{:02d}'.format(yn),
            },
            'usage': {
                'registered_users': usage[0],
                'activated_users': usage[1],
                'active_users': usage[2],
            },
        }

        non_zero_qaus = [qau for qau in qaus if qau['usage']['active_users']]
        assert non_zero_qaus == [
            make_usage(yn=1, qn=1, usage=(1, 1, 1), start=make_when(2010, 1), end=make_when(2010, 4)),
            make_usage(yn=2, qn=1, usage=(2, 2, 1), start=make_when(2011, 1), end=make_when(2011, 4)),
            make_usage(yn=3, qn=1, usage=(3, 3, 1), start=make_when(2012, 1), end=make_when(2012, 4)),
            make_usage(yn=4, qn=1, usage=(4, 4, 1), start=make_when(2013, 1), end=make_when(2013, 4)),
            make_usage(yn=5, qn=1, usage=(5, 5, 1), start=make_when(2014, 1), end=make_when(2014, 4)),
            make_usage(yn=6, qn=1, usage=(6, 6, 1), start=make_when(2015, 1), end=make_when(2015, 4)),
            make_usage(yn=6, qn=3, usage=(7, 7, 1), start=make_when(2015, 7), end=make_when(2015, 10)),
            make_usage(yn=7, qn=1, usage=(8, 8, 1), start=make_when(2016, 1), end=make_when(2016, 4)),
            make_usage(yn=8, qn=1, usage=(9, 9, 1), start=make_when(2017, 1), end=self.now),
        ]

        # test number of quarters returned with custom start/end dates
        when = make_when(2013, 2)
        assert len(list(customer_quarterly_usage(self.subscription_start, start=when))) == 17  # 4 years, 2 months
        assert len(list(customer_quarterly_usage(self.subscription_start, end=when))) == 13  # 3 years, 1 month
        assert len(list(customer_quarterly_usage(self.subscription_start, start=when, end=when))) == 0

    def test_customer_yearly_usage(self):
        yaus = list(customer_yearly_usage(self.subscription_start))
        assert len(yaus) == 8  # 7 years, 3 months

        make_when = lambda y, m, **kw: datetime(
            year=2010, month=1, day=24, hour=22, tzinfo=self.tzinfo).replace(
                year=y, month=m, **kw)

        make_usage = lambda yn, usage, start, end: {
            'period': {
                'start': start,
                'end': end,
            },
            'labels': {
                'year': 'Y{:02d}'.format(yn),
            },
            'usage': {
                'registered_users': usage[0],
                'activated_users': usage[1],
                'active_users': usage[2],
            },
        }

        non_zero_yaus = [yau for yau in yaus if yau['usage']['active_users']]
        assert non_zero_yaus == [
            make_usage(yn=1, usage=(1, 1, 1), start=make_when(2010, 1), end=make_when(2011, 1)),
            make_usage(yn=2, usage=(2, 2, 1), start=make_when(2011, 1), end=make_when(2012, 1)),
            make_usage(yn=3, usage=(3, 3, 1), start=make_when(2012, 1), end=make_when(2013, 1)),
            make_usage(yn=4, usage=(4, 4, 1), start=make_when(2013, 1), end=make_when(2014, 1)),
            make_usage(yn=5, usage=(5, 5, 1), start=make_when(2014, 1), end=make_when(2015, 1)),
            make_usage(yn=6, usage=(7, 7, 2), start=make_when(2015, 1), end=make_when(2016, 1)),
            make_usage(yn=7, usage=(8, 8, 1), start=make_when(2016, 1), end=make_when(2017, 1)),
            make_usage(yn=8, usage=(9, 9, 1), start=make_when(2017, 1), end=self.now),
        ]

        # test number of quarters returned with custom start/end dates
        when = make_when(2013, 2)
        assert len(list(customer_yearly_usage(self.subscription_start, start=when))) == 5  # 4 years, 2 months
        assert len(list(customer_yearly_usage(self.subscription_start, end=when))) == 4  # 3 years, 1 month
        assert len(list(customer_yearly_usage(self.subscription_start, start=when, end=when))) == 0

    def test_calendar_monthly_usage(self):
        cal_maus = list(calendar_monthly_usage(self.subscription_start))
        assert len(cal_maus) == 88  # 7 years, 4 months

        make_when = lambda y, m, **kw: datetime(
            year=2010, month=1, day=1, hour=0, tzinfo=self.tzinfo).replace(
                year=y, month=m, **kw)

        make_usage = lambda usage, start, end: {
            'period': {
             'start': start,
             'end': end,
            },
            'labels': {
             'calendar_year_month': start.strftime('%Y-%m'),
             'calendar_year': start.year,
            },
            'usage': {
             'registered_users': usage[0],
             'activated_users': usage[1],
             'active_users': usage[2],
            },
        }

        non_zero_cal_maus = [mau for mau in cal_maus if mau['usage']['active_users']]
        assert non_zero_cal_maus == [
            make_usage(usage=(1, 1, 1), start=make_when(2010, 2), end=make_when(2010, 3)),
            make_usage(usage=(2, 2, 1), start=make_when(2011, 2), end=make_when(2011, 3)),
            make_usage(usage=(3, 3, 1), start=make_when(2012, 2), end=make_when(2012, 3)),
            make_usage(usage=(4, 4, 1), start=make_when(2013, 2), end=make_when(2013, 3)),
            make_usage(usage=(5, 5, 1), start=make_when(2014, 2), end=make_when(2014, 3)),
            make_usage(usage=(6, 6, 1), start=make_when(2015, 2), end=make_when(2015, 3)),
            make_usage(usage=(7, 7, 1), start=make_when(2015, 10), end=make_when(2015, 11)),
            make_usage(usage=(8, 8, 1), start=make_when(2016, 2), end=make_when(2016, 3)),
            make_usage(usage=(9, 9, 1), start=make_when(2017, 2), end=make_when(2017, 3)),
        ]

        # test number of months returned with custom start/end dates
        assert len(list(calendar_monthly_usage(start=make_when(2013, 2), end=make_when(2013,5)))) == 3
        assert len(list(calendar_monthly_usage(start=make_when(2013, 2), end=make_when(2013,2)))) == 0
