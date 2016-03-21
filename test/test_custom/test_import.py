#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

from nicos.utils.tacostubs import generate_stubs

from test.utils import rootdir, SkipTest


def setup_module():
    generate_stubs()


def import_and_check(modname):
    try:
        __import__(modname)
    except ImportError:
        # we lack a precondition module, don't worry about that
        raise SkipTest
    except ValueError as err:
        if 'has already been set to' in str(err):
            # import order error with GUI widget modules
            raise SkipTest
        raise


def collect_files(instr, instrlib):
    some_skipped = False
    for mod in os.listdir(instrlib):
        if mod.endswith('.py'):
            try:
                import_and_check('nicos.%s.%s' % (instr, mod[:-3]))
            except SkipTest:
                some_skipped = True
    if some_skipped:
        raise SkipTest

def test_import_all():
    custom_dir = path.join(rootdir, '..', '..', 'custom')
    for instr in sorted(os.listdir(custom_dir)):
        if instr == 'delab':
            continue
        instrlib = path.join(custom_dir, instr, 'lib')
        if not path.isdir(instrlib):
            continue

        def tf(*args):
            collect_files(*args)

        tf.description =  __name__ + '.test_import_all: ' + instr
        yield tf, instr, instrlib
