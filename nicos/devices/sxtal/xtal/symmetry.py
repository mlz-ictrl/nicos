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
import numpy as np
from nicos.devices.tas.spacegroups import get_spacegroup, can_reflect

lnot = np.logical_not
land = np.logical_and
lor = np.logical_or
lxor = np.logical_xor


class Bravais(object):

    conditions = {
        'C': lambda h, k, l: (lnot((h + k) % 2)),
        'A': lambda h, k, l: (lnot((k + l) % 2)),
        'B': lambda h, k, l: (lnot((h + l) % 2)),
        'I': lambda h, k, l: (lnot((h + k + l) % 2)),
        'R': lambda h, k, l: (lnot((-h + k + l) % 3)),
        'F': lambda h, k, l: (land(
            (lnot((h + k) % 2)),
            (lnot((h + l) % 2)))),
        'P': lambda h, k, l: lor(h, True)}

    def __init__(self, bravais):
        self.bravais = bravais

    def allowed(self, hkl):
        if self.bravais in Bravais.conditions:
            return Bravais.conditions[self.bravais](*hkl)
        else:
            return Bravais.conditions['P'](*hkl)

symbols = ('-1', '2/m', '4/mmm', '6/mmm', '4/m', '6/m',
           '-3m1', '-31m', '-3', 'R-3m1', 'R-31m', 'R-3',
           'm3m', 'm3')


class Laue(object):
    def __init__(self, laue):
        self.laue = laue

    def uniqds(self, ds):
        condition = self.uniq((ds[:, 0], ds[:, 1], ds[:, 2]))
        return np.compress(condition, ds, axis=0)

    def uniq(self, hkl):
        h, k, l = hkl
        if self.laue == '-1':
            return lnot(land(np.equal(l, 0),
                             lor(np.less(k, 0),
                                 np.less(h, 0)
                                 )
                             )
                        )
        if self.laue == '2/m':
            return lnot(land(np.equal(l, 0),
                             np.less(h, 0))
                        )
        if self.laue in ('4/mmm', '6/mmm'):
            return lnot(np.less(h, k))
        if self.laue in ('4/m', '6/m'):
            return lnot(land(np.less(h, k),
                             np.equal(h, 0)
                             )
                        )
        if self.laue == '-3m1':
            return lnot(land(np.less(h, k),
                             np.equal(l, 0)
                             )
                        )
        if self.laue == '-31m':
            return lnot(lor(np.less(h, k),
                            land(np.less(l, 0),
                                 np.equal(k, 0)
                                 )
                            )
                        )
        if self.laue == '-3':
            return lnot(land(np.less(h, k),
                             land(lor(np.less_equal(k, h), np.less_equal(h, 0)),
                                  lor(np.equal(l, 0),
                                      lor(np.equal(k, 0),
                                          np.greater_equal(np.abs(h), k)
                                          )
                                      )
                                  )
                             )
                        )
        if self.laue == 'R-3m':
            return lnot(lor(land(np.greater_equal(l, 0),
                                 lor(np.less(h, k),
                                     np.less(k, l)
                                     )
                                 ), land(np.equal(k, 0),
                                         land(np.greater_equal(h, np.abs(l)
                                                               ), lor(np.less_equal(k, 0),
                                                                      np.less(h, k)
                                                                      )
                                              )
                                         )
                            )
                        )
        if self.laue == 'R-3':
            return lnot(lor(land(np.greater_equal(l, 0),
                                 lor(np.less(k, 0),
                                     lor(np.greater_equal(h, k),
                                         np.greater_equal(k, l)
                                         )
                                     )
                                 ),
                            lor(lor(np.less(k, 0),
                                    land(lor(np.less_equal(h, 0),
                                             np.not_equal(k, 0)),
                                         lor(np.less(h, k),
                                             np.less(k, 0))
                                         )
                                    ),
                                lor(np.equal(h, 0),
                                    np.less_equal(k, l)
                                    )
                                )
                            )
                        )
        if self.laue == 'm3m':
            return lnot(lor(np.less(h, k),
                            lor(np.less(k, l),
                                np.less(h, l)
                                )
                            )
                        )

        if self.laue == 'm3':
            return lnot(land(lor(np.less(h, k), np.less(k, l)),
                             lor(np.equal(h, 0),
                                 lor(np.greater_equal(h, k),
                                     np.less_equal(h, l)
                                     )
                                 )
                             )
                        )
        return lor(h, True)


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


def _testbravais(t, mode, hkl):
    # This is a 'template' function
    b = Bravais(t)
    # note: return is a np.bool_, so testing with 'is' fails
    if mode:
        assert b.allowed(hkl)
    else:
        assert not b.allowed(hkl)


def _testlaue(sym):
    # This is a 'template' function
    from nicos.devices.sxtal.xtal.uniqdata import uniq
    lauein = np.array([(h, k, l) for l in range(-2, 3)
                       for k in range(-2, 3)
                       for h in range(-2, 3)])
    l = Laue(sym)
    res = l.uniqds(lauein)
    assert np.array_equiv(uniq[sym], res)


def _test():
    import six
    for t, vals in six.iteritems(valid):
        for hkl in vals:
            # this def is necessary to get uniq descriptions in the
            # test output.
            def tf1(t, mode, hkl):
                _testbravais(t, mode, hkl)
            tf1.description = 'Bravais allowed %s %s' % (t, hkl)
            yield tf1, t, True, hkl
    for t, vals in six.iteritems(invalid):
        for hkl in vals:
            # this def is necessary to get uniq descriptions in the
            # test output.
            def tf2(t, mode, hkl):
                _testbravais(t, mode, hkl)
            tf2.description = 'Bravais forbidden %s %s' % (t, hkl)
            yield tf2, t, False, hkl
    for sym in symbols:
        # this def is necessary to get uniq descriptions in the
        # test output.
        def tf3(sym):
            _testlaue(sym)
        tf3.description = 'Laue uniqds for %s' % sym
        yield tf3, sym
