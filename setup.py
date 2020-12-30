# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os.path
import site
import sys

installdir = '/ToolsNLP'

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ToolsNLP',
    version='1.0.0',
    description='Packaging common processing when analyzing related to natural language processing',
    long_description=readme,
    author='9en',
    author_email='mty.0613@gmail.com',
    python_requires='>=3.4',
    url='https://github.com/9en/ToolsNLP',
    license=license,
    data_files=[(os.path.join(installdir, '.fonts'), ['ToolsNLP/.fonts/ipaexg.ttf']),
        (os.path.join(installdir,'sentiment_dict'), ['ToolsNLP/sentiment_dict/pn_noun.json', 'ToolsNLP/sentiment_dict/pn_wago.json'])],
    packages=find_packages(exclude=('tests'))
)

