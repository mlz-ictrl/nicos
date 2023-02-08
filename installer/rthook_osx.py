#!/bin/python

import os
import gr

qt = os.environ.get('NICOS_QT')

dirgr = os.path.dirname(gr.__file__)
libs = ['QtWidgets', 'QtCore', 'QtGui']
v = 'A' if qt else '5'
for lib in libs:
    os.makedirs(f'{dirgr}/lib/{lib}.framework/Versions/{v}')
    os.symlink(f'../../../../../{lib}',
               f'{dirgr}/lib/{lib}.framework/Versions/{v}/{lib}')

icufiles = ['qtwebengine_resources.pak', 'qtwebengine_resources_200p.pak',
            'qtwebengine_resources_100p.pak',
            'qtwebengine_devtools_resources.pak', 'icudtl.dat']
dir = os.path.dirname(dirgr)
v = '6' if qt else '5'
for file in icufiles:
    os.symlink(f'../../{file}', f'{dir}/PyQt{v}/Qt{v}/{file}')

os.symlink(f'../../../qtwebengine_locales',
           f'{dir}/PyQt{v}/Qt{v}/translations/qtwebengine_locales')
