# -*- mode: python -*-

import sys
from os import path

specdir = path.abspath(SPECPATH)
rootdir = path.dirname(SPECPATH)
sys.path.insert(0, specdir)

from utils import find_custom, find_gr, find_modules, find_uis, \
    find_uncertainties


a = Analysis(
    [path.join(rootdir, 'bin', 'nicos-gui')],
    pathex=[rootdir],
    binaries=[],
    datas=
        find_custom() +
        find_gr() +
        find_uis() +
        find_uncertainties() +
        [(path.join(rootdir, 'nicos', 'RELEASE-VERSION'), 'nicos')],
    hiddenimports=
        find_modules('nicos', 'clients', 'gui') +
        find_modules('nicos', 'clients', 'flowui') +
        find_modules('nicos', 'guisupport') +
        find_modules('nicos', 'core') +
        find_modules('nicos', 'devices'),
    hookspath=[],
    excludes=['Tkinter', 'matplotlib', 'gtk', 'IPython', 'ipykernel', 'pygments'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='nicos-gui-debug',
    debug=True,
    strip=False,
    console=True,
    cdict={
        'EXTENSION': 0,
        'DATA': 0,
        'BINARY': 0,
        'EXECUTABLE': 0,
        'PYSOURCE': 0,
        'PYMODULE': 0,
        'PYZ': 0
    }
)
