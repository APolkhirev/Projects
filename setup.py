# coding: utf-8

from cx_Freeze import setup, Executable

executables = [Executable('ne_auditor.py',
                          targetName='ne_auditor.exe',
                          icon='favicon.ico',
                          shortcutName='NE Auditor'),
               ]

options = {
    'build_exe': {
        'include_msvcr': True,
    }
}

setup(name='ne_auditor',
      version='0.1',
      description='Auditor for network elements',
      executables=executables,
      options=options)