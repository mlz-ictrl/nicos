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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Detector switcher for KWS."""

from __future__ import absolute_import, division, print_function

from nicos.core import MASTER, SIMULATION, Attach, ConfigurationError, \
    DeviceMixinBase, HasLimits, Moveable, MoveError, Override, Param, dictof, \
    dictwith, multiReset, multiStop, oneof, status
from nicos.devices.abstract import MappedMoveable
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqSleep, \
    SequencerMixin
from nicos.devices.tango import Motor as TangoMotor
from nicos.pycompat import iteritems
from nicos.utils import num_sort


class oneof_detector(oneof):
    def __call__(self, val=None):
        try:
            return oneof.__call__(self, val)
        except ValueError:
            raise ValueError('preset %r does not exist for the current '
                             'selector setting' % val)


class DetectorPosSwitcherMixin(DeviceMixinBase):

    parameters = {
        'offsets':  Param('Offsets to correct TOF chopper-detector length '
                          'for the errors in the det_z axis value',
                          type=dictof(float, float),
                          mandatory=True),
        'mapkey':   Param('Last selector position for mapping',
                          type=str, settable=True, internal=True),
    }


class DetectorPosSwitcher(DetectorPosSwitcherMixin, SequencerMixin,
                          MappedMoveable):

    hardware_access = False

    attached_devices = {
        'det_z':      Attach('Large detector Z axis', Moveable),
        'bs_x':       Attach('Large detector beamstop X axis', Moveable),
        'bs_y':       Attach('Large detector beamstop Y axis', Moveable),
    }

    parameters = {
        'presets':    Param('Presets that determine the mappings',
                            type=dictof(str, dictof(str, dictwith(
                                x=float, y=float, z=float))),
                            mandatory=True),
        'offsets':    Param('Offsets to correct TOF chopper-detector length '
                            'for the errors in the det_z axis value',
                            type=dictof(float, float),
                            mandatory=True),
        'mapkey':     Param('Last selector position for mapping',
                            type=str, settable=True, internal=True),
        'beamstopsettlepos': Param('Settling position for beamstop y axis',
                                   settable=True, default=400),
    }

    parameter_overrides = {
        'mapping':  Override(mandatory=False, settable=True, internal=True),
        'fallback':  Override(userparam=False, type=str, mandatory=True),
    }

    def doInit(self, mode):
        # check that an offset is defined for each z distance
        for _selpos, selpresets in iteritems(self.presets):
            for _pname, preset in iteritems(selpresets):
                if preset['z'] not in self.offsets:
                    raise ConfigurationError(
                        self, 'no detector offset found in configuration '
                        'for detector distance of %.2f m' % preset['z'])
        MappedMoveable.doInit(self, mode)
        # apply mapping of last selector pos in case it changed
        if mode == MASTER:
            self._updateMapping(self.mapkey)

    def _updateMapping(self, selpos):
        self.log.debug('updating the detector mapping for selector '
                       'setting %s' % selpos)
        try:
            pos = self.presets.get(selpos, {})
            new_mapping = {k: [v['x'], v['y'], v['z']] for (k, v) in pos.items()}
            self.mapping = new_mapping
            self.mapkey = selpos
            self.valuetype = oneof_detector(*sorted(new_mapping, key=num_sort))
            if self._cache:
                self._cache.invalidate(self, 'value')
                self._cache.invalidate(self, 'status')
        except Exception:
            self.log.warning('could not update detector mapping', exc=1)

    def _startRaw(self, pos):
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])

        seq = []
        seq.append(SeqDev(self._attached_bs_y, pos[1], stoppable=True))
        seq.append(SeqDev(self._attached_bs_x, pos[0], stoppable=True))
        seq.append(SeqDev(self._attached_det_z, pos[2], stoppable=True))

        # if z has to move, reposition beamstop y afterwards by going to
        # some other value (damping vibrations) and back
        if abs(self._attached_det_z.read(0) - pos[2]) > self._attached_det_z.precision:
            seq.append(SeqDev(self._attached_bs_y, self.beamstopsettlepos, stoppable=True))
            seq.append(SeqSleep(30))
            seq.append(SeqDev(self._attached_bs_y, pos[1], stoppable=True))

        self._startSequence(seq)

    def _readRaw(self, maxage=0):
        return {n: (d.read(maxage), getattr(d, 'precision', 0))
                for (n, d) in self._adevs.items()}

    def _mapReadValue(self, pos):
        def eq(posname, val):
            return abs(pos[posname][0] - val) <= pos[posname][1]

        for name, values in iteritems(self.mapping):
            if eq('det_z', values[2]) and eq('bs_x', values[0]) and \
               eq('bs_y', values[1]):
                return name
        return self.fallback

    def doStatus(self, maxage=0):
        seq_status = SequencerMixin.doStatus(self, maxage)
        if seq_status[0] not in (status.OK, status.WARN):
            return seq_status
        return MappedMoveable.doStatus(self, maxage)

    def doReset(self):
        multiReset(self._adevs)

    def doStop(self):
        multiStop(self._adevs)


class DetectorZAxis(HasLimits, BaseSequencer):
    """Special device for the detector Z axis.

    Switches HV off before moving.
    """

    hardware_access = False

    parameters = {
        'precision': Param('Precision', volatile=True),
    }

    attached_devices = {
        'motor': Attach('The raw motor', Moveable),
        'hv':    Attach('The HV switch', Moveable),
    }

    def doReadPrecision(self):
        return self._attached_motor.precision

    def doReadAbslimits(self):
        return self._attached_motor.abslimits

    def _generateSequence(self, target):
        seq = []
        if self._attached_hv.read(0) != 'off':
            seq.append(SeqDev(self._attached_hv, 'off'))
        seq.append(SeqDev(self._attached_motor, target, stoppable=True))
        return seq

    def doRead(self, maxage=None):
        return self._attached_motor.read(maxage)

    def doStatus(self, maxage=None):
        code, text = BaseSequencer.doStatus(self, maxage)
        if code == status.OK:
            text = self._attached_motor.status(maxage)[1]
        return code, text

    def doStart(self, target):
        if abs(self.read(0) - target) <= self.precision:
            return
        BaseSequencer.doStart(self, target)


class LockedMotor(TangoMotor):
    """A motor that is sometimes switched off by the SPS due to interlocks."""

    def doStatus(self, maxage=None):
        code, text = TangoMotor.doStatus(self, maxage)
        if code == status.DISABLED:
            # an error here most likely just means that the interlock is on
            code = status.OK
        return code, text

    def doStart(self, target):
        if abs(self.read(0) - target) <= self.precision:
            return
        return TangoMotor.doStart(self, target)

    def doStop(self):
        code = TangoMotor.doStatus(self, 0)[0]
        if code != status.DISABLED:
            TangoMotor.doStop(self)
