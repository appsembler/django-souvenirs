Django Souvenirs
================

Souvenirs is a Django app for efficiently tracking user activity.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-souvenirs

Or get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/appsembler/django-souvenirs.git#egg=souvenirs

Add ``souvenirs`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = [
        ...,
        'souvenirs',
    ]

Migrate your database

.. code-block:: bash

    ./manage.py migrate souvenirs

Usage
-----

configuration, api
