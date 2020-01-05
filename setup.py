#!/usr/bin/env python3

from importlib.util import find_spec
from pathlib import PurePath

from setuptools import find_packages, setup

import MangAdventure

if find_spec('isort'):
    from isort.settings import default
    default['known_django'] = 'django'
    default['known_mangadv'] = 'MangAdventure'


def read(fname):
    with open(PurePath(__file__).parent / fname) as f:
        return f.read()


setup(
    name=MangAdventure.__name__,
    version=MangAdventure.__version__,
    license=MangAdventure.__license__,
    author=MangAdventure.__author__,
    maintainer=MangAdventure.__author__,
    description=MangAdventure.__doc__,
    long_description=read('README.md'),
    url='https://mangadventure.readthedocs.io',
    download_url='https://github.com/mangadventure/MangAdventure',
    keywords=['manga', 'scanlation', 'reader'],
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=read('requirements.txt').splitlines(),
    extras_require={
        'dev': read('dev-requirements.txt').splitlines(),
        'docs': read('docs/requirements.txt').splitlines(),
        'debug': 'django-debug-toolbar',
        'mysql': 'mysqlclient',
        'pgsql': 'psycopg2',
        'csp': 'django-csp>=3.6',
        'uwsgi': 'uwsgi',
        'sentry': 'sentry-sdk',
    },
    entry_points={
        'console_scripts': [
            'mangadventure = MangAdventure.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: '
        'Dynamic Content :: Content Management System',
    ]
)
