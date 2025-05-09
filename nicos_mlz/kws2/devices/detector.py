# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

"""Detector switcher for KWS 2 with large/small detector selection."""

from nicos import session
from nicos.core import MASTER, SIMULATION, Attach, ConfigurationError, \
    HasOffset, Moveable, MoveError, Override, Param, dictof, dictwith, \
    multiReset, multiStop, status
from nicos.devices.abstract import MappedMoveable
from nicos.devices.entangle import AnalogInput
from nicos.devices.generic.sequence import SeqCall, SeqDev, SequencerMixin
from nicos.utils import num_sort

from nicos_mlz.kws1.devices.detector import DetectorPosSwitcherMixin
from nicos_mlz.kws1.devices.params import oneof_detector


class DetectorPosSwitcher(DetectorPosSwitcherMixin, SequencerMixin,
                          MappedMoveable):
    """Switcher for the detector and detector position.

    This controls the large/small detector and the X/Y/Z components of the
    detector position.  Presets depend on the target wavelength given by the
    selector.
    """

    hardware_access = False

    attached_devices = {
        'det_z':      Attach('Large detector Z-axis', Moveable),
        'bs_x':       Attach('Large detector beamstop X-axis', Moveable),
        'bs_y':       Attach('Large detector beamstop Y-axis', Moveable),
        'psd_x':      Attach('Small detector X-axis', Moveable),
        'psd_y':      Attach('Small detector Y-axis', Moveable),
        'attenuator': Attach('Beam attenuator', Moveable),
    }

    parameters = {
        'presets':    Param('Presets that determine the mappings',
                            type=dictof(str, dictof(str, dictwith(
                                x=float, y=float, z=float, attenuator=str,
                                small=bool))),
                            mandatory=True),
        'offsets':    Param('Offsets to correct TOF chopper-detector length '
                            'for the errors in the det_z axis value',
                            type=dictof(float, float),
                            mandatory=True),
        'mapkey':     Param('Last selector position for mapping',
                            type=str, settable=True, internal=True),
        'psdtoppos':  Param('"Top" end position of small detector',
                            unit='mm', mandatory=True),
        'detbackpos': Param('"Back" end position of large detector',
                            unit='m', mandatory=True),
    }

    parameter_overrides = {
        'mapping':  Override(mandatory=False, settable=True, internal=True),
        'fallback':  Override(userparam=False, type=str, mandatory=True),
    }

    def doInit(self, mode):
        # check that an offset is defined for each z distance
        for _selpos, selpresets in self.presets.items():
            for _pname, preset in selpresets.items():
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
                       'setting %s', selpos)
        try:
            pos = self.presets.get(selpos, {})
            new_mapping = {k: [v['x'], v['y'], v['z'], v['small'], v['attenuator']]
                           for (k, v) in pos.items()}
            self.mapping = new_mapping
            self.mapkey = selpos
            self.valuetype = oneof_detector(*sorted(new_mapping, key=num_sort))
            if self._cache:
                self._cache.invalidate(self, 'value')
                self._cache.invalidate(self, 'status')
        except Exception:
            self.log.warning('could not update detector mapping', exc=1)

    def _startRaw(self, target):
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])

        # switch det_img alias synchronously, the chopper sets its mode param!
        det_img_alias = session.getDevice('det_img')
        if target[3]:
            det_img_alias.alias = 'det_img_jum'
        else:
            det_img_alias.alias = 'det_img_ge'

        seq = []
        seq.append(SeqDev(self._attached_attenuator, target[4]))
        if target[3]:
            seq.append(SeqDev(self._attached_det_z, self.detbackpos,
                              stoppable=True))
            seq.append(SeqDev(self._attached_psd_y, target[1], stoppable=True))
            seq.append(SeqDev(self._attached_psd_x, target[0], stoppable=True))
        else:
            seq.append(SeqDev(self._attached_psd_x, 0, stoppable=True))
            seq.append(SeqDev(self._attached_psd_y, self.psdtoppos,
                              stoppable=True))
            seq.append(SeqDev(self._attached_bs_y, target[1], stoppable=True))
            seq.append(SeqDev(self._attached_bs_x, target[0], stoppable=True))
            seq.append(SeqDev(self._attached_det_z, target[2], stoppable=True))
            # maybe reposition beamstop Y-axis to counter jitter.
            seq.append(SeqCall(self._check_bsy, target[1]))

        self._startSequence(seq)

    def _check_bsy(self, target):
        bsy = self._attached_bs_y
        for _i in range(5):
            if self._seq_stopflag:
                return
            readings = []
            for _j in range(20):
                readings.append(bsy.read(0))
                session.delay(0.2)
            if all(abs(v - target) <= bsy.precision for v in readings):
                return  # it's ok
            self.log.warning('beamstop not ok, waiting 60 seconds for repositioning')
            session.delay(60)
            if self._seq_stopflag:
                return
            bsy.maw(target)
        self.log.error('beamstop not ok after 5 reposition tries')

    def _readRaw(self, maxage=0):
        return {n: (d.read(maxage), getattr(d, 'precision', 0))
                for (n, d) in self._adevs.items()}

    def _mapReadValue(self, value):
        def eq(posname, val):
            return abs(value[posname][0] - val) <= value[posname][1]

        for name, values in self.mapping.items():
            if value['attenuator'][0] != values[4]:
                continue
            if values[3]:
                if not eq('det_z', self.detbackpos):
                    continue
                if eq('psd_x', values[0]) and eq('psd_y', values[1]):
                    return name
            else:
                if not eq('psd_y', self.psdtoppos):
                    continue
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


class DetectorBsEncoder(HasOffset, AnalogInput):
    def doRead(self, maxage=0):
        return self._dev.value - self.offset
