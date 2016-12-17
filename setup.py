
import os

from setuptools import find_packages, setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
        name='labella',
        version='0.9.1',
        description='Python version of Labella.js',
        long_description=read('README.rst'),
        author='Gertjan van den Burg',
        author_email='gertjanvandenburg@gmail.com',
        license='Apache v2',
        packages=find_packages(),
        install_requires = [
            'intervaltree'
            ]
        )
