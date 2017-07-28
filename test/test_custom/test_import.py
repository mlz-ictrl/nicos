#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
import glob
from os import path

import pytest

from test.utils import module_root


def import_and_check(modname):
    try:
        __import__(modname)
    except ImportError as e:
        # we lack a precondition module, don't worry about that
        pytest.skip('import error for %s: %s' % (modname, e))
    except ValueError as err:
        if 'has already been set to' in str(err):
            # import order error with GUI widget modules
            pytest.skip('GUI widget module')
        raise


facility_dirs = [d for d in glob.glob(path.join(module_root, 'nicos_*'))
                 if path.isdir(d)]
all_instrs = sorted(path.basename(facility_dir) + '.' + instr_dir
                    for facility_dir in facility_dirs
                    for instr_dir in os.listdir(facility_dir)
                    if path.isdir(path.join(facility_dir, instr_dir)))


@pytest.mark.parametrize('fac_instr', all_instrs)
def test_import_all(fac_instr):
    (facility, instr) = fac_instr.split('.')
    if instr == 'delab':
        return
    instrlib = path.join(module_root, facility, instr, 'devices')
    if not path.isdir(instrlib):
        return
    for mod in os.listdir(instrlib):
        if mod.endswith('.py'):
            import_and_check('%s.%s.devices.%s' % (facility, instr, mod[:-3]))
