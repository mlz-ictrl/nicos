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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
from nicos.core import Param
from nicos.core.device import Moveable, Override, listof
from nicos.core.errors import InvalidValueError
from nicos.utils import createSubprocess


class ProcDevice(Moveable):
    """
    A little device class which runs an external process and allows to
    wait for it to finish.
    """

    parameters = {'subprocess': Param('Path of subprocess to run',
                                      type=str, mandatory=True),
                  'args': Param('Arguments for the subprocess',
                                type=listof(str), mandatory=True), }

    parameter_overrides = {
        'unit': Override(description='(not used)', mandatory=False),
    }
    _subprocess = None

    def doStart(self, target):
        if self._subprocess is not None:
            raise InvalidValueError('Process is still running')

        fullargs = list(self.args)
        fullargs.insert(0, self.subprocess)
        self._subprocess = createSubprocess(fullargs)

    def doIsCompleted(self):
        if self._subprocess is None:
            return True
        ret = self._subprocess.poll()
        if ret is None:
            return False
        else:
            self._subprocess = None
            return True

    def doRead(self, maxage=0):
        return .0

    def doStop(self):
        if self._subprocess is not None:
            self._subprocess.terminate()
