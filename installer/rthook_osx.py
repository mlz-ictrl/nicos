#!/bin/python

import os
import gr

# We're building the installer always with Qt 6.
os.environ['NICOS_QT'] = '6'

dirgr = os.path.dirname(gr.__file__)
libs = ['QtWidgets', 'QtCore', 'QtGui']
for lib in libs:
    os.makedirs(f'{dirgr}/lib/{lib}.framework/Versions/A')
    os.symlink(f'../../../../../{lib}',
               f'{dirgr}/lib/{lib}.framework/Versions/A/{lib}')

icufiles = ['qtwebengine_resources.pak', 'qtwebengine_resources_200p.pak',
            'qtwebengine_resources_100p.pak',
            'qtwebengine_devtools_resources.pak', 'icudtl.dat']
dir = os.path.dirname(dirgr)
for file in icufiles:
    os.symlink(f'../../{file}', f'{dir}/PyQt6/Qt6/{file}')

os.symlink(f'../../../qtwebengine_locales',
           f'{dir}/PyQt6/Qt6/translations/qtwebengine_locales')
