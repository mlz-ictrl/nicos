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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF detector."""

from time import time as currenttime

import numpy

from nicos import session
from nicos.core import Attach, Moveable, NicosError, Override, Param, \
    intrange, listof, status
from nicos.core.constants import INTERMEDIATE, SIMULATION
from nicos.devices.generic.detector import Detector as GenericDetector
from nicos.devices.tango import ImageChannel, TOFChannel

from nicos_mlz.toftof.devices import calculations as calc
from nicos_mlz.toftof.devices.chopper import BaseChopperController


class TOFTOFChannel(ImageChannel, TOFChannel):
    # This class is, unfortunately, not agnostic to hw specifics
    parameters = {
        'frametime': Param('Total width of all time bins in s',
                           type=float, mandatory=False, volatile=True,
                           default=0.1, category='general', settable=True,),
    }
    parameter_overrides = {
        'timechannels': Override(default=1024),
        'timeinterval': Override(type=float, unit='s', volatile=True),
        'delay':        Override(type=float, unit='s', volatile=True),
    }

    def doReadFrametime(self):
        return self.doReadTimeinterval() * self.doReadTimechannels()

    def doWriteFrametime(self, value):
        self.doStop()

        # as the HW can only realize selected values for timeinterval, probe
        # until success
        wanted_timeinterval = int(
            (value / self.doReadTimechannels()) / calc.ttr) * calc.ttr
        self.doWriteTimeinterval(wanted_timeinterval)
        # note: if a doReadTimeinterval differs in value from a previous
        #       doWriteTimeinterval,
        #       HW does actually uses the returned value, not the wanted.
        #       (in this case: returned < set) so, increase the wanted value
        #       until the used one is big enough
        actual_timeinterval = self.doReadTimeinterval()
        while (actual_timeinterval * self.timechannels < value):
            wanted_timeinterval += calc.ttr
            self.doWriteTimeinterval(wanted_timeinterval)
            actual_timeinterval = self.doReadTimeinterval()

    def doStop(self):
        if self.doStatus()[0] == status.BUSY:
            self._dev.Stop()

    def doWriteTimechannels(self, value):
        self.doStop()
        self._dev.timeChannels = value

    def doReadTimeinterval(self):
        # our timeinterval is in s, entangle is in ns, in multiple of calc.ttr
        return self._dev.timeInterval * 1e-9

    def doWriteTimeinterval(self, value):
        # our timeinterval is in s, entangle is in ns, in multiple of calc.ttr
        self.doStop()
        self._dev.timeInterval = int(value / calc.ttr) * int(calc.ttr * 1e9)

    def doReadDelay(self):
        # our delay is in s, entangle is in ns, in multiple of calc.ttr
        return self._dev.delay * 1e-9

    def doWriteDelay(self, value):
        # our delay is in s, entangle is in ns, in multiple of calc.ttr
        self.doStop()
        self.log.debug('set counter delay: %f s', value)
        value = int(value / calc.ttr) * int(calc.ttr * 1e9)
        self.log.debug('set counter delay: %d ns', value)
        self._dev.delay = value


class Detector(GenericDetector):

    attached_devices = {
        'rc': Attach('The Radial collimator', Moveable),
        'chopper': Attach('The chopper controller', BaseChopperController),
        'chdelay': Attach('Setting chopper delay', Moveable),
    }

    parameters = {
        'monitorchannel': Param('Channel number of the monitor counter',
                                settable=False, type=intrange(1, 1024),
                                default=956, category='general',
                                ),
        'timechannels': Param('Number of time channels per detector channel',
                              type=intrange(1, 4096), settable=True,
                              default=1024, volatile=True,
                              category='general',
                              ),
        'frametime': Param('Time interval between pulses',
                           type=float, settable=True,
                           default=0.0128571, volatile=True,
                           category='general', unit='s',
                           ),
        'delay': Param('TOF frame delay',
                       type=float, settable=True, volatile=True,
                       default=162093*5e-8, fmtstr='%g',
                       category='general', unit='s',
                       ),
        # note: check if channelwidth is REALLY needed as it duplicates
        #       timeinterval
        'channelwidth': Param('Duration of single time slot in units of 50ns',
                              volatile=True, mandatory=False, settable=False,
                              category='general', unit='ticks',
                              ),
        'timeinterval': Param('Duration of a single time slot',
                              volatile=True, default=252*5e-8,
                              category='general', unit='s',
                              ),
        'numinputs': Param('Number of detector channels',
                           type=int, default=1006, category='general',
                           ),
        'rates': Param('The rates detected by the detector',
                       settable=False, type=listof(listof(float)),
                       userparam=True,
                       category='status',
                       ),
        'userdelay': Param('Additional chopper delay', type=float,
                           settable=True, default=0, unit='s',
                           ),
        'detinfofile': Param('Path to the detector-info file',
                             type=str, settable=False,
                             default='nicos_mlz/toftof/detinfo.dat',
                             # mandatory=True,
                             ),
    }

    _last_time = 0
    _last_counts = 0
    _last_moncounts = 0
    _user_comment = 'No comment'

    def doPreinit(self, mode):
        GenericDetector.doPreinit(self, mode)

    def doInit(self, mode):
        GenericDetector.doInit(self, mode)
        if mode == SIMULATION:
            return
        self._import_detinfo()

    def doInfo(self):
        for p in ('timechannels', 'timeinterval', 'delay', 'channelwidth'):
            self._pollParam(p)
        ret = GenericDetector.doInfo(self)
        return ret

    def doSetPreset(self, **preset):
        GenericDetector.doSetPreset(self, **preset)
        if not self._user_comment:  # Comment must be fulfilled for data sink
            self._user_comment = 'No comment'

    def _update(self):
        self.log.debug('reading chopper parameters')
        chwl, chspeed, chratio, _, chst = self._attached_chopper._getparams()

        self.frametime = calc.calculateFrameTime(chspeed, chratio)
        self.log.debug('setting frame time interval: %f', self.frametime)

        if chspeed > 150:
            # calculate chopper delay from chopper parameters
            self.log.debug('calculating chopper delay')
            ch5_90deg_offset = self._attached_chopper.ch5_90deg_offset
            _chdelay = calc.calculateChopperDelay(chwl, chspeed, chratio, chst,
                                                  ch5_90deg_offset)

            # select counter delay from chopper parameters
            self.log.debug('calculating counter delay')
            _ctrdelay = calc.calculateCounterDelay(chwl, chspeed, chratio,
                                                   self.userdelay,
                                                   ch5_90deg_offset)
        else:
            _chdelay = 0
            _ctrdelay = 0
        self.log.debug('setting chopper delay to: %g', _chdelay)
        self._attached_chdelay.move(_chdelay)
        self.doWriteDelay(_ctrdelay)

    def doStart(self):
        try:
            if self._attached_rc.read(0) != 'on':
                self.log.warning('radial collimator is not moving!')
        except NicosError:
            self.log.warning('could not check radial collimator', exc=1)

        self._update()

        self._last_time = 0
        self._last_counts = 0
        self._last_moncounts = 0
        self._starttime = currenttime()
        self._setROParam('rates', [[0., 0.], [0., 0.]])

        session.action('run# %06d' % session.experiment.lastpoint)

        GenericDetector.doStart(self)

    def doResume(self):
        GenericDetector.doResume(self)
        # Reset the time for instantaneous rates calculation
        self._last_time = 0

    def doRead(self, maxage=0):
        ret = GenericDetector.doRead(self, maxage)
        meastime = float(ret[0])
        monitor = int(ret[1])
        counts = int(ret[2])
        if meastime >= self._attached_timers[0].preselection:
            difftim = meastime = 0
        else:
            difftim = meastime - self._last_time

        monrate = monitor / meastime if meastime else 0
        if monitor == 0 and self._last_moncounts > 0:
            self._last_moncounts = 0
        monrate_inst = (monitor - self._last_moncounts) / difftim if difftim \
            else 0

        detrate = counts / meastime if meastime else 0
        if counts == 0 and self._last_counts > 0:
            self._last_counts = 0
        detrate_inst = (counts - self._last_counts) / difftim if difftim \
            else 0
        self._setROParam('rates', [[detrate, monrate],
                                   [detrate_inst, monrate_inst]])
        self._last_time = meastime
        self._last_counts = counts
        self._last_moncounts = monitor
        return ret

    def duringMeasureHook(self, elapsed):
        ret = GenericDetector.duringMeasureHook(self, elapsed)
        if ret == INTERMEDIATE:
            [detrate, monrate], [detrate_inst, monrate_inst] = self.rates
            self.log.info('Monitor: rate: %8.3f counts/s, instantaneous '
                          'rate: %8.3f counts/s', monrate, monrate_inst)
            self.log.info('Signal: rate: %8.3f counts/s, instantaneous '
                          'rate: %8.3f counts/s', detrate, detrate_inst)
        return ret

    def doReadDelay(self):
        self._update()
        return self._attached_images[0].delay

    def doWriteDelay(self, value):
        self.log.debug('setting counter delay to: %g', value)
        self._attached_images[0].delay = value

    def doReadTimechannels(self):
        return self._attached_images[0].timechannels

    def doWriteTimechannels(self, value):
        self._attached_images[0].timechannels = value

    def doReadFrametime(self):
        return self._attached_images[0].frametime

    def doWriteFrametime(self, value):
        self._attached_images[0].frametime = value
        return self.doReadFrametime()  # may differ from requested value

    def doReadTimeinterval(self):
        self._update()
        return self._attached_images[0].timeinterval

    def doReadChannelwidth(self):
        return int(self.timeinterval / calc.ttr)

    def _import_detinfo(self):
        with open(self.detinfofile, newline=None, encoding='utf-8') as fp:
            self._detinfo = list(fp)

        amap = {}  # maps "Total" (ElNr) to 2theta without 'None' detectors
        dmap = []  # maps "Total" (ElNr) to 2theta over all detectors
        dinfo = []  # dinfo[EntryNr]
        theta = []
        for line in self._detinfo:
            if not line.startswith('#'):
                ls = line.split()
                if 'None' not in ls[13]:
                    amap[int(ls[12])] = float(ls[5])
                theta.append(float(ls[5]))
                dmap.append(int(ls[12]))
                dinfo.append(
                    list(map(int, ls[:5])) + [float(ls[5])] +
                    list(map(int, ls[6:8])) + [float(ls[8])] +
                    list(map(int, ls[9:13])) +
                    [' '.join(ls[13:-2]).strip("'")] +
                    list(map(int, ls[-2:]))
                )

        inds = numpy.array(theta).argsort()
        self._detectormap = numpy.array(dmap)[inds].tolist()
        self._detinfolength = len(dinfo)
        self._detinfo_parsed = dinfo
        self.log.debug('%s', self._detinfo_parsed)
        self._anglemap = tuple((i - 1) for i in sorted(amap,
                                                       key=amap.__getitem__))
