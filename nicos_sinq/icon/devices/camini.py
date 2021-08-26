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

import datetime
from time import time as currenttime

from nicos import session
from nicos.core import Attach, Moveable, Param, Readable, Value, pvname, status
from nicos.devices.generic import Detector
from nicos.devices.generic.sequence import SeqDev, SeqMethod, SeqSleep, \
    SequenceItem, SequencerMixin

from nicos_ess.devices.epics.base import EpicsDeviceEss


class WaitPV(SequenceItem):

    def __init__(self, camini, pv, value, timeout=0):
        self._pv = pv
        self._value = value
        self._stopped = False
        self._camini = camini
        self._timeout = timeout
        SequenceItem.__init__(self)

    def run(self):
        self._endtime = currenttime() + self._timeout

    def stop(self):
        self._stopped = True

    def isCompleted(self):
        if self._camini._timedout:
            return True
        if self._timeout != 0 and currenttime() > self._endtime:
            self._camini._timedout = True
            return True
        return bool(self._camini.readPV(self._pv) ==
                    self._value or self._stopped)


class WaitThreshold(SequenceItem):

    def __init__(self, camini, dev, threshold):
        self._dev = dev
        self._threshold = threshold
        self._stopped = False
        self._camini = camini
        SequenceItem.__init__(self)

    def stop(self):
        self._stopped = True

    def isCompleted(self):
        if self._camini._timedout:
            return True
        return bool(self._stopped or self._dev.read() >= self._threshold)


class WaitNotPV(SequenceItem):

    def __init__(self, camini, pv, value, timeout=0):
        self._pv = pv
        self._value = value
        self._stopped = False
        self._camini = camini
        self._timeout = timeout
        SequenceItem.__init__(self)

    def run(self):
        self._endtime = currenttime() + self._timeout

    def stop(self):
        self._stopped = True

    def isCompleted(self):
        if self._camini._timedout:
            return True
        if self._timeout != 0 and currenttime() > self._endtime:
            self._camini._timedout = True
            return True
        return bool(self._camini.readPV(self._pv) !=
                    self._value or self._stopped)


class PutPV(SequenceItem):

    def __init__(self, camini, pv, value):
        self._pv = pv
        self._value = value
        self._camini = camini
        SequenceItem.__init__(self)

    def run(self):
        if not self._camini._timedout:
            self._camini.writePV(self._pv, self._value)

    def isCompleted(self):
        return True


class Message(SequenceItem):
    def __init__(self, camini, message):
        self._message = message
        self._camini = camini
        SequenceItem.__init__(self)

    def run(self):
        if not self._camini._timedout:
            session.log.info(self._message)

    def isCompleted(self):
        return True


