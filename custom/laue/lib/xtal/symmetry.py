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


def _test():
    for t, vals in valid.iteritems():
        b = Bravais(t)
        for hkl in vals:
            assert b.allowed(hkl) is True

    for t, vals in invalid.iteritems():
        b = Bravais(t)
        for hkl in vals:
            assert b.allowed(hkl) is False
