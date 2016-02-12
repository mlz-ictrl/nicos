#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2015 by the NICOS contributors (see AUTHORS)
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
#   pedersen
#
# *****************************************************************************

"""
Symmetry-related classes
"""

import numpy
from nicos.devices.tas.spacegroups import get_spacegroup, can_reflect


class Bravais(object):

    conditions = {
        'C': lambda h, k, l: (numpy.logical_not((h + k) % 2)),
        'A': lambda h, k, l: (numpy.logical_not((k + l) % 2)),
        'B': lambda h, k, l: (numpy.logical_not((h + l) % 2)),
        'I': lambda h, k, l: (numpy.logical_not((h + k + l) % 2)),
        'R': lambda h, k, l: (numpy.logical_not((-h + k + l) % 3)),
        'F': lambda h, k, l: (numpy.logical_and(
            (numpy.logical_not((h + k) % 2)),
            (numpy.logical_not((h + l) % 2)))),
        'P': lambda h, k, l: numpy.logical_or(h, True)}

    def __init__(self, bravais):
        self.bravais = bravais

    def allowed(self, hkl):
        if self.bravais in Bravais.conditions:
            return Bravais.conditions[self.bravais](*hkl)
        else:
            return Bravais.conditions['P'](*hkl)


class SpaceGroup(object):
    def __init__(self, spgr):
        self.spgr = get_spacegroup(spgr)

    def allowed(self, hkl):
        return can_reflect(self.spgr, *hkl)


valid = {'C': [(0, 0, 3), (1, 1, 0), (2, 2, 0), (-1, 1, 0), (1, -1, 0), (3, 3, 1), (4, 4, 3)],
         'A': [(1, 0, 0), (0, 1, 1), (0, 2, 2), (0, -1, 1), (0, 1, -1,), (3, 3, 1), (3, 4, 4)],
         'B': [(0, 1, 0), (1, 0, 1), (2, 0, 2), (-1, 0, 1), (1, 0, -1,), (3, 3, 1), (4, 3, 4)],
         'I': [(0, 1, 1), (1, 0, 1), (1, 1, 0), (0, -1, 1), (-1, 0, 1), (-1, 1, 0),
               (0, 1, -1), (1, 0, -1), (1, -1, 0), (0, -1, -1), (-1, 0, -1), (-1, -1, 0)],
         'R': [(0, 1, 2), (0, 2, 1), (1, 2, 2), (-1, 2, 0)],
         'F': [(1, 1, 1), (2, 2, 2), (2, 2, 0), (-1, 1, -1)]
         }
invalid = {'C': [(0, 1, 2), (2, 1, 0), (1, 2, 0), (-1, 2, 0), (2, -1, 0)],
           'A': [(1, 1, 0), (0, 2, 1), (0, 2, -1)],
           'B': [(1, 1, 0), (1, 0, 0), (1, 0, 2), (-1, 0, 2), (2, 0, -1,)],
           'I': [(1, 1, 1), (1, -1, 1), (-1, 1, 1), (-1, -1, 1), (1, 1, -1), (-1, 1, -1),
                 (1, -1, -1), (-1, -1, -1)],
           'R': [(1, 1, 2), (-1, 2, 1), (2, 2, 2), (-2, 2, 0)],
           'F': [(1, 1, 0), (0, 1, 1), (1, 0, 1)]
           }

def _testfunc(t, mode, hkl):
    b = Bravais(t)
    # note: return is a numpy.bool_, so testing with 'is' fails
    if mode:
        assert b.allowed(hkl)
    else:
        assert not b.allowed(hkl)

def _test():
    import six
    for t, vals in six.iteritems(valid):
        for hkl in vals:
            _testfunc.description = '%s %s , OK' %(t, hkl)
            yield _testfunc, t, True, hkl
    for t, vals in six.iteritems(invalid):
        for hkl in vals:
            _testfunc.description = '%s %s , False' %(t, hkl)
            yield _testfunc, t, False, hkl
