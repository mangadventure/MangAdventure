#!/usr/bin/env python3

from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.develop import develop

import MangAdventure

cwd = Path(__file__).parent


class Develop(develop):
    def run(self):
        super().run()
        with open(self.egg_link, 'r') as lnk:
            path = Path(lnk.readline()[:-1], 'static', 'extra')
        path.mkdir(exist_ok=True)
        path.joinpath('style.scss').touch(0o644)


setup(
    name=MangAdventure.__name__,
    version=MangAdventure.__version__,
    license=MangAdventure.__license__,
    author=MangAdventure.__author__,
    maintainer=MangAdventure.__author__,
    description=MangAdventure.__doc__,
    long_description=(cwd / 'README.md').read_text(),
    url='https://mangadventure.readthedocs.io',
    download_url='https://github.com/mangadventure/MangAdventure',
    keywords=['manga', 'scanlation', 'reader'],
    packages=find_packages(),
    python_requires='>=3.8',
    setup_requires=['wheel'],
    install_requires=(cwd / 'requirements.txt').read_text().splitlines(),
    extras_require={
        'dev': (cwd / 'dev-requirements.txt').read_text().splitlines(),
        'docs': (cwd / 'docs' / 'requirements.txt').read_text().splitlines(),
        'debug': 'django-debug-toolbar',
        'mysql': 'mysqlclient',
        'pgsql': 'psycopg2',
        'csp': 'django-csp>=3.7',
        'uwsgi': 'uwsgi',
        'sentry': 'sentry-sdk~=1.9',
    },
    entry_points={
        'console_scripts': [
            'mangadventure = MangAdventure.__main__:run'
        ]
    },
    cmdclass={'develop': Develop},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.1',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: '
        'Dynamic Content :: Content Management System',
    ]
)
