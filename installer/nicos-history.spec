# -*- mode: python -*-

import sys
from os import path

sys.path.insert(0, path.abspath('.'))

from utils import rootdir, find_uis, find_custom, find_gr, find_modules

binscript = path.join(rootdir, 'bin', 'nicos-history')


a = Analysis([binscript],
             pathex=[rootdir],
             binaries=[],
             datas=find_uis() + find_custom() + find_gr() + [
                 (path.join(rootdir, 'nicos', 'RELEASE-VERSION'), 'nicos')],
             hiddenimports=
                 find_modules('nicos', 'clients', 'gui') +
                 find_modules('nicos', 'guisupport') +
                 find_modules('nicos', 'core'),
             hookspath=[],
             runtime_hooks=['rthook_pyqt4.py'],
             excludes=['Tkinter', 'matplotlib', 'PyQt5', 'gtk', 'IPython',
                       'ipykernel', 'pygments'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='nicos-history',
          debug=False,
          strip=False,
          console=False)
