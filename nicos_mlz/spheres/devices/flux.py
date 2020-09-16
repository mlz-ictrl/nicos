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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# *****************************************************************************

from nicos.core.params import Param, listof
from nicos.devices.tango import VectorInput


class Flux(VectorInput):
    """Device which stores the flux averages over the relevant detectors.
    """

    parameters = {
        'fluxvalues': Param('Raw flux values', internal=True,
                            type=listof(listof(int)))
    }

    def init(self):
        VectorInput.init(self)
        self._fluxvalues = [[], [], []]

    def doPoll(self, i, maxage):
        val = self.doRead()
        self._pollParam('fluxvalues')

        return self.status(), val

    def doReadFluxvalues(self):
        if not hasattr(self, '_fluxvalues'):
            self.doRead()
        return self._fluxvalues

    def doRead(self, maxage=0):
        flux = self._dev.GetFlux()

        if len(flux) != 16*6:
            self.log.warning('SIS returned %d flux values, expected %d',
                             len(flux), 16*6)
            return [0, 0, 0]

        # pylint: disable=unbalanced-tuple-unpacking
        cElast, cInelast, cDir, tElast, tInelast, tDir = self.split(flux, 16)
        rDets = self._dev.GetRegularDetectors()

        self._fluxvalues = [cElast, cInelast, cDir]

        elast = [sum([x for i, x in enumerate(cElast) if i in rDets]),
                 sum([x for i, x in enumerate(tElast) if i in rDets])]
        inelast = [sum([x for i, x in enumerate(cInelast) if i in rDets]),
                   sum([x for i, x in enumerate(tInelast) if i in rDets])]
        direct = [sum([x for i, x in enumerate(cDir) if i in rDets]),
                  sum([x for i, x in enumerate(tDir) if i in rDets])]

        if not elast[1]:
            elastic = 0
        else:
            elastic = int(elast[0]/2e-5/elast[1])

        if not inelast[1]:
            inelastic = 0
        else:
            inelastic = int(inelast[0]/2e-5/inelast[1])
        if not direct[1]:
            direct = 0
        else:
            direct = int(direct[0]/2e-5/direct[1])

        return [elastic, inelastic, direct]

    def split(self, inp, chunksize):
        output = []
        index = 0
        listsize = len(inp)

        while index < listsize:
            output.append([int(x) for x in inp[index:index + chunksize]])
            index += chunksize

        return output
