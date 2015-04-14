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

"""Special device for Refsans slits"""


#~ from time import sleep
from math import tan, radians

from nicos.core import Moveable, HasPrecision, Param, Value, Override, oneof, \
    AutoDevice, tupleof, dictof, multiWait, multiReset, ProgrammingError
from nicos.utils import lazy_property
from nicos.devices.abstract import CanReference


class Opening(object):
    """should make handling slits and offsets and stuff easier"""
    def __init__(self, center, height):
        self.center = center
        self.height = height
        self.bottom = center - height / 2.
        self.top = center + height / 2.


RAW = 'raw'
CENTER = 'center'
NORMAL = 'normal'

class Slit(CanReference, Moveable):
    """A Refsans slit consisting of two blades with shapes in them.

    Normally, the ``bottom`` and ``top`` devices need to share a common
    coordinate system, i.e. when ``bottom.read() == top.read()`` the slit is
    closed. Positions are with respect to a ground-based fixed reference location,
    i.e. more positive numbers indicate a higher position, further away from earth.
    The slit opening, aka. `height` is ``height = top.read() - bottom.read()``.

    All positional Values are with respect to the center of the selected shape.
    `leftshape` and `rightshape` can be set individually or in a combined way, using `shape`.
    All instances have attributes controlling single dimensions that can be used
    as devices, for example in scans.  These attributes are:

    * `first`, `second` -- controlling the blades individually
    * `top`, `bottom` -- controlling the vertical opening.
    * `center`, `height` -- controlling "logical"
      coordinates of the slit

    The parameter `opmode` selects which pair is normally used for read/start
    operations.
    * `raw` controls the blades directly
    * `normal` controls `top`and `bottom`
    * `center` controls `center` and `height`

    The behaviour is undefined if several subdevices are moved simultaenously.

    Example usage::

        >>> move(slit.center, 5)        # move slit center
        >>> scan(slit.height, 0, 1, 6)  # scan over slit width from 0 to 5 mm
        >>> move(slit, (0, 5))          # in CENTER mode: move slit to center=0, height=5
    """

    attached_devices = {
        'first':   (HasPrecision, 'First Blade (normally also used for top)'),
        'second':  (HasPrecision, 'Second Blade (normally also used for bottom)'),
    }

    parameters = {
        'opmode': Param('Mode of operation for the slit',
                        type=oneof(RAW, CENTER, NORMAL),
                        settable=True,
                       ),
        'shape': Param('Selected combined shape of the slitsystem',
                       type=oneof('will', 'be', 'replaced'),
                       settable=True, chatty=True,
                      ),
        'leftshape': Param('Selected left shape of the slitsystem',
                           type=oneof('will', 'be', 'replaced'),
                           settable=True,
                          ),
        'rightshape': Param('Selected right shape of the slitsystem',
                            type=oneof('will', 'be', 'replaced'),
                            settable=True,
                           ),
        'leftshapes' : Param('Translates shape name to shape center and ' \
                             'height for 1st slit',
                             type=dictof(str, tupleof(float, float)),
                             mandatory=True, userparam=False,
                            ),
        'rightshapes' : Param('Translates shape name to shape center and ' \
                              'height for 2nd slit',
                              type=dictof(str, tupleof(float, float)),
                              mandatory=True, userparam=False,
                             ),
        'distance'    : Param('Horizontal Distance between the two subslits in main units',
                              type=float, unit='main'),
        'tilt'        : Param('Tilt of the beam, in degrees. Negative=going down.',
                              type=float, unit='deg', settable=True),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%.2f %.2f'),
        'unit': Override(mandatory=False, default='mm'),
    }

    valuetype = tupleof(float, float)

    # we are not talking to HW directly:
    hardware_access = False

    def doInit(self, mode):
        # set up validators:
        self._shapes = {}
        for l in self.leftshapes:
            for r in self.rightshapes:
                self._shapes[l+'x'+r] = l, r

        self.parameters['shape'].type.vals = sorted(self._shapes.keys())
        self.parameters['leftshape'].type.vals = sorted(self.leftshapes.keys())
        self.parameters['rightshape'].type.vals = sorted(self.rightshapes.keys())

        # sanity checks (raising here would prevent the device from being
        #                created, so you can adjust the wrong value!)
        if self.leftshape not in self.leftshapes:
            self.log.warning('unknown left shape %r, using %r instead' % \
                             (self.leftshape, self.leftshapes.keys()[0]))
            self._setROParam('leftshape', self.leftshapes.keys()[0])
        if self.rightshape not in self.rightshapes:
            self.log.warning('unknown right shape %r, using %r instead' % \
                             (self.rightshape, self.rightshapes.keys()[0]))
            self._setROParam('rightshape', self.rightshapes.keys()[0])

        # init private stuff
        self._leftOpening = Opening(*self.leftshapes[self.leftshape])
        self._rightOpening = Opening(*self.rightshapes[self.rightshape])

        # generate auto devices
        for name, idx, mode in [
            ('center', 0, CENTER), ('height', 1, CENTER),
            ('top', 0, NORMAL), ('bottom', 1, NORMAL),
            ('first', 0, RAW), ('second', 1, RAW)]:
            self.__dict__[name] = SlitAxis(self.name+'.'+name, slit=self,
                                           unit=self.unit, lowlevel=True,
                                           index=idx, opmode=mode)

        self._motors = [self._adevs['first'], self._adevs['second']]

    #
    # raw methods (handling always RAW tuples)
    #

    def _readRaw(self, maxage=0):
        return tuple(d.read(maxage) for d in self._motors)

    def _startRaw(self, targets):
        for d, p in zip(self._motors, targets):
            d.start(p)

    def _isAllowedRaw(self, targets):
        for d, p in zip(self._motors, targets):
            r = d.isAllowed(p)
            if not r[0]:
                return r
        return True, ''

    #
    # Nicos methods for 'cooked' values
    #

    def doRead(self, maxage=0):
        return self._mapReadValue(self._readRaw(maxage), opmode=self.opmode)

    def doStart(self, targets):
        self._startRaw(self._mapTargetValue(targets, opmode=self.opmode))

    def doIsAllowed(self, targets):
        rawpos = self._mapTargetValue(targets, opmode=self.opmode)
        r = self._isAllowedRaw(rawpos)
        if not r[0]:
            return r
        # further tests, which may fail....
        height = self._mapReadValue(rawpos, opmode=CENTER)[1]
        if height < 0:
            return False, 'Opening would be negative!'
        elif height > self._leftOpening.height:
            return False, 'Opening would be bigger than left/first/top shape!'
        elif height > self._rightOpening.height:
            return False, 'Opening would be bigger than right/second/bottom shape!'
        return True, ''

    #
    # other NICOS methods
    #

    def doShutdown(self):
        for name in [CENTER, 'height', 'top', 'bottom', 'first', 'second']:
            if name in self.__dict__:
                self.__dict__[name].shutdown()

    def doReset(self):
        multiReset(self._axes)
        multiWait(self._axes)

    def doReference(self):
        for m in self._motors:
            if isinstance(m, CanReference):
                self.log.info('referencing %s...' % m)
                m.reference()
            else:
                self.log.warning('%s cannot be referenced!' % m)

    def valueInfo(self):
        if self.opmode == RAW:
            return Value('%s.first' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.second' % self, unit=self.unit, fmtstr='%.2f')
        elif self.opmode == NORMAL:
            return Value('%s.top' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.bottom' % self, unit=self.unit, fmtstr='%.2f')
        elif self.opmode == CENTER:
            return Value('%s.center' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.height' % self, unit=self.unit, fmtstr='%.2f')
        else:
            raise ProgrammingError(self, 'invalid Opmode %r!' % self.opmode)

    #
    # Parameters
    #

    def doReadUnit(self):
        return self._adevs['first'].unit

    def doWriteOpmode(self, mode):
        # interpretation of values may have changed, invalidate old values....
        if self._cache:
            for d in [self.top, self.bottom, self.first, self.second, self.center, self.height]:
                d._cache.invalidate(d, 'value')
            self.read(0)

    def doWriteLeftshape(self, leftshape):
        self.shape = leftshape + 'x' + self.rightshape

    def doWriteRightshape(self, rightshape):
        self.shape = self.leftshape + 'x' + rightshape

    def doWriteShape(self, shape):
        self._leftOpening = Opening(*self.leftshapes[self.leftshape])
        self._rightOpening = Opening(*self.rightshapes[self.rightshape])

    def doWriteTilt(self, tilt):
        # re-adjust the slits
        self._setROParam('tilt', tilt)
        self.start(self.target)

    #
    # Conversions raw <-> cooked
    #

    def _mapTargetValue(self, positions, opmode=RAW):
        # maps cooked target values onto RAW values considering shape and _given_ opmode
        if opmode == RAW:
            return positions
        # translate center, height -> top, bottom and convert positions to a list
        if opmode == CENTER:
            positions = [positions[0] + 0.5 * positions[1], positions[0] - 0.5 * positions[1]]
        else:
            positions = list(positions)

        # consider shape related offsets
        positions[0] -= self._leftOpening.top
        positions[1] -= self._rightOpening.bottom

        # correct for beam tilt: assume point of rotation is between blades. if an offset would be needed, put it here as well.
        positions[0] -= 0.5 * self.distance * tan(radians(self.tilt)) #+ self.offset
        positions[1] += 0.5 * self.distance * tan(radians(self.tilt)) #+ self.offset
        return positions

    def _mapReadValue(self, positions, opmode=RAW):
        # maps RAW values onto cooked values considering shape and _given_ opmode
        if opmode == RAW:
            return positions

        # convert to a list
        positions = list(positions)

        # correct for beam tilt: assume point of rotation is between blades. if an offset would be needed, put it here as well.
        positions[0] += 0.5 * self.distance * tan(radians(self.tilt)) #- self.offset
        positions[1] -= 0.5 * self.distance * tan(radians(self.tilt)) #- self.offset

        # correct shape related offsets
        positions[0] += self._leftOpening.top
        positions[1] += self._rightOpening.bottom

        # translate top, bottom -> center, height, if requested
        if opmode == CENTER:
            return [0.5 * (positions[0] + positions[1]), positions[0] - positions[1]]
        return positions


class SlitAxis(AutoDevice, Moveable):
    """
    "Partial" devices for slit axes, useful for e.g. scanning
    over the device slit.center.
    """

    attached_devices = {
        'slit': (Slit, 'Slit whose axis is controlled'),
    }

    parameters = {
        'index': Param('which index of the super slit is used for this device', type=int, userparam=False),
        'opmode': Param('mode of the super slit to be used for this device', type=str, userparam=False),
    }

    valuetype = float

    hardware_access = False

    @lazy_property
    def slit(self):
        return self._adevs['slit']

    def doRead(self, maxage=0):
        """read main slit's raw values and convert to our opmode"""
        poslist = self.slit._readRaw(maxage)
        return self.slit._mapReadValue(poslist, opmode=self.opmode)[self.index]

    def _conv(self, target):
        """convert our target value to target values for the main slit axis"""
        _rawtargets = [d.target if d.target else d.read() for d in self.slit._motors]
        # convert to our cooked version
        pos = self.slit._mapReadValue(_rawtargets, opmode=self.opmode)
        # adjust our index
        pos[self.index] = target
        # translate to RAW
        raw = self.slit._mapTargetValue(pos, opmode=self.opmode)
        # return values translate to opmode of main slit device
        return self.slit._mapReadValue(raw, opmode=self.slit.opmode)

    def doStart(self, target):
        """convert our target value to target values for the main slit axis and start movement there"""
        self.slit.start(self._conv(target))

    def doIsAllowed(self, target):
        return self.slit.isAllowed(self._conv(target))
