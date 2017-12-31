#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

import os
import glob
from os import path
from setuptools import setup
from setuptools.command.install import install as stinstall
from distutils.dir_util import mkpath  # pylint: disable=E0611,F0401

from nicos import nicos_version

root_packages = ['nicos'] + [d for d in glob.glob('nicos_*') if path.isdir(d)]

scripts = ['bin/' + name for name in os.listdir('bin')
           if name.startswith('nicos-')] + ['bin/designer-nicos']


def find_package_files():
    """Find all packages, package data files and pure data dirs."""
    packages = []
    package_data = {}
    pure_data_dirs = []
    for pkg in root_packages:
        for root, dirs, files in os.walk(pkg):
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            if '__init__.py' not in files:
                # Any non-package gets installed by copy-tree.
                pure_data_dirs.append(root)
            else:
                pkgname = root.replace(os.sep, '.')
                packages.append(pkgname)
                # In a package, we only install non-Python files.
                datas = [f for f in files
                         if not f.endswith(('.py', '.pyc', '.pyo'))]
                if datas:
                    package_data[pkgname] = datas
    return (packages, package_data, pure_data_dirs)


packages, package_data, pure_data_dirs = find_package_files()


class nicosinstall(stinstall):
    user_options = stinstall.user_options + [
        ('install-pid=', None, 'Path for pid files'),
        ('install-log=', None, 'Path for log files'),
    ]

    def initialize_options(self):
        stinstall.initialize_options(self)
        self.install_pid = None
        self.install_log = None

    def finalize_options(self):
        if self.prefix is None and 'VIRTUAL_ENV' not in os.environ:
            self.announce('No explicit install path set, using /opt/nicos.', 2)
            self.prefix = '/opt/nicos'
        # override "lib/pythonX.Y/site-packages"
        self.install_purelib = '$base'
        self.install_platlib = '$base'
        stinstall.finalize_options(self)
        if self.install_pid is None:
            self.install_pid = 'pid'
        if self.install_log is None:
            self.install_log = 'log'
        if not path.isabs(self.install_pid):
            self.install_pid = path.join(self.install_base, self.install_pid)
        if not path.isabs(self.install_log):
            self.install_log = path.join(self.install_base, self.install_log)
        self._expand_attrs(['install_pid', 'install_log'])
        self.install_etc = path.join(self.install_base, 'etc')
        self.install_conf = path.join(self.install_base, 'nicos.conf')
        self.install_icons = path.join(self.install_base, 'icons')
        self.true_etc = self.install_etc
        self.true_pid = self.install_pid
        self.true_log = self.install_log

        self.dump_dirs('post-finalize-custom')
        if self.root is not None:
            self.change_roots('etc', 'pid', 'log', 'conf', 'icons')
        self.dump_dirs('post-finalize-custom_root')

    def run(self):
        stinstall.run(self)
        self.run_install_datadirs()
        self.run_install_icons()
        self.run_install_etc()

    def run_install_datadirs(self):
        for datadir in pure_data_dirs:
            self.copy_tree(datadir, path.join(self.install_data, datadir))

    def run_install_icons(self):
        for res in ['16x16', '32x32', '48x48', 'scalable']:
            self.copy_tree(path.join('resources', 'icons', res),
                           path.join(self.install_icons, res))

    def run_install_etc(self):
        self.copy_tree('etc', self.install_etc)
        mkpath(self.install_pid)
        mkpath(self.install_log)
        nicos_conf_tmpl = """\
[nicos]
pid_path = %s
logging_path = %s
installed_from = %s
"""
        with open(self.install_conf, 'w') as cf:
            cf.write(nicos_conf_tmpl % (self.true_pid,
                                        self.true_log,
                                        path.abspath(os.curdir)))
            instr = os.getenv('INSTRUMENT')
            if instr:
                cf.write('\ninstrument = %s\n' % instr)

            setup_package = os.getenv('SETUPPACKAGE')
            if setup_package:
                cf.write('\nsetup_package = %s\n' % setup_package)


setup(
    name = 'nicos',
    version = nicos_version,
    license = 'GPL',
    author = 'Georg Brandl',
    author_email = 'georg.brandl@frm2.tum.de',
    maintainer = 'Jens Krueger',
    maintainer_email = 'jens.krueger@frm2.tum.de',
    description = 'The Networked Instrument Control System of the MLZ',
    url = 'https://forge.frm2.tum.de/projects/NICOS/',
    cmdclass = {'install': nicosinstall},
    packages = packages,
    package_data = package_data,
    scripts = scripts,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: GPL License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
