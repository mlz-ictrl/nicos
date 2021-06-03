#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
import numpy as np

from nicos.core import Device, Param, tupleof
from nicos.core.errors import InvalidValueError


class ReflexList(Device):
    """
    This class maintains a list of crystallographic reflections.
    A reflection is characterised by its reciprocal space coordinates
    and its setting angles on the diffractometer. In some cases there
    may be additional information associated with a reflection such as
    Intensity, sigma, whatever. Each of these morsels is represented
    as a tuple. And each reflection is represented as a tuple of
    reciprocal space coordinates, setting angles, aux
    """

    parameters = {
        'reflection_list': Param('The actual list of reflections',
                                 type=list,
                                 settable=True),
        'column_headers': Param('The names of each component of the '
                                'reflection, grouped by data type',
                                type=tupleof(tuple, tuple, tuple),
                                default=(('H', 'K', 'L'),
                                         ('STT', 'OM', 'CHI', 'PHI'), ('',))
                                ),
    }

    hardware_access = False
    _hkl_len = 3
    _angle_len = 4
    _ex_len = 0

    def doInit(self, mode):
        self._hkl_len = len(self.column_headers[0])
        self._angle_len = len(self.column_headers[1])
        self._ex_len = len(self.column_headers[2])

    def clear(self):
        self.reflection_list = []

    def append(self, Qpos=None, angles=None, aux=None):
        if not Qpos and not angles:
            raise InvalidValueError('One of reciprocal coordinates '
                                    'or angles must be given')
        if not Qpos:
            Qpos = (0,)*self._hkl_len
        if len(Qpos) != self._hkl_len:
            raise InvalidValueError('Reciprocal coordinates mismatch, '
                                    'need %d, got %d'
                                    % (self._hkl_len, len(Qpos)))
        if not angles:
            angles = (0,)*self._angle_len
        if len(angles) != self._angle_len:
            raise InvalidValueError('Angle settings mismatch, '
                                    'need %d, got %d'
                                    % (self._angle_len, len(angles)))
        if not aux:
            aux = ()
        reflist = list(self.reflection_list)
        reflist.append((Qpos, angles, aux))
        self.reflection_list = reflist

    def get_reflection(self, idx):
        if idx < 0 or idx > len(self.reflection_list):
            raise InvalidValueError('NO reflection with '
                                    'index %d found' % idx)
        return self.reflection_list[idx]

    def modify_reflection(self, idx, Qpos=None, angles=None, aux=None):
        oldref = self.get_reflection(idx)
        if not Qpos:
            Qpos = oldref[0]
        if len(Qpos) != len(oldref[0]):
            raise InvalidValueError('Expected %d values for Q, got %d' %
                                    (len(oldref[0]), len(Qpos)))
        if not angles:
            angles = oldref[1]
        if len(angles) != len(oldref[1]):
            raise InvalidValueError('Expected %d angles, got %d' %
                                    (len(oldref[1]), len(angles)))
        if not aux:
            aux = oldref[2]
        if len(aux) != len(oldref[2]):
            raise InvalidValueError('Expected %d auxiliaries, got %d' %
                                    (len(oldref[2]), len(aux)))
        reflist = list(self.reflection_list)
        reflist[idx] = (Qpos, angles, aux)
        self.reflection_list = reflist

    def delete(self, idx):
        reflist = list(self.reflection_list)
        del reflist[idx]
        self.reflection_list = reflist

    def __len__(self):
        return len(self.reflection_list)

    def generate(self, start):
        """
        A generator function for iterating over the reflection list
        """
        num = start
        while True:
            if num < len(self.reflection_list):
                yield self.get_reflection(num)
            else:
                return
            num += 1

    def find_reflection(self, hkl):
        for count, r in enumerate(self.reflection_list):
            if np.allclose(r[0], hkl):
                return count
        return -1
