================
Django Souvenirs
================

|PyPI| |Build Status| |Coverage Report|

How active are users on your Django site? Django can tell you
when users registered (``User.date_joined``) and when they signed in
(``User.last_login``). But sessions are long-lived so this doesn't really answer
the question.

Souvenirs is a Django app for efficiently tracking when users are on your site,
and making that information available through an easy API.

|Souvenirs Album Cover|

Installation
------------

Get the latest stable release from PyPI_

.. code-block:: bash

    pip install django-souvenirs

Or the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/appsembler/django-souvenirs.git#egg=souvenirs

Add to ``settings.py``

.. code-block:: python

    INSTALLED_APPS += [
        'souvenirs',
    ]
    MIDDLEWARE_CLASSES += [
        'souvenirs.middleware.SouvenirsMiddleware',
    ]

Migrate your database

.. code-block:: bash

    ./manage.py migrate souvenirs

Usage
-----

There are two core API calls: ``souvenez`` ("remember") and
``count_active_users``.

You can call ``souvenez(user)`` as often per user as you'd like, by default it
will rate-limit DB entries to once per hour. If you use the provided middleware,
then ``souvenez`` will be called automatically on each request.

Call ``count_active_users`` to find the number of unique users active for a
given time period. For example::

    >>> from souvenirs.control import count_active_users
    >>> from django.utils import timezone
    >>> from datetime import timedelta
    >>> now = timezone.now()
    >>> count_active_users(start=now - timedelta(days=1), end=now)
    42

Either ``start`` or ``end`` can be omitted, which makes the query unbounded in
that direction. The above call is effectively the same as omitting ``end``::

    >>> count_active_users(start=timezone.now() - timedelta(days=1))
    42

and this counts the total number of users active for all time, or at least since
you installed the middleware::

    >>> count_active_users()
    1012

Reports
-------

Souvenirs provides some functions for reporting registered users and activity
over a period of time. For example, to see activity per calendar month for 2016::

    >>> from datetime import datetime
    >>> from django.utils import timezone
    >>> from souvenirs.reports import calendar_monthly_usage
    >>> start = datetime(2016, 1, 1)  # inclusive
    >>> end = datetime(2017, 1, 1)    # exclusive
    >>> for d in calendar_monthly_usage(start=timezone.make_aware(start),
                                        end=timezone.make_aware(end)):
    ...   print(d['labels']['calendar_year_month'],
                d['usage']['registered_users'],
                d['usage']['activated_users'],  # User.is_active
                d['usage']['active_users'])
    2016-01 12  10  9
    2016-02 20  13  11
    2016-03 38  16  10
    2016-04 38  28  14
    2016-05 38  29  20
    2016-06 57  46  37
    2016-07 62  58  43
    2016-08 117 80  49
    2016-09 175 300 75
    2016-10 280 333 89
    2016-11 420 360 99
    2016-12 588 540 151

See reports_ for additional reporting functions, especially for starting
subscriptions on arbitrary days (instead of calendar months).

.. |reports| replace:: ``souvenirs.reports``
.. _reports: https://github.com/appsembler/django-souvenirs/blob/master/souvenirs/reports.py

Settings
--------

Souvenirs uses hopefully sane defaults for all settings. Here's what you can
override if you want:

``SOUVENIRS_RATELIMIT_SECONDS``: how often to record an active user in the DB,
default ``360``

``SOUVENIRS_CACHE_NAME``: which cache to use for rate-limiting,
default ``'default'``

``SOUVENIRS_CACHE_PREFIX``: how to prefix rate-limiting cache entries,
default ``'souvenirs.'``

``SOUVENIRS_USAGE_REPORTS_FUNCTION``: all the reporting functions call a
low-level function usage_. This can be overridden (probably wrapped) if you'd
like to use the souvenirs reporting functions to generate richer data, for
example incorporating some other data per time period.

.. |usage| replace:: ``usage_for_periods``
.. _usage: https://github.com/appsembler/django-souvenirs/blob/master/souvenirs/reports.py#L117

Contributing
------------

To contribute to this project, fork to your own github user, make your changes
on a branch, run the tests and open a pull request. If you have hub_ and tox_
installed, it's like this:

.. code-block:: bash

    hub clone appsembler/django-souvenirs
    cd django-souvenirs
    git checkout -b my-awesome-feature
    # hack hack hack!
    tox --skip-missing-interpreters
    git commit -am "my awesome commit"
    hub fork  # for example agriffis/django-souvenirs
    git push --set-upstream agriffis  # insert your github user here
    hub pull-request

Legal
-----

Copyright 2017 `NodeRabbit Inc., d.b.a. Appsembler <https://appsembler.com>`_

Released under the `MIT license <https://github.com/appsembler/django-souvenirs/blob/master/LICENSE>`_

.. _PyPI: https://pypi.python.org/pypi/django-souvenirs

.. |Build Status| image:: https://img.shields.io/travis/appsembler/django-souvenirs/master.svg?style=plastic
   :target: https://travis-ci.org/appsembler/django-souvenirs?branch=master

.. |Coverage Report| image:: https://img.shields.io/codecov/c/github/appsembler/django-souvenirs/master.svg?style=plastic
   :target: https://codecov.io/gh/appsembler/django-souvenirs/branch/master

.. |PyPI| image:: https://img.shields.io/pypi/v/django-souvenirs.svg?style=plastic
   :target: PyPI_

.. |Souvenirs Album Cover| image:: https://images-na.ssl-images-amazon.com/images/I/51UhpUAIRaL._SS500.jpg
   :target: https://www.amazon.com/Souvenirs-Reinhardt-Quintet-St%C3%A9phane-Grappelli/dp/B000VWONGE

.. _hub: https://hub.github.com/

.. _tox: https://pypi.python.org/pypi/tox
