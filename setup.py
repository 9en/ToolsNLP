# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os.path
import site

sitedir = site.getsitepackages()[-1]
installdir = os.path.join(sitedir, 'ToolsNLP')


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ToolsNLP',
    version='1.0.0',
    description='Packaging common processing when analyzing related to natural language processing',
    long_description=readme,
    author='suzuki_motoya',
    author_email='suzuki_motoya@cyberagent.co.jp',
    python_requires='>=3.4',
    install_requires=['numpy==1.15.4','neologdn','scipy==1.1.0', 'mecab-python3', 'gensim==3.6.0', 'matplotlib', 'wordcloud', 'pandas'],
    url='https://github.com/9en/ToolsNLP',
    license=license,
    data_files=[(os.path.join(installdir, '.fonts'), ['ToolsNLP/.fonts/ipaexg.ttf']),
        (os.path.join(installdir,'sentiment_dict'), ['ToolsNLP/sentiment_dict/pn_noun.json'])],
    packages=find_packages(exclude=('tests'))
)

