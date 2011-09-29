#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

"""Definition of abstract base device classes."""

__version__ = "$Revision$"

import sys
import threading
from os import path
from time import time, sleep

from nicos import session
from nicos import status
from nicos.data import NeedsDatapath
from nicos.utils import readFileCounter, updateFileCounter
from nicos.device import Readable, Moveable, Measurable, \
     HasLimits, HasOffset, HasPrecision, Param, Override, usermethod


class Coder(HasPrecision, Readable):
    """Base class for all coders."""

    def doRead(self):
        """Returns the current position from encoder controller."""
        return 0

    def doSetPosition(self, target):
        """Sets the current position of the encoder controller to the target."""
        pass

    def doReset(self):
        """Resets the encoder controller."""
        pass


class Motor(HasLimits, Moveable, Coder, HasPrecision):
    """Base class for all motors.

    This class inherits from Coder since a Motor can be used instead of a true
    encoder to supply the current position to an Axis.
    """

    parameters = {
        'speed': Param('The motor speed', unit='main/s', settable=True),
    }

    @usermethod
    def setPosition(self, pos):
        """Sets the current position of the motor controller to the target."""
        self.doSetPosition(pos)

    def doInit(self):
        """Initializes the class."""
        pass

    def doStart(self, target):
        """Starts the movement of the motor to target."""
        pass

    def doRead(self):
        """Returns the current position from motor controller."""
        return 0

    def doSetPosition(self, target):
        """Sets the current position of the motor controller to the target."""
        pass

    def doReset(self):
        """Resets the motor controller."""
        pass

    def doStop(self):
        """Stops the movement of the motor."""
        pass


class Axis(HasLimits, HasOffset, HasPrecision, Moveable):
    """Base class for all axes."""

    parameters = {
        'dragerror': Param('The so called \'Schleppfehler\' of the axis',
                           unit='main', default=1, settable=True),
        'maxtries':  Param('Number of tries to reach the target', type=int,
                           default=3, settable=True),
        'loopdelay': Param('The sleep time when checking the movement',
                           unit='s', default=0.3, settable=True),
        'backlash':  Param('The maximum allowed backlash', unit='main',
                           settable=True),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False, settable=True),
    }

    @usermethod
    def setPosition(self, pos):
        """Sets the current position of the motor controller to the target."""
        self.doSetPosition(pos)

    def doSetPosition(self, target):
        """Sets the current position of the motor controller to the target."""
        pass


class ImageStorage(NeedsDatapath):
    """
    Mixin for detectors that store images in their own directory.
    """

    parameters = {
        'subdir': Param('Subdirectory name for the image files',
                        type=str, mandatory=True),
        'nametemplate': Param('Template for data file names',
                              type=str, default='%08d.dat', settable=True),
        # XXX this is awkward with simulation mode
        'lastfilename': Param('File name of the last measurement',
                              type=str, settable=True),
        'lastfilenumber': Param('File number of the last measurement',
                                type=int, settable=True),
    }

    def doReadDatapath(self):
        return session.experiment.datapath

    def doUpdateDatapath(self, value):
        # always use only first data path
        self._datapath = path.join(value[0], self.subdir)
        self._counter = readFileCounter(path.join(self._datapath, 'counter'))
        self._setROParam('lastfilenumber', self._counter)
        self._setROParam('listfilename', self.nametemplate % self._counter)

    def _newFile(self):
        if self._datapath is None:
            self.datapath = session.experiment.datapath
        self.lastfilename = path.join(
            self._datapath, self.nametemplate[self.mode] % self._counter)
        self.lastfilenumber = self._counter
        self._counter += 1
        updateFileCounter(path.join(self._datapath, 'counter'), self._counter)

    def _writeFile(self, content):
        with open(self.lastfilename, 'w') as fp:
            fp.write(content)


class AsyncDetector(Measurable):
    """
    Base class for a detector that needs to execute code during measurement.
    """

    # hooks

    def _devStatus(self):
        """Executed to determine if there are hardware errors.

        Return None if the device state is fine, and an error status tuple
        otherwise.
        """
        return None

    def _preStartAction(self, **preset):
        """Action to run before starting measurement.  This should set the
        preset in the detector.
        """
        raise NotImplementedError

    def _startAction(self):
        """Action to start the actual measurement, run in the thread."""
        raise NotImplementedError

    def _measurementComplete(self):
        """Ask the hardware if the measurement is complete."""
        raise NotImplementedError

    def _duringMeasureAction(self, elapsedtime):
        """Action to run during measurement."""
        pass

    def _afterMeasureAction(self):
        """Action to run after measurement (e.g. saving the data)."""
        raise NotImplementedError

    def _measurementFailedAction(self, err):
        """Action to run when measurement failed."""
        pass

    # end hooks

    def doInit(self):
        self._measure = threading.Event()
        self._processed = threading.Event()
        self._processed.set()
        if self._mode != 'simulation':
            self._thread = threading.Thread(target=self._thread_entry)
            self._thread.setDaemon(True)
            self._thread.start()

    def doStart(self, **preset):
        self._processed.wait()
        self._processed.clear()
        try:
            self._preStartAction(**preset)
        except:
            self._processed.set()
            raise
        self._measure.set()

    def doStatus(self):
        st = self._devStatus()
        if st is not None:
            return st
        elif self._measure.isSet():
            return status.BUSY, 'measuring'
        elif not self._processed.isSet():
            return status.BUSY, 'processing',
        return status.OK, 'idle'

    def doIsCompleted(self):
        return not self._measure.isSet() and self._processed.isSet()

    def _thread_entry(self):
        while True:
            try:
                # wait for start signal
                self._measure.wait()
                # start measurement
                self._startAction()
                started = time()
                # wait for completion of measurement
                while True:
                    sleep(0.2)
                    if self._measurementComplete():
                        return
                    self._duringMeasureAction(time() - started)
            except:
                self._measurementFailedAction(sys.exc_info()[1])
                self.log.exception('measuring failed')
                self._measure.clear()
                self._processed.set()
                continue
            self._measure.clear()
            try:
                self._afterMeasureAction()
            except:
                self._measurementFailedAction(sys.exc_info()[1])
                self.log.exception('completing measurement failed')
            finally:
                self._processed.set()
