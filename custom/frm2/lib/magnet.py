#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
Supporting classes for FRM2-magnets (Garfield, MiraMagnet, ...)
"""

from nicos.core import Moveable
from nicos.devices.generic.sequence import SeqDev, SeqCall, SeqSleep
from nicos.devices.generic.magnet import BipolarSwitchingMagnet


class GarfieldMagnet(BipolarSwitchingMagnet):
    """Class for Garfield Magnet.

    uses a polarity switch ('+' or '-') to flip polarity and an onoff switch
    to cut power (to be able to switch polarity) in addition to an
    unipolar current source.

    Please try to avoid to build anything like this or get headaches!
    better version would be the MiraMagnet.
    """

    attached_devices = {
        'onoffswitch': (Moveable, 'Switch to set for on/off'),
        'polswitch':   (Moveable, 'Switch to set for polarity'),
    }

    def _get_field_polarity(self):
        sign = -1 if self._adevs['polswitch'].read() == '-' else +1
        if self._adevs['onoffswitch'].read() == 'off':
            return 0
        return sign

    def _seq_set_field_polarity(self, polarity, sequence):
        if polarity == 0:
            return
        pol, onoff = self._adevs['polswitch'], self._adevs['onoffswitch']
        # handle switching polarity

        sequence.append(SeqDev(onoff, 'off'))
        sequence.append(SeqSleep(0.3, 'disabling power'))
        sequence.append(SeqDev(pol, '+' if polarity > 0 else '-'))
        sequence.append(SeqSleep(0.3, 'switching polarity'))
        sequence.append(SeqDev(onoff, 'on'))
        sequence.append(SeqSleep(0.3, 'enabling power'))
        try:
            sequence.append(SeqCall(self._adevs['currentsource']._dev.deviceOn))
            sequence.append(SeqSleep(0.3, 're-enabling power source'))
        except Exception:
            pass # would fail on non taco devices and is only needed on those


class MiraMagnet(BipolarSwitchingMagnet):
    """Class for MiraMagnet

    second best way(*) to control a bipolar magnet, using two relays
    to put current directly (plusswitch) or reversed (minusswitch)
    into the coils. if both are activated, short the powerswitch
    to have a clean zero current in the coil.
    This also allows removing/reconnecting the coil without
    depowering the currentsource.

    (*) The best way would be to use a bipolar current supply.
    """

    attached_devices = {
        'plusswitch':  (Moveable, 'Switch to positive polarity'),
        'minusswitch': (Moveable, 'Switch to negative polarity'),
    }

    def _get_field_polarity(self):
        code = ','.join(self._adevs[n].read() for n in ('plusswitch', 'minusswitch'))
        if code == 'on,off':
            sign = +1
        elif code == 'off,on':
            sign = -1
        else:
            sign = 0 # off or short
        self.log.debug('Field polarity is %s' % sign)
        return sign

    def _seq_set_field_polarity(self, polarity, sequence):
        plus, minus = self._adevs['plusswitch'], self._adevs['minusswitch']
        # first switch on, then switch off
        subsequence = []
        if polarity >= 0 and plus.read(0) != 'on':
            subsequence.append(SeqDev(plus, 'on'))
        if polarity <=0 and minus.read(0) != 'on':
            subsequence.append(SeqDev(minus, 'on'))
        if subsequence:
            subsequence.append(SeqSleep(0.3, 'shorting output'))
            sequence.append(subsequence)
        if polarity < 0:
            sequence.append(SeqDev(plus, 'off'))
            sequence.append(SeqDev(minus, 'on'))   # due to bug in Phytron server.
            sequence.append(SeqSleep(0.3, 'switching to negative polarity'))
        elif polarity > 0:
            sequence.append(SeqDev(minus, 'off'))
            sequence.append(SeqSleep(0.3, 'switching to positive polarity'))

