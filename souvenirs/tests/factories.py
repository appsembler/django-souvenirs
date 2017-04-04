from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.utils import timezone
import factory
from factory.django import DjangoModelFactory
from souvenirs.models import Souvenir


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'user{}'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_active = True


class SouvenirFactory(DjangoModelFactory):
    class Meta:
        model = Souvenir

    user = factory.SubFactory(
        UserFactory,
        date_joined=factory.SelfAttribute('..when'),
        last_login=factory.SelfAttribute('..when'),
    )
