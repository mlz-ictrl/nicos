#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""
Supporting classes for FRM2 magnets, currently only Garfield (amagnet).
"""

from nicos.core import Moveable, Attach, Param, Override, tupleof, dictof, \
    status, HasLimits
from nicos.devices.generic.sequence import SeqDev, SeqSleep
from nicos.devices.generic.magnet import BipolarSwitchingMagnet


class GarfieldMagnet(BipolarSwitchingMagnet):
    """Garfield Magnet

    uses a polarity switch ('+' or '-') to flip polarity and an onoff switch
    to cut power (to be able to switch polarity) in addition to an
    unipolar current source.

    Please try to avoid to build anything like this or get headaches!
    Better version would be the MiraMagnet.
    """

    attached_devices = {
        'onoffswitch': Attach('Switch to set for on/off', Moveable),
        'polswitch':   Attach('Switch to set for polarity', Moveable),
        'symmetry':    Attach('Switch to read for symmetry', Moveable),
    }

    parameters = {
        'calibrationtable': Param('Map of Coefficients for calibration  per symmetry setting',
                                  type=dictof(str, tupleof(
                                      float, float, float, float, float)),
                                  mandatory=True,),
    }

    parameter_overrides = {
        'calibration': Override(volatile=True, settable=False, mandatory=False),
    }

    def doWriteUserlimits(self, limits):
        abslimits = self.abslimits
        # include 0 in limits
        lmin = min(max(limits[0], abslimits[0]), 0)
        lmax = max(min(limits[1], abslimits[1]), 0)
        newlimits = (lmin, lmax)
        self.log.debug('Set limits: %r' % (newlimits,))
        HasLimits.doWriteUserlimits(self, newlimits)
        # intentionally not calling CalibratedMagnet.doWriteUserlimits
        # we do not want to change the limits of the current source
        return newlimits

    def doReadCalibration(self):
        symval = self._attached_symmetry.read()
        return self.calibrationtable.get(symval, (0.0, 0.0, 0.0, 0.0, 0.0))

    def doWriteCalibration(self, cal):
        symval = self._attached_symmetry.read()
        self.calibrationtable[symval] = cal

    def _get_field_polarity(self):
        sign = int(self._attached_polswitch.read())
        if self._attached_onoffswitch.read() == 'off':
            return 0
        return sign

    def doReset(self):
        if self._attached_onoffswitch.status()[0] == status.ERROR:
            self._attached_onoffswitch.reset()
            self._attached_onoffswitch.move('on')
            # immediate action, no need to wait....

    def _seq_set_field_polarity(self, polarity, sequence):
        if polarity == 0:
            return
        pol, onoff = self._attached_polswitch, self._attached_onoffswitch
        # handle switching polarity

        sequence.append(SeqDev(onoff, 'off'))
        sequence.append(SeqSleep(0.3, 'disabling power'))
        sequence.append(SeqDev(pol, '%+d' % polarity))
        sequence.append(SeqSleep(0.3, 'switching polarity'))
        sequence.append(SeqDev(onoff, 'on'))
        sequence.append(SeqSleep(0.3, 'enabling power'))