class CaminiDetector(EpicsDeviceEss, SequencerMixin,
                     Detector):
    """
    NIAG runs most of their CCD cameras through Camini.
    The camera is setup outside off NICOS and then
    operated through I/O's ever afterwards. This is
    done via a LabView program named Camini.

    No real data transfer happens, the presets are managed
    outside of NICOS too. But NICOS sends meta data to Camini
    which is written into image files by Camini
    """
    parameters = {
        'trigpv': Param('PV to send a trigger signal', type=pvname,
                        mandatory=True, userparam=False),
        'validpv': Param('PV to inform whether the metadata is valid',
                         type=pvname, mandatory=True, userparam=False),
        'metapv': Param('PV containing the metadata', type=pvname,
                        mandatory=True, userparam=False),
        'shutpv': Param('PV to monitor the camera shutter', type=pvname,
                        mandatory=True, userparam=False),
        'armpv': Param('PV to monitor whether the camera is ready',
                       type=pvname, mandatory=True, userparam=False),
        'filepv': Param('PV for the image filename', type=pvname,
                        mandatory=True, userparam=False),
        'arm_timeout': Param('Timeout when waiting for the camera to be ready',
                             type=float, mandatory=True,
                             userparam=True, settable=True),
        'shutter_timeout': Param('Timeout for the shutter to open',
                                 type=float,
                                 mandatory=True,
                                 userparam=True, settable=True),
        'exposure_timeout': Param('Image exposure timeout > exposure_time',
                                  type=float, mandatory=True,
                                  userparam=True, settable=True),
    }
    attached_devices = {
        'shutter': Attach('Beam Shutter', Moveable),
        'auto': Attach('Automatic Shutter Switch', Moveable),
        'beam_current': Attach('Beam current', Readable),
        'rate_threshold': Attach('Threshold for starting exposure', Readable)
    }

    _presetkeys = []

    _timestamp = None

    _timedout = False

    def presetInfo(self):
        return {'t', 'timer', 'm', 'monitor'}

    def readPV(self, pvname):
        return self._get_pv(pvname)

    def writePV(self, pvname, value):
        return self._put_pv(pvname, value, True)

    def doPreinit(self, mode):
        EpicsDeviceEss.doPreinit(self, mode)

    def _get_pv_parameters(self):
        pvs = {'trigpv', 'validpv', 'metapv', 'shutpv', 'armpv', 'filepv'}
        return pvs

    def doSetPreset(self, **preset):
        pass

    def doStart(self):
        self._timedout = False
        self._timestamp = None
        self._startSequence(self._generateSequence())

    def doStatus(self, maxage=0):
        # It was calling the inappropriate doStatus() from EpicsDeviceEss
        if self._timedout:
            return status.ERROR, 'Timeout'
        if self._seq_is_running():
            return status.BUSY, 'Executing Sequence'
        stat = SequencerMixin.doStatus(self, maxage)
        if stat[0] not in self.busystates and not self._timestamp:
            now = datetime.datetime.now()
            self._timestamp = now.strftime('%Y-%m-%dT%H:%M:%S')
        return stat

    def doReset(self):
        self._timedout = False
        SequencerMixin.doReset(self)

    def _generateSequence(self):
        seq = []

        shutter_mode = self._attached_auto.read(0)

        if shutter_mode == 'auto':
            seq.append(SeqDev(self._attached_shutter, 'open'))

        # Wait for arm to become 0
        seq.append(WaitPV(self, 'armpv', 0, timeout=self.arm_timeout))

        # set valid 0
        seq.append(PutPV(self, 'validpv', 0))

        # wait for beam
        seq.append(Message(self, 'Waiting for beam...'))
        s = WaitThreshold(self, self._attached_beam_current,
                          self._attached_rate_threshold.read())
        seq.append(s)
        seq.append(Message(self, 'Beam is on, exposing...'))

        # Start the detector
        seq.append(PutPV(self, 'trigpv', 1))

        # wait for the detector to actually start
        s = WaitNotPV(self, 'shutpv', 1, timeout=self.shutter_timeout)
        seq.append(s)

        # Reset the start signal
        seq.append(PutPV(self, 'trigpv', 0))

        # Wait for counting to finish
        s = WaitPV(self, 'shutpv', 1, timeout=self.exposure_timeout)
        seq.append(s)

        # Write the metadata
        seq.append(SeqMethod(self, '_writeMetaData'))

        # Camini is tired, needs a little sleep
        seq.append(SeqSleep(.1))

        # set valid 1
        seq.append(PutPV(self, 'validpv', 1))

        if shutter_mode == 'auto':
            seq.append(SeqDev(self._attached_shutter, 'closed'))

        return seq

    def doRead(self, maxage=0):
        return [self._pvs['filepv'].get(timeout=self.epicstimeout,
                as_string=True, count=256), self._timestamp]

    def _writeMetaData(self):
        meta = self._getMetadata()
        self._put_pv('metapv', meta, wait=True)

    def _getMetadata(self):

        retval = ''

        devlist = [devname
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname], Readable)]

        self.log.debug('devlist : %s', devlist)

        setups = session.getSetupInfo()
        setups_log = {}

        self.log.debug('setup list: %s', list(setups.keys()))

        for s in setups:
            self.log.debug('setup "%s":', s)
            s_devlist = (setups[s])['devices']
            self.log.debug(s_devlist)
            s_devlist = [d for d in s_devlist if d in devlist]
            self.log.debug(s_devlist)
            for d in s_devlist:
                if s not in setups_log.keys():
                    setups_log[s] = []
                setups_log[s].append(session.devices[d])

        self.log.debug(str(setups_log))

        for s in setups_log:  # pylint: disable=consider-using-dict-items
            for dev in setups_log[s]:

                # The FITS standard defines max 8 characters for a header key.
                # To make longer keys possible, we use the HIERARCH keyword
                # here (67 chars max).
                # To get a consistent looking header, add it to every key
                key = 'HIERARCH ' + s + '/' + dev.name

                # use only ascii characters and escapes if necessary.
                try:
                    val = dev.read(0)
                    value = dev.format(val, unit=True).encode('unicode-escape')
                except Exception as e:
                    session.log.warning('Failed to read dev.name, %s,'
                                        ' with %s', dev.name, e)
                    session.log.warning('Offending value: %s', val)
                    value = 'Unknown'

                # Determine maximum possible value length (key dependend).
                maxValLen = 63 - len(key)

                # Split the dataset into several header entries if necessary
                # (due to the limited length)
                splittedHeaderItems = [value[i:i + maxValLen]
                                       for i in
                                       range(0, len(value), maxValLen)]

                for item in splittedHeaderItems:
                    retval = retval + (key + ' = ' + str(item)).ljust(80)[:80]

        return retval

    def valueInfo(self):
        return (Value('Image File', unit=self.unit, fmtstr='%s'),
                Value('Timestamp', unit='s', fmtstr='%s'))

    def arrayInfo(self):
        return ()
