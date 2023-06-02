#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
     name='amyloidAI',
     version="1.0",
     author="Claes Ladefoged",
     author_email="claes.noehr.ladefoged@regionh.dk",
     description="Estimate amyloid accumulation",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/CAAI/amyloidID",
     scripts=[
             'amyloidAI/amyloidAI',
     ],
     packages=find_packages('amyloidAI'),
     install_requires=[
         'onnxruntime',
         'numpy',
         'torchio',
         'nipype',
         
     ],
     classifiers=[
         'Programming Language :: Python :: 3.8',
     ],
 )
