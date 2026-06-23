# -*- mode: python -*-

import sys
from os import path

specdir = path.abspath(SPECPATH)
rootdir = path.dirname(SPECPATH)
sys.path.insert(0, specdir)

from utils import find_custom, find_gr, find_modules, find_resources, \
    find_uis, find_uncertainties

a = Analysis(
    [path.join(rootdir, 'bin', 'nicos-gui')],
    pathex=[rootdir],
    binaries=[],
    datas=
        find_custom() +
        find_gr() +
        find_resources() +
        find_uis() +
        [(path.join(rootdir, 'nicos', 'RELEASE-VERSION'), 'nicos')],
    hiddenimports=
        find_modules('nicos', 'clients', 'gui') +
        find_modules('nicos', 'clients', 'flowui') +
        find_modules('nicos', 'guisupport') +
        find_modules('nicos', 'core') +
        find_modules('nicos', 'devices'),
    hookspath=[],
    runtime_hooks=['rthook_osx.py'],
    excludes=['Tkinter', 'matplotlib', 'gtk', 'IPython', 'ipykernel', 'pygments'],
    cipher=None,
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='nicos-gui',
    debug=False,
    strip=False,
    upx=False,
    icon='../resources/icons/nicos.icns',
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='nicos-gui',
)
app = BUNDLE(
    coll,
    name='nicos-gui.app',
    icon='../resources/icons/nicos.icns',
    bundle_identifier=None,
)
