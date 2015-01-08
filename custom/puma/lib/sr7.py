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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for PUMA SR7 shutter control."""

from nicos.core import Moveable, Readable, PositionError, oneof, \
     status, waitForStatus, Override


class SR7Shutter(Moveable):
    """Class for the PUMA secondary shutter."""

    attached_devices = {
        'sr7cl':     (Readable, 'status of SR7 shutter closed/open'),
        'sr7p1':     (Readable, 'status of SR7 position 1'),
        'sr7p2':     (Readable, 'status of SR7 position 2'),
        'sr7p3':     (Readable, 'status of SR7 position 3'),
        #'hdiacl':    (Readable, 'status of virtual source closed/open'),
        #'stopinh':   (Readable, 'status of emergency button active/inactive'),
        #'sr7save':   (Readable, 'SR7 security circle ok for open the beam'),
        'sr7set':    (Moveable, 'emergency close of all shutters'),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False, default='')
    }

    positions = ['close', 'S1', 'S2', 'S3']
    valuetype = oneof(*positions)

    def doIsAllowed(self, pos):
        # only shutter close is allowed
        if pos != 'close':
            return False, 'can only close shutter from remote'
        return True, ''

    def doStart(self, pos):
        if pos == self.read(0):
            return
        self._adevs['sr7set'].start(self.positions.index(pos))
        if self.wait() != pos:
            raise PositionError(self, 'device returned wrong position')
        self.log.info('SR7: %s' % pos)

    def doWait(self):
        waitForStatus(self, timeout=5)

    def doRead(self, maxage=0):
        res = self.doStatus()[0]
        if res == status.OK:
            if self._adevs['sr7cl'].doRead() == 1:
                return 'close'
            elif self._adevs['sr7p1'].doRead() == 1:
                return 'S1'
            elif self._adevs['sr7p2'].doRead() == 1:
                return 'S2'
            elif self._adevs['sr7p3'].doRead() == 1:
                return 'S3'
        else:
            raise PositionError(self, 'SR7 shutter moving or undefined')

    def doStatus(self, maxage=0):
        cl, p1, p2, p3 = self._adevs['sr7cl'].doRead(), \
            self._adevs['sr7p1'].doRead(), self._adevs['sr7p2'].doRead(), \
            self._adevs['sr7p3'].doRead()
        if p1 == 1 and p2 == 1 and p3 == 1:
            return status.BUSY, 'moving'
        elif cl == 1 or p1 == 1 or p2 == 1 or p3 == 1:
            return status.OK, 'idle'
        else:
            return status.ERROR, 'undefined position'
