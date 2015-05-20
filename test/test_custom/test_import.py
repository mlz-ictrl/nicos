#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS custom lib tests: import all custom modules at least once."""

import os
from os import path
import nose

from nicos.utils.tacostubs import generate_stubs

from test.utils import rootdir, SkipTest


def setup_module():
    generate_stubs()


def import_and_check(modname):
    try:
        __import__(modname)
    except ImportError:  # we lack a precondition module, don't worry about that
        raise SkipTest
    except ValueError as err:
        if 'has already been set to' in str(err):
            # import order error with GUI widget modules
            raise SkipTest
        raise


def test_import_all():
    custom_dir = path.join(rootdir, '..', '..', 'custom')
    for instr in sorted(os.listdir(custom_dir)):
        if instr == 'delab':
            continue
        if not path.isdir(path.join(custom_dir, instr, 'lib')):
            continue
        for mod in os.listdir(path.join(custom_dir, instr, 'lib')):
            if mod.endswith('.py'):
                yield import_and_check, 'nicos.%s.%s' % (instr, mod[:-3])


def test_all_tests():
    custom_dir = path.join(rootdir, '..', '..', 'custom')
    loader = nose.loader.TestLoader()
    for instr in sorted(os.listdir(custom_dir)):
        if instr == 'delab':
            continue
        libdir = path.join(custom_dir, instr, 'lib')
        if not path.isdir(libdir):
            continue

        for s in loader.loadTestsFromDir(libdir):
            if s:
                nose.run(suite=s)
