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
from nicos import session
from nicos.core import Attach, DataSink, DataSinkHandler, Moveable, Readable
from nicos.core.utils import multiWait


class BoaShutterHandler(DataSinkHandler):

    _startDataset = None

    def _moveShutter(self, target):
        if self.sink._attached_auto.read(0) == 'auto':
            session.log.info('Moving shutter to %s', target)
            self.sink._attached_shutter1.start(target)
            multiWait([self.sink._attached_shutter1])

    def prepare(self):
        DataSinkHandler.prepare(self)
        if not self._startDataset:
            self._startDataset = self.dataset
            self._moveShutter('open')

    def end(self):
        DataSinkHandler.end(self)
        if self.dataset == self._startDataset:
            self._moveShutter('closed')
            self._startDataset = None


class BoaShutterSink(DataSink):
    """
    This class abuses the DataSink interface to open and close the
    BOA experiment shutters when a scan begins or ends. This is conditional
    on a ManualMove which decides if automatic shutter management is enabled
    or not.
    """
    attached_devices = {
        'shutter1': Attach('First shutter to open', Moveable),
        'auto': Attach('Devices which knows if we are in automatic '
                       'or manual mode',
                       Readable),

    }
    handlerclass = BoaShutterHandler


class DummyHandler(DataSinkHandler):
    """
    Just a place holder doing nothing
    """


class DummySink(DataSink):
    """
    Just a dummy sink doing nothing
    """
    handlerclass = DummyHandler
