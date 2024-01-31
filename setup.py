# -*- coding: utf-8 -*-
"""
setup.py 

Created on 05.01.2024

author: Felix Scope

taken from 
https://github.com/yngvem/python-project-structure?tab=readme-ov-file#structuring-a-repository
"""
from setuptools import setup, find_packages

install_requires = []

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()
        
setup(
    name='MtG-OCR',
    version='0.1.0',
    packages=find_packages(),

)