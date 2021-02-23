# coding: utf-8

from cx_Freeze import setup, Executable

executables = [Executable('ne_auditor.py',
                          icon='favicon.ico'),
               ]
#excludes = ['tkinter', 'email', 'html', 'http', 'urllib', 'xml', 'bz2']

options = {
    'build_exe': {
        'include_msvcr': True,
#        'excludes': excludes,
    }
}

setup(name='ne_auditor',
      version='0.0.1',
      description='Auditor for network elements',
      executables=executables,
      options=options)
