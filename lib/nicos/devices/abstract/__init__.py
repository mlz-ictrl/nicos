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

"""Definition of abstract base device classes."""

import sys
import threading
from os import path
from time import time, sleep
import numpy as np

from nicos import session
from nicos.core import status, usermethod, Device, DeviceMixinBase, \
     Readable, Moveable, Measurable, HasLimits, HasOffset, HasPrecision, \
     HasMapping, ConfigurationError, \
     ModeError, ProgrammingError, PositionError, InvalidValueError
from nicos.core.params import subdir, Param, Override, oneof
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


class Motor(Coder, HasLimits, Moveable):  #pylint: disable=W0223
    """Base class for all motors.

    This class inherits from Coder since a Motor can be used instead of a true
    encoder to supply the current position to an Axis.
    """

    parameters = {
        'speed': Param('The motor speed', unit='main/s', settable=True),
    }


class Axis(HasOffset, HasPrecision, HasLimits, Moveable):
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


class CanReference(DeviceMixinBase):
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


class ImageSaver(Device):
    """
    Abstract baseclass for saving >=2D image type data

    Each ImageSaver/FileFormat needs to write either:
    * into a different subdir
    * name files differently to avoid nameclashes
    (both would also be ok.)
    """
    parameters = {
        'subdir': Param('Subdirectory name for the image files',
                        type=subdir, mandatory=True),
        'nametemplate': Param('Template for data file names',
                              type=str, default='%08d.dat', settable=True),
    }

    def prepareImage(self, subdir='', *args):
        """should prepare an Imagefile in the given subdir"""
        exp = session.experiment
        s, l, f = exp.createImageFile(self.nametemplate, subdir, self.subdir)
        self._filename = s
        self._filepath = l
        self._file = f

    def addHeader(self, *args):
        """Adds headerinfo to the file, may be called several times..."""
        # may also store the info first and write it to the file in saveImage later...
        pass

    def saveImage(self, content, *args):
        """Saves the given image content

        content MUST be a numpy array with the right shape
        if the fileformat to be supported has image shaping options,
        they should be applied here.
        """
        # stupid validator, making sure we have a numpy.array:
        # content = np.array(content)

    def updateImage(self, content, *args):
        """updates the image with the given content

        usefull for live-displays or fileformats wanting to store several
        states of the data-aquisition
        """

    def finalizeImage(self, *args):
        """finalizes the on-disk image, normally just a close"""
        if self._file:
            self._file.close()
            self._file = None
        else:
            raise ProgrammingError(self, 'finalize before prepare or file '
                                          'could not be created!', exc=1)


class ImageStorage(DeviceMixinBase):
    """
    Mixin for detectors that store images.

    ALL detectors storing images MUST subclass this.
    """

    attached_devices = {
        'fileformats' : ([ImageSaver],'Filesavers for all wanted fileformats.')
    }

    parameters = {
        'subdir': Param('Subdirectory name for the image files',
                        type=subdir, mandatory=True),
        'nametemplate': Param('Template for data file names',
                              type=str, default='%08d.dat', settable=True),
    }

    _file = None

    def _newFile(self):
        exp = session.experiment
        sname, lname, fp = exp.createImageFile(self.nametemplate, self.subdir)
        self._imagename = sname
        self._relpath = lname
        self._file = fp
        self._counter = session.experiment.lastimage

    def _writeFile(self, content, writer=file.write):
        if self._file is None:
            raise ProgrammingError(self, '_writeFile before _newFile, '
                                          'FIX CODE!', exc=1)
        try:
            writer(self._file, content)
        finally:
            self._file.close()
            self._file = None

    #
    # multiplier for Saving Fileformats.... used by later patches....
    #
    def prepareImage(self, *args):
        """should prepare an Imagefile"""
        for ff in self._adevs['fileformats']:
            ff.prepareImage(self.subdir, *args)

    def addHeader(self, *args):
        """Adds headerinfo to the file, may be called several times..."""
        for ff in self._adevs['fileformats']:
            ff.addHeader(*args)

    def saveImage(self, *args):
        """Saves the given image content"""
        for ff in self._adevs['fileformats']:
            ff.saveImage(*args)

    def updateImage(self, *args):
        """updates the given image content"""
        for ff in self._adevs['fileformats']:
            ff.updateImage(*args)

    def finalizeImage(self, *args):
        """finalize/close image"""
        for ff in self._adevs['fileformats']:
            ff.finalizeImage(*args)


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


