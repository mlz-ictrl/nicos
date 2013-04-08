#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

from __future__ import with_statement

__version__ = "$Revision$"

import sys
import threading
from os import path
from time import time, sleep

from nicos import session
from nicos.core import status, Device, Readable, Moveable, Measurable, \
     HasLimits, HasOffset, HasPrecision, Param, Override, usermethod, \
     ModeError, ProgrammingError
from nicos.devices.datasinks import NeedsDatapath
from nicos.utils import readFileCounter, updateFileCounter


class Coder(HasPrecision, Readable):
    """Base class for all coders."""

    @usermethod
    def setPosition(self, pos):
        """Sets the current position of the controller to the target.

        This operation is forbidden in slave mode, and does the right thing
        virtually in simulation mode.

        .. method:: doSetPosition(pos)

           This is called to actually set the new position in the hardware.
        """
        if self._mode == 'slave':
            raise ModeError(self, 'setting new position not possible in '
                            'slave mode')
        elif self._sim_active:
            self._sim_setValue(pos)
            return
        self.doSetPosition(pos)
        if self._cache:
            self._cache.invalidate(self, 'value')

    def doSetPosition(self, pos):
        raise NotImplementedError('implement doSetPosition for concrete coders')


class Motor(HasLimits, Moveable, Coder, HasPrecision):  #pylint: disable=W0223
    """Base class for all motors.

    This class inherits from Coder since a Motor can be used instead of a true
    encoder to supply the current position to an Axis.
    """

    parameters = {
        'speed': Param('The motor speed', unit='main/s', settable=True),
    }


class Axis(HasLimits, HasOffset, HasPrecision, Moveable):
    """Base class for all axes."""

    parameters = {
        'dragerror': Param('Maximum deviation of motor and coder when read out '
                           'during a positioning step', unit='main', default=1,
                           settable=True),
        'maxtries':  Param('Number of tries to reach the target', type=int,
                           default=3, settable=True),
        'loopdelay': Param('The sleep time when checking the movement',
                           unit='s', default=0.3, settable=True),
        'backlash':  Param('The backlash for the axis: if positive/negative, '
                           'always approach from positive/negative values',
                           unit='main', default=0, settable=True),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False, settable=True),
    }


class CanReference(object):
    """
    Mixin class for axis devices that want to provide a 'reference' method.

    Concrete implementations must provide a 'doReference' method.  It can
    return the new current position after referencing or None.
    """

    @usermethod
    def reference(self, *args):
        """Do a reference drive of the axis."""
        if self._mode == 'slave':
            raise ModeError(self, 'referencing not possible in slave mode')
        elif self._sim_active:
            return
        elif hasattr(self, 'fixed') and self.fixed:
            self.log.error('device fixed, not referencing: %s' % self.fixed)
            return
        newpos = self.doReference(*args)
        if newpos is None:
            newpos = self.read(0)
        return newpos


class ImageStorage(Device, NeedsDatapath):
    """
    Mixin for detectors that store images in their own directory.
    """

    parameters = {
        'subdir': Param('Subdirectory name for the image files',
                        type=str, mandatory=True),
        'nametemplate': Param('Template for data file names',
                              type=str, default='%08d.dat', settable=True),
        'lastfilename': Param('File name of the last measurement',
                              type=str, settable=True),
        'lastfilenumber': Param('File number of the last measurement',
                                type=int, settable=True),
        'filecounter':  Param('File path to write the current file counter '
                              '(or empty to use a default file path)',
                              type=str),
    }

    def doUpdateDatapath(self, value):
        # always use only first data path
        self._datapath = path.join(value[0], self.subdir)
        self._readCurrentCounter()

    def _readCurrentCounter(self):
        self._counter = readFileCounter(self.filecounter or
                                        path.join(self._datapath, 'counter'))
        self._setROParam('lastfilenumber', self._counter)
        self._setROParam('lastfilename', self._getFilename(self._counter))

    def _getFilename(self, counter):
        return self.nametemplate % counter

    def _newFile(self, increment=True):
        if self._datapath is None:
            self.datapath = session.experiment.datapath
        if self.lastfilenumber != self._counter:
            # inconsistent state -- better read the on-disk counter
            self._readCurrentCounter()
        if increment:
            self._counter += 1
        updateFileCounter(self.filecounter or
                          path.join(self._datapath, 'counter'), self._counter)
        self.lastfilename = path.join(self._datapath,
                                      self._getFilename(self._counter))
        self.lastfilenumber = self._counter

    def _writeFile(self, content, exists_ok=False, writer=file.write):
        if path.isfile(self.lastfilename) and not exists_ok:
            raise ProgrammingError(self, 'data file %r already exists' %
                                   self.lastfilename)
        with open(self.lastfilename, 'w') as fp:
            writer(fp, content)


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

    def _startAction(self, **preset):
        """Action to run before starting measurement.  This should set the
        preset in the detector and start the measurement.
        """
        raise NotImplementedError('implement _startAction')

    def _measurementComplete(self):
        """Ask the hardware if the measurement is complete."""
        raise NotImplementedError('implement _measurementComplete')

    def _duringMeasureAction(self, elapsedtime):
        """Action to run during measurement."""
        pass

    def _afterMeasureAction(self):
        """Action to run after measurement (e.g. saving the data)."""
        raise NotImplementedError('implement _afterMeasureAction')

    def _measurementFailedAction(self, err):
        """Action to run when measurement failed."""
        pass

    # end hooks

    def doInit(self, mode):
        self._measure = threading.Event()
        self._processed = threading.Event()
        self._processed.set()
        if self._mode != 'simulation':
            self._thread = threading.Thread(target=self._thread_entry,
                                            name='AsyncDetector %s' % self)
            self._thread.setDaemon(True)
            self._thread.start()

    def doStart(self, **preset):
        self._processed.wait()
        self._processed.clear()
        try:
            self._startAction(**preset)
        except:
            self._processed.set()
            raise
        else:
            self._measure.set()

    def doStatus(self, maxage=0):
        st = self._devStatus()
        if st is not None:
            return st
        elif self._measure.isSet():
            return status.BUSY, 'measuring'
        elif not self._processed.isSet():
            return status.BUSY, 'processing'
        return status.OK, ''

    def doIsCompleted(self):
        return not self._measure.isSet() and self._processed.isSet()

    def _thread_entry(self):
        while True:
            try:
                # wait for start signal
                self._measure.wait()
                # start measurement
                #self._startAction()
                started = time()
                # wait for completion of measurement
                while True:
                    sleep(0.2)
                    if self._measurementComplete():
                        break
                    self._duringMeasureAction(time() - started)
            except Exception:
                self._measurementFailedAction(sys.exc_info()[1])
                self.log.exception('measuring failed')
                self._measure.clear()
                self._processed.set()
                continue
            self._measure.clear()
            try:
                self._afterMeasureAction()
            except Exception:
                self._measurementFailedAction(sys.exc_info()[1])
                self.log.exception('completing measurement failed')
            finally:
                self._processed.set()
