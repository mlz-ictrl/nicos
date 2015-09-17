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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import time

from nicos.core import Param, Attach, status
from nicos.devices.generic import Switcher
from nicos.devices.vendor.lima import Andor2LimaCCD


class AntaresIkonLCCD(Andor2LimaCCD):
    """
    Extension to Andor2LimaCCD; Adds the ability to open shutter before the
    acquisition and close them afterwards.

    The given shutter devices MUST BE of type <nicos.devices.generic.Switcher>
    and MUST HAVE the values 'open' and 'closed'.  This state is enforced to
    avoid setups that configure almighty monster-detectors.
    """

    attached_devices = {
        'fastshutter': Attach('Fast shutter switcher device', Switcher),
    }

    parameters = {
        'openfastshutter': Param('Open fast shutter before the acquisition. '
                                 'Caution: It has to be closed manually',
                                 type=bool, settable=True, default=True),
    }

    def doStart(self, **preset):
        # open fastshutter automatically if desired
        if self.shuttermode in ['always_open', 'auto'] and self.openfastshutter:
            # reset fast shutter if in error state (the shutter sometimes goes
            # into error state because it couldn't be opened, but it works
            # again after reset on the next try
            fastshutter = self._adevs['fastshutter']
            if fastshutter.status(0)[0] == status.ERROR:
                self.log.warning('resetting fast shutter before opening: it is'
                                 ' in error state')
                fastshutter.reset()
            fastshutter.move('open')

            # wait some time due to a bug in the jcns tango servers
            # (the moving status isn't set immediately)
            time.sleep(0.1)

        Andor2LimaCCD.doStart(self, **preset)

    def doSave(self, exception=False):
        if exception:
            return
        Andor2LimaCCD.doSave(self, exception)