# MappedReadable and MappedMoveable operate (via read/start) on a set of
# predefined values which are mapped via the mapping parameter onto
# device-specific (raw) values.

class MappedReadable(HasMapping, Readable):
    """Base class for all read-only value-mapped devices
    (also called selector or multiplexer/mux).

    Subclasses need to define their attached devices and
    implement a _readRaw(), returning (raw) device values.
    Subclasses should also implement a doStatus().
    Subclasses reimplementing doInit() need to call this class' doInit().
    """

    def doInit(self, mode):
        if self.fallback in self.mapping:
            raise ConfigurationError(self, 'Value of fallback parameter is '
                                     'not allowed to be in the mapping!')
        self._inverse_mapping = {}
        for k, v in self.mapping.iteritems():
            self._inverse_mapping[v] = k

    def doStatus(self, maxage=0):
        """May be derived in subclasses to yield the current status of the device.

        Shall never raise, but return status.NOTREACHED instead....
        """
        try:
            r = self.read(maxage)
            if r == self.fallback:
                return status.NOTREACHED, 'not one of the configured values'
            return status.OK, 'idle'
        except PositionError, e:
            return status.NOTREACHED, str(e)

    def doRead(self, maxage=0):
        return self._mapReadValue(self._readRaw(maxage))

    def _mapReadValue(self, value):
        """Hook for integration of mapping/switcher devices.

        shall be redefined in derived classes, default implementation is a NOP
        Allowed actions are transformation of the given value, readonly access
        to self attributes.
        This is the right place for the _inverse_mapping....
        """
        if value in self._inverse_mapping:
            return self._inverse_mapping[value]
        elif self.relax_mapping:
            if self.fallback is not None:
                return self.fallback
        else:
            raise PositionError(self, 'unknown unmapped position %r' % value)

    def _readRaw(self, maxage=0):
        """Reads the unmapped/raw value from the device.

        Must be implemented in derived classes!
        """
        raise ProgrammingError(self, 'Somebody please implement a proper '
                               '_readRaw or doRead method!')


class MappedMoveable(MappedReadable, Moveable):
    """Base class for all moveable value-mapped devices

    Subclasses need to define their attached devices and
    implement _readRaw() and _startRaw(), operating on raw values.
    Subclasses should also implement a doStatus().
    Subclasses reimplementing doInit() need to call this class' doInit().
    """

    # set this to true in derived classes to allow passing values out of mapping
    relax_mapping = False

    def doInit(self, mode):
        # be restrictive?
        if not self.relax_mapping:
            self.valuetype = oneof(*self.mapping)
        MappedReadable.doInit(self, mode)

    def doStart(self, target):
        return self._startRaw(self._mapTargetValue(target))

    def _mapTargetValue(self, target):
        """Hook for integration of mapping/switcher devices.

        shall be redefined in derived classes, default implementation is a NOP.
        Allowed actions are transformation of the given value, readonly access
        to self attributes.
        If there is a mapping defined, here the forward mapping should be used.
        """
        if not self.relax_mapping:
            # be strict...
            if target not in self.mapping:
                positions = ', '.join(repr(pos) for pos in self.mapping)
                raise InvalidValueError(self, '%r is an invalid position for '
                                        'this device; valid positions are %s'
                                        % (target, positions))
        return self.mapping.get(target, target)

    def _startRaw(self, target):
        """Initiate movement to the unmapped/raw value from the device.

        Must be implemented in derived classes!
        """
        raise ProgrammingError(self, 'Somebody please implement a proper '
                               '_startRaw or doStart method!')
