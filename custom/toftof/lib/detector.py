#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Attach, Moveable, NicosError, Param, intrange, listof
# from nicos.core.constants import INTERMEDIATE
from nicos.devices.generic.detector import Detector as GenericDetector

from nicos.toftof.chopper import BaseChopperController

from nicos.toftof import calculations as calc


class Detector(GenericDetector):

    attached_devices = {
        'rc': Attach('The Radial collimator', Moveable),
        'chopper': Attach('The chopper controller', BaseChopperController),
        'chdelay': Attach('Setting chopper delay', Moveable),
    }

    parameters = {
        'monitorchannel': Param('Channel number of the monitor counter',
                                settable=False, type=intrange(1, 1006),
                                default=956, category='general',
                                ),
        'timechannels': Param('Number of time channels per detector channel',
                              type=intrange(1, 4096), settable=True,
                              default=1024, volatile=True,
                              category='general',
                              ),
        'timeinterval': Param('Time interval between pulses',
                              type=float, settable=True, volatile=True,
                              default=0.0128571,
                              category='general',
                              ),
        'delay': Param('TOF frame delay',
                       type=int, settable=True, volatile=True,
                       default=162093,
                       category='general',
                       ),
        'channelwidth': Param('Channel width',
                              volatile=True, default=252,
                              category='general',
                              ),
        'numinputs': Param('Number of detector channels',
                           type=int, volatile=True,
                           default=1024,
                           category='general',
                           ),
        'rates': Param('The rates detected by the detector',
                       settable=False, type=listof(listof(float)),
                       userparam=True,
                       category='status',
                       ),
        'userdelay': Param('Additional chopper delay', type=float,
                           settable=True, default=0,
                           ),
        'detinfofile': Param('Path to the detector-info file',
                             type=str, settable=False,
                             default='custom/toftof/detinfo.dat',
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
        self._import_detinfo()

    def presetInfo(self):
        return set(['info']) | GenericDetector.presetInfo(self)

    def doInfo(self):
        ret = GenericDetector.doInfo(self)
        ret.append(('usercomment', self._user_comment, self._user_comment, '',
                    'general'))
        return ret

    def doSetPreset(self, **preset):
        self._user_comment = preset.pop('info', 'No comment')
        GenericDetector.doSetPreset(self, **preset)

    def doStart(self):
        try:
            if self._attached_rc.read(0) != 'on':
                self.log.warning('radial collimator is not moving!')
        except NicosError:
            self.log.warning('could not check radial collimator', exc=1)

        self.log.debug('reading chopper parameters')
        chwl, chspeed, chratio, _, chst = self._attached_chopper._getparams()

        _timeinterval = calc.calculateTimeInterval(chspeed, chratio)
        self.log.debug('setting time interval : %f' % _timeinterval)
        self.timeinterval = _timeinterval

        if chspeed > 150:
            # calculate chopper delay from chopper parameters
            self.log.debug('calculating chopper delay')
            ch5_90deg_offset = self._attached_chopper.ch5_90deg_offset
            _chdelay = calc.calculateChopperDelay(chwl, chspeed, chratio, chst,
                                                  ch5_90deg_offset)
            self.log.debug('setting chopper delay to : %d' % _chdelay)
            self._attached_chdelay.move(_chdelay)

            # select counter delay from chopper parameters
            self.log.debug('calculating counter delay')
            _ctrdelay = calc.calculateCounterDelay(chwl, chspeed, chratio,
                                                   self.userdelay,
                                                   ch5_90deg_offset)
            self.log.debug('setting counter delay to : %d' % _ctrdelay)
            self.delay = _ctrdelay
        else:
            _chdelay = 0
            self.log.debug('setting chopper delay to : %d' % _chdelay)
            self._attached_chdelay.move(_chdelay)

        self._last_time = 0
        self._last_counts = 0
        self._last_moncounts = 0
        self._starttime = currenttime()
        self._setROParam('rates', [[0., 0.], [0., 0.]])

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

    def doReadDelay(self):
        return self._attached_images[0].delay

    def doWriteDelay(self, value):
        self.log.debug('set detector delay: %d' % value)
        self._attached_images[0].delay = value

    def doReadTimechannels(self):
        return self._attached_images[0].timechannels

    def doWriteTimechannels(self, value):
        self._attached_images[0].timechannels = value

    def doReadTimeinterval(self):
        return self._attached_images[0].timeinterval

    def doWriteTimeinterval(self, value):
        self._attached_images[0].timeinterval = value

    def doReadChannelwidth(self):
        return self._attached_images[0].channelwidth

    def doReadNuminputs(self):
        return self._attached_images[0].numinputs

    def _import_detinfo(self):
        with open(self.detinfofile, 'U') as fp:
            self._detinfo = list(fp)
        for line in self._detinfo:
            if not line.startswith('#'):
                break
        dmap = {}  # maps "Total" (ElNr) to 2theta
        dinfo = [None]  # dinfo[EntryNr]
        for line in self._detinfo:
            if not line.startswith('#'):
                ls = line.split()
                if 'None' not in ls[13]:
                    dmap[int(ls[12])] = float(ls[5])
                dinfo.append(
                    list(map(int, ls[:5])) + [float(ls[5])] +
                    list(map(int, ls[6:8])) + [float(ls[8])] +
                    list(map(int, ls[9:13])) +
                    [' '.join(ls[13:-2]).strip("'")] +
                    list(map(int, ls[-2:]))
                )
        self._detinfolength = len(dinfo)
        self._detinfo_parsed = dinfo
        self.log.debug(self._detinfo_parsed)
        self._anglemap = tuple((i - 1) for i in sorted(dmap,
                                                       key=dmap.__getitem__))
