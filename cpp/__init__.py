# Recompiles um_emulator if outdated.

import os
import time
import subprocess
import pathlib
import contextlib


@contextlib.contextmanager
def changed_cur_dir(path):
    cur = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cur)



def check_updates():
    project_dir = pathlib.Path(__file__).parent.parent.absolute()
    command = r'cl /std:c++17 /EHsc /LD /MDd /O2 um_emulator.cpp C:\Python37\libs\python37.lib /Feum_emulator.pyd /I C:\Python37\include'

    with changed_cur_dir(project_dir / 'cpp'):
        last_cpp_edit = os.stat('um_emulator.cpp').st_mtime
        last_py_edit = os.stat('__init__.py').st_mtime

        if pathlib.Path('um_emulator.pyd').exists():
            last_compilation = os.stat('um_emulator.pyd').st_mtime
            if last_compilation > last_cpp_edit and last_compilation > last_py_edit:
                return

        subprocess.check_call(command, shell=True)
        os.remove('um_emulator.exp')
        os.remove('um_emulator.lib')
        os.remove('um_emulator.obj')

check_updates()
