#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

import glob
import os
from configparser import ConfigParser
from distutils.dir_util import mkpath
from os import path

from setuptools import setup
from setuptools.command.install import install as stinstall

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
        ('setup-package=', None, 'Path for the NICOS setups'),
        ('instrument=', None, 'Name of the instrument'),
    ]

    def initialize_options(self):
        stinstall.initialize_options(self)
        self.install_pid = None
        self.install_log = None
        self.setup_package = None
        self.instrument = None

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
        if not self.instrument:
            self.instrument = os.getenv('INSTRUMENT')
        if self.instrument and self.instrument.count('.') > 0:
            self.setup_package, self.instrument = self.instrument.split('.')
        if not self.setup_package:
            self.setup_package = os.getenv('SETUPPACKAGE')
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

    def createInitialGlobalNicosConf(self):
        cfg = ConfigParser()
        cfg.optionxform = str
        cfg.read(self.install_conf)
        if not cfg.has_section('nicos'):
            cfg.add_section('nicos')
        cfg.set('nicos', 'pid_path', '%s' % self.true_pid)
        cfg.set('nicos', 'logging_path', '%s' % self.true_log)
        cfg.set('nicos', 'installed_from', '%s' % path.abspath(os.curdir))
        if self.instrument:
            cfg.set('nicos', 'instrument',  '%s' % self.instrument)
        else:
            self.announce("INSTRUMENT not given, please check %s to set the"
                          " correct instrument! "
                          "(see Installation guide in docs)" % self.install_conf, 2)
        if self.setup_package:
            cfg.set('nicos', 'setup_package', '%s' % self.setup_package)
        else:
            self.announce("SETUPPACKAGE not given, please check %s to set the"
                          " correct setup_package! "
                          "(see Installation guide in docs)" % self.install_conf, 2)
        with open(self.install_conf, 'w') as configfile:
            cfg.write(configfile)

    def run_install_etc(self):
        self.copy_tree('etc', self.install_etc)
        mkpath(self.install_pid)
        mkpath(self.install_log)
        self.createInitialGlobalNicosConf()


setup(
    name = 'nicos',
    version = nicos_version,
    license = 'GPL',
    author = 'Georg Brandl',
    author_email = 'g.brandl@fz-juelich.de',
    maintainer = 'Jens Krüger',
    maintainer_email = 'jens.krueger@frm2.tum.de',
    description = 'The Networked Instrument Control System',
    url = 'http://www.nicos-controls.org',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
