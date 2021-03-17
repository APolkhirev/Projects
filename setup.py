from cx_Freeze import setup, Executable

executables = [Executable('ne_auditor.py', icon='favicon.ico')]
excludes = ['tkinter']

options = {
    'build_exe': {
        'include_msvcr': True,
        'excludes': excludes,
    }
}

setup(name='ne_auditor',
      version='0.5',
      description='Multivendor Auditor for Network Elements',
      executables=executables,
      options=options)
