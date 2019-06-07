#!/usr/bin/env python

from setuptools import setup, find_packages
from os.path import join, dirname
import MangAdventure


def read(fname):
    with open(join(dirname(__file__), fname)) as f:
        return f.read()


setup(
    name=MangAdventure.__name__,
    version=MangAdventure.__version__,
    license=MangAdventure.__license__,
    author=MangAdventure.__author__,
    maintainer=MangAdventure.__author__,
    description=MangAdventure.__doc__,
    long_description=read('README.md'),
    url='https://mangadventure.rtfd.io',
    download_url='https://github.com/mangadventure/MangAdventure',
    keywords=['manga', 'scanlation', 'reader'],
    packages=find_packages(),
    python_requires='>=2.7',
    install_requires=read('requirements.txt').splitlines(),
    extras_require={
        'dev': [
            'sphinx',
            'sphinx-rtd-theme',
            'django-debug-toolbar',
        ],
        'csp': 'django-csp',
        'uwsgi': 'uwsgi',
        'gunicorn': 'gunicorn'
    },
    entry_points={
        'console_scripts': ['mangadventure = manage:main']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: '
        'Dynamic Content :: Content Management System',
    ]
)

