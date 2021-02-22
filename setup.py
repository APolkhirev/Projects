# coding: utf-8

from cx_Freeze import setup, Executable

executables = [Executable('ne_auditor.py')]

setup(name='ne_auditor',
      version='0.1',
      description='Auditor for network elements',
      executables=executables)