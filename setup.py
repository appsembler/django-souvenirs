from __future__ import absolute_import, unicode_literals

from codecs import open
import os
from setuptools import setup, find_packages
import souvenirs as app


def read(fname):
    top = os.path.dirname(__file__)
    with open(os.path.join(top, fname), encoding='utf-8') as f:
        return f.read()


setup(
    name="django-souvenirs",
    version=app.__version__,
    description='Django app for efficiently measuring usage',
    long_description=read('README.rst'),
    license='MIT',
    platforms=['OS Independent'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='django reusable souvenirs metrics usage tracking'.split(),
    author='Aron Griffis',
    author_email='aron@scampersand.com',
    url="https://github.com/appsembler/django-souvenirs",
    packages=find_packages(),
    install_requires=['tabulate'],
)
