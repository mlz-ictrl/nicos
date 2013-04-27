#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""MIRA specific axis classes."""

import IO

from nicos.devices.taco.axis import Axis as TacoAxis


class PhytronAxis(TacoAxis):
    def _reset_phytron(self):
        motor = self._getMotor()
        iodev = self._taco_guard(motor.deviceQueryResource, 'iodev')
        addr = self._taco_guard(motor.deviceQueryResource, 'address')
        client = IO.StringIO(iodev)
        self.log.info('Resetting Phytron controller...')
        pvals = {}
        # find out number and names of axes in controller
        AXISNAMES = ['X', 'Y', 'Z', 'W']
        sui = self._taco_guard(client.communicate, '\x02%sSUI' % addr).rstrip('\x03')
        # SUI return: \x02\x06I=XYZ...
        axes = AXISNAMES[:len(sui) - 4]
        # query all parameters (1-50) for all axes and store them
        for axis in axes:
            for pnum in range(50):
                response = self._taco_guard(client.communicate, '\x02%s%sP%dR' %
                                            (addr, axis, pnum)).rstrip('\x03')
                if response[1] == '\x06':
                    pvals[axis, pnum] = response[2:]
        # do the controller reset
        self._taco_guard(client.communicate, '\x02%sCR' % addr)
        # re-set value of all parameters for all axes
        for (axis, pnum), pval in pvals.iteritems():
            self._taco_guard(client.communicate, '\x02%s%sP%dS%s' %
                             (addr, axis, pnum, pval))
        self.log.info('Phytron reset complete')

    def doReset(self):
        TacoAxis.doReset(self)
        self._reset_phytron()
