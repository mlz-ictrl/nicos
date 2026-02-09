# -*- mode: python -*-

import sys
from os import path

sys.path.insert(0, path.abspath('.'))

from utils import find_custom, find_gr, find_gr_osx, find_modules, \
                  find_uis, find_uncertainties, nicos_version, \
                  rootdir

a = Analysis(
    [path.join(rootdir, 'bin', 'nicos-gui')],
    pathex=[rootdir],
    binaries=[],
    datas=find_uis() +
          find_custom() +
          find_gr_osx() +
          find_uncertainties() +
          [(path.join(rootdir, 'nicos', 'RELEASE-VERSION'), 'nicos')],
    hiddenimports=find_modules('nicos', 'clients', 'gui') +
                  find_modules('nicos', 'clients', 'flowui') +
                  find_modules('nicos', 'guisupport') +
                  find_modules('nicos', 'core') +
                  find_modules('nicos', 'devices'),
    hookspath=[],
    runtime_hooks=['rthook_osx.py'],
    excludes=['Tkinter', 'matplotlib', 'gtk', 'IPython', 'ipykernel', 'pygments'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    version=nicos_version(),
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
