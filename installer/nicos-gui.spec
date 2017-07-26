# -*- mode: python -*-

import os
import sys
import subprocess
from os import path

rootdir = path.abspath('..')
binscript = path.join(rootdir, 'bin', 'nicos-gui')
guidir = path.join(rootdir, 'nicos', 'clients', 'gui')
customdir = path.join(rootdir, 'nicos_mlz')

# Make sure to generate the version file.
os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + path.pathsep + rootdir
subprocess.check_call([sys.executable,
                       path.join(rootdir, 'nicos', '_vendor', 'gitversion.py')])


# Include all modules/files for the custom directory.
def find_custom():
    res = []
    for root, _dirs, files in os.walk(customdir):
        for fn in files:
            if fn.endswith('.pyc'):
                continue
            res.append((path.join(root, fn),
                        path.join('nicos_mlz', root[len(customdir) + 1:])))
    return res


# Include all .ui files for the main GUI module.
def find_uis():
    res = []
    for root, _dirs, files in os.walk(guidir):
        if any(uifile for uifile in files if uifile.endswith('.ui')):
            res.append((path.join(root, '*.ui'),
                        path.join('nicos', 'clients', 'gui',
                                  root[len(guidir) + 1:])))
    return res


# Include all modules found in a certain package -- they may not be
# automatically found because of dynamic importing via the guiconfig file
# and custom widgets in .ui files.
def find_modules(*modules):
    res = []
    startdir = path.join(rootdir, *modules)
    startmod = '.'.join(modules) + '.'
    for root, _dirs, files in os.walk(startdir):
        modpath = root[len(startdir) + 1:].replace(path.sep, '.')
        if modpath:
            modpath += '.'
        for mod in files:
            if mod.endswith('.py'):
                res.append(startmod + modpath + mod[:-3])
    return res


a = Analysis([binscript],
             pathex=[rootdir],
             binaries=[],
             datas=find_uis() + find_custom() + [
                 (path.join(rootdir, 'nicos', 'RELEASE-VERSION'), 'nicos')],
             hiddenimports=
                 find_modules('nicos', 'clients', 'gui') +
                 find_modules('nicos', 'guisupport') +
                 find_modules('nicos', 'core') +
                 find_modules('nicos', 'devices'),
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
          name='nicos-gui',
          debug=False,
          strip=False,
          upx=False,
          console=False)
