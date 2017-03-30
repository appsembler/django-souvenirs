from __future__ import absolute_import, unicode_literals

import datetime
from django.utils import timezone
import pytest
from souvenirs.models import Souvenir
from souvenirs.control import count_active_users, souvenez
from .factories import SouvenirFactory, UserFactory


@pytest.mark.django_db
class TestSouvenir:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.tzinfo = timezone.get_current_timezone()
        self.souvenirs = [
            SouvenirFactory(when=datetime.datetime(year=i, month=2, day=14,
                                                   hour=12, tzinfo=self.tzinfo))
            for i in range(2010, 2018)
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

    def test_count_active_users(self):
        assert count_active_users() == 8

        when = datetime.datetime(year=2013, month=1, day=1, tzinfo=self.tzinfo)
        assert count_active_users(start=when)
        assert count_active_users(end=when)

        # combine start and end.
        when = datetime.datetime(year=2013, month=2, day=1, tzinfo=self.tzinfo)
        assert count_active_users(start=when, end=when.replace(year=2015)) == 2
        assert count_active_users(start=when.replace(year=2015), end=when) == 0

        # ensure start inclusive and end exclusive by using a datetime that
        # exactly matches a record.
        when = datetime.datetime(year=2013, month=2, day=14, hour=12, tzinfo=self.tzinfo)
        assert Souvenir.objects.filter(when=when).exists()
        assert count_active_users(start=when) == 5
        assert count_active_users(end=when) == 3
        assert count_active_users(start=when, end=when) == 0

    def test_count_active_users_distinct(self):
        for s in self.souvenirs:
            SouvenirFactory(user=s.user, when=s.when)
        self.test_count_active_users()

