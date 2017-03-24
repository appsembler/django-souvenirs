from __future__ import absolute_import, unicode_literals

import datetime
from django.utils import timezone
import pytest
from souvenirs.models import Souvenir
from souvenirs.control import total_active_users, monthly_active_users, souvenez
from .factories import SouvenirFactory, UserFactory


@pytest.mark.django_db
class TestSouvenir:

    # setup_method doesn't work with pytest.mark.django_db.
    # This is the workaround, see http://stackoverflow.com/questions/34089425
    @pytest.fixture(autouse=True)
    def setup_souvenirs(self, db):
        self.tzinfo = timezone.get_current_timezone()
        self.souvenirs = [
            SouvenirFactory(when=datetime.datetime(year=i, month=2, day=14,
                                                   hour=12, tzinfo=self.tzinfo))
            for i in range(2010, 2018)
        ]

    def test_total_active_users(self):
        assert total_active_users() == 8

        when = datetime.datetime(year=2013, month=1, day=1, tzinfo=self.tzinfo)
        assert total_active_users(start=when)
        assert total_active_users(end=when)

        # combine start and end.
        when = datetime.datetime(year=2013, month=2, day=1, tzinfo=self.tzinfo)
        assert total_active_users(start=when, end=when.replace(year=2015)) == 2
        assert total_active_users(start=when.replace(year=2015), end=when) == 0

        # ensure start inclusive and end exclusive by using a datetime that
        # exactly matches a record.
        when = datetime.datetime(year=2013, month=2, day=14, hour=12, tzinfo=self.tzinfo)
        assert Souvenir.objects.filter(when=when).exists()
        assert total_active_users(start=when) == 5
        assert total_active_users(end=when) == 3
        assert total_active_users(start=when, end=when) == 0

    def test_total_active_users_distinct(self):
        for s in self.souvenirs:
            SouvenirFactory(user=s.user, when=s.when)
        self.test_total_active_users()

    def test_monthly_active_users(self):
        muas = list(monthly_active_users())
        assert len(muas) == 85  # months from 2010-02 to 2017-02 inclusive

        make_when = lambda y, m, **kw: datetime.datetime(
            year=2013, month=2, day=14, hour=12, tzinfo=self.tzinfo).replace(
                year=y, month=m, **kw)

        non_zero_muas = [mua for mua in muas if mua[2]]
        assert non_zero_muas == [
            (make_when(2010, 2), make_when(2010, 3), 1),
            (make_when(2011, 2), make_when(2011, 3), 1),
            (make_when(2012, 2), make_when(2012, 3), 1),
            (make_when(2013, 2), make_when(2013, 3), 1),
            (make_when(2014, 2), make_when(2014, 3), 1),
            (make_when(2015, 2), make_when(2015, 3), 1),
            (make_when(2016, 2), make_when(2016, 3), 1),
            (make_when(2017, 2), make_when(2017, 2, second=1), 1),
        ]

        # try with start/end args
        when = make_when(2013, 2)
        assert len(list(monthly_active_users(start=when))) == 49
        assert len(list(monthly_active_users(end=when))) == 36
        assert len(list(monthly_active_users(start=when, end=when))) == 0

    def test_monthly_active_users_calendar(self):
        muas = list(monthly_active_users(calendar=True))
        assert len(muas) == 85  # months from 2010-02 to 2017-02 inclusive

        make_when = lambda y, m, **kw: datetime.datetime(
            year=2013, month=2, day=1, tzinfo=self.tzinfo).replace(
                year=y, month=m, **kw)

        non_zero_muas = [mua for mua in muas if mua[2]]
        assert non_zero_muas == [
            (make_when(2010, 2), make_when(2010, 3), 1),
            (make_when(2011, 2), make_when(2011, 3), 1),
            (make_when(2012, 2), make_when(2012, 3), 1),
            (make_when(2013, 2), make_when(2013, 3), 1),
            (make_when(2014, 2), make_when(2014, 3), 1),
            (make_when(2015, 2), make_when(2015, 3), 1),
            (make_when(2016, 2), make_when(2016, 3), 1),
            (make_when(2017, 2), make_when(2017, 2, day=14, hour=12, minute=0, second=1), 1),
        ]

    def test_souvenez(self):
        Souvenir.objects.all().delete()
        assert Souvenir.objects.count() == 0
        u, u2 = UserFactory(), UserFactory()
        assert souvenez(u, when=timezone.now() - datetime.timedelta(minutes=61)) == 'added'
        assert souvenez(u) == 'added'
        assert souvenez(u2) == 'added'
        assert souvenez(u) == 'rate-limited'
        assert souvenez(u, ratelimit=False) == 'added'
        assert Souvenir.objects.count() == 4

