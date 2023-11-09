#!/usr/bin/env python3

from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.develop import develop


class Develop(develop):
    def run(self):
        super().run()
        with open(self.egg_link, 'r') as lnk:
            path = Path(lnk.readline()[:-1], 'static', 'extra')
        path.mkdir(exist_ok=True)
        path.joinpath('style.scss').touch(0o644)


setup(packages=find_packages(), cmdclass={'develop': Develop})
