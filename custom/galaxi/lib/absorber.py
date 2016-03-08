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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#
# *****************************************************************************

"""GALAXI Absorber plates"""

from nicos.core import Moveable
from nicos.core.params import Attach
from nicos.core.mixins import HasLimits

from math import log, sqrt


class AbsorberDevice(HasLimits, Moveable):
    """Main device for moving a combination of different absorbers in beam"""

    values = (3.68e0, 3.66e0, 9.52e0, 9.29e0, 3.62e1, 3.59e1, 9.12e1, 9.83e1,
              6.66e3, 6.70e3, 4.25e5, 4.18e5, 2.30e6, 2.30e6, 4.17e5)

    attached_devices = {
        'absorbers': Attach('Absorber', Moveable, multiple=14),
    }

    def doInit(self, mode):
        self.log.debug('Absorber init')
        self.read()

    def doRead(self, maxage=0):
        self.log.debug('Absorber read')
        currentValue = 1.0
        for (i, dev) in enumerate(self._attached_absorbers):
            if dev.read(maxage) == 'in':
                currentValue *= self.values[i]
        return currentValue

    def doStart(self, target):
        self.log.debug('Absorber start')
        if target < sqrt(min(self.values)):
            for dev in self._attached_absorbers:
                dev.move('out')
        else:
            index = self._acombi(target)
            index_nr = 0
            for (i, dev) in enumerate(self._attached_absorbers):
                if index[index_nr] == i:
                    dev.maw('in')
                    if index_nr < (len(index) - 1):
                        index_nr += 1
            index_nr = 0
            for (i, dev) in enumerate(self._attached_absorbers):
                if index[index_nr] != i:
                    dev.move('out')
                elif index_nr < len(index)-1:
                    index_nr += 1

    def _acombi(self,target):
        bestValue = self.values[0]
        bestDifference = abs(target - bestValue)
        bestIndices = [0]
        for val in range(1, pow(2,14) + 1):
            valueTmp = 1
            indicesTmp = []
            pos = 0
            maxBit = int(log(val,2))
            innerLoop = True
            while (pos <= maxBit) & innerLoop:
                if valueTmp >= target:
                    innerLoop = False
                mask = 1 << pos
                if (val & mask) == mask:
                    valueTmp = self.values[pos] * valueTmp
                    indicesTmp.append(pos)
                    differenceTmp = abs(target - valueTmp)
                    if differenceTmp < bestDifference:
                        bestDifference = differenceTmp
                        bestValue = valueTmp
                        bestIndices = indicesTmp
                pos += 1
        return bestIndices
