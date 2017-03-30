from __future__ import absolute_import, unicode_literals

from datetime import timedelta
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
import pytest
from souvenirs.middleware import SouvenirsMiddleware
from souvenirs.models import Souvenir
from .factories import UserFactory


@pytest.mark.django_db
class TestMiddleware:

    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.sm = SouvenirsMiddleware()
        self.request = mocker.Mock()

    def test_process_request_with_user(self):
        self.request.user = u = UserFactory()
        assert Souvenir.objects.count() == 0
        assert self.sm.process_request(self.request) is None
        assert Souvenir.objects.count() == 1
        s = Souvenir.objects.all()[0]
        assert s.user == u
        assert timedelta() <= (timezone.now() - s.when) <= timedelta(seconds=10)

    def test_process_request_with_anonymous(self):
        self.request.user = u = AnonymousUser()
        assert Souvenir.objects.count() == 0
        assert self.sm.process_request(self.request) is None
        assert Souvenir.objects.count() == 0
