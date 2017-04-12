#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
"""Classes to simulate the DSpec detector."""

import time

from nicos.core import Measurable, Param, Value, status, usermethod
from nicos.core.errors import NicosError


class DSPec(Measurable):

    parameters = {
        'prefix': Param('prefix for filesaving',
                        type=str, settable=False, mandatory=True),
        'truetime': Param('truetime',
                          type=float, settable=False, mandatory=False,
                          prefercache=True),
        'livetime': Param('livetime',
                          type=float, settable=False, mandatory=False,
                          prefercache=True),
        'state': Param('state',
                       type=int, settable=True, mandatory=False,
                       default=status.OK),
        'preselection': Param('presel', type=dict, settable=True,
                              mandatory=False),
    }
    # attached_devices = {
    #   'sink': Attach('Sink to pass additional data to', DataSink)
    # }

    @usermethod
    def getvals(self):
        spectrum = [1] * 16384
        return spectrum

    @usermethod
    def getEcal(self):
        return '0 0 0'

    @usermethod
    def getlive(self):
        return self.truetime

    @usermethod
    def getpoll(self):
        return self._dev.PollTime[0]

    @usermethod
    def gettrue(self):
        return self.livetime

    @usermethod
    def initdev(self):
        self._dev.Init()

    @usermethod
    def getstate(self):
        return self._dev.Status()

    @usermethod
    def savefile(self):
        self.doFinish()

    @usermethod
    def resetvals(self):
        self._started = None
        self._stop = None
        self._preset = {}

    def doUpdatePreselection(self, value):
        self._preset = value

    def doPreinit(self, mode):
        self._started = None
        self._stop = None
        self._preset = {}

    def doReadTruetime(self, maxage=0):
        if self._started is not None:
            return time.time() - self._started
        else:
            return 0
        # return self._dev.Truetime[0]

    def doReadLivetime(self, maxage=0):
        if self._started is not None:
            return time.time() - self._started
        else:
            return 0

    def doStatus(self, maxage=0):
        self.log.warning('status %s', self.state)
        return (self.state, 'TESTING' if self.state == status.OK else 'MOVING')

    def doPoll(self, n, maxage=0):
        return ((status.OK, ''), [0 for _i in range(16384)])

    def doReadIsmaster(self):
        pass

    def doRead(self, maxage=0):
        return [1 for _i in range(16384)]

    def doSetPreset(self, **preset):
        self._started = None
        self._stop = None
        self.preselection = preset

        if preset['cond'] == 'ClockTime':
            self._stop = preset['value']

    def doStart(self):
        self.state = status.BUSY
        self._started = time.time()
        self.log.warning('started')
        return
        # try:
        #     self._dev.Stop()
        #     self._dev.Clear()
        #     self._dev.Start()
        # except NicosError:
        #     try:
        #         self._dev.stop()
        #         self._dev.Init()
        #         self._dev.Clear()
        #         self._dev.Start()
        #     except NicosError:
        #         pass

    def doPause(self):
        self.doStop()
        return True

    def doResume(self):
        self.state = status.BUSY
        return True
        # try:
        #     self._dev.Stop()
        #     self._dev.Clear()
        #     self._dev.Start()
        # except NicosError:
        #     try:
        #         self._dev.stop()
        #         self._dev.Init()
        #         self._dev.Clear()
        #         self._dev.Start()
        #     except NicosError:
        #         pass
        # return True

    def doStop(self):
        self.state = status.OK
        return
        # try:
        #     self._dev.Stop()
        # except NicosError:
        #     self._dev.Init()
        #     self._dev.Stop()

    def doIsCompleted(self):
        if self._started is None:
            return True
        if self._stop is not None:
            if time.time() >= self._stop:
                return True
        if self.preselection['cond'] in ['TrueTime', 'LiveTime']:
            if time.time() - self._started >= self.preselection['value']:
                return True
        return False

    def valueInfo(self):
        return (Value('DSpecSpectra', type='counter'),)

    def doFinish(self):
        try:
            self.doStop()
        except NicosError:
            pass
        # reset values
        self._started = None
        self._stop = None
        self._preset = {}

        # temp
        return

        # try:
        #     spectra = [int(i) for i in self.doRead()]
        # except NicosError:
        #     self._preset['Comment'] += 'CACHED'
        #     spectra = self._cache.get(self, 'value')
        #     if spectra is None:
        #         self.log.warning('no spectra cached')
        #         return
        #     self.log.warning('using cached spectra')

        # timeb = []
        # tb_time = array('i', [int(self._started)])
        # tb_fill = array('h', [0, 0, 0])
        # timeb.extend([tb_time, tb_fill])

        # Type elap:
        # elap = []
        # el_time = array('i', [int(self.livetime * 100),
        #                       int(self.truetime * 100)])
        # el_fill_1 = array('i', [0])
        # el_fill_2 = array('d', [0])
        # elap.extend([el_time, el_fill_1, el_fill_2])

        # Type xcal:
        # xcal = []
        # ec_fill_1 = array('f', [0, 0, 0])
        # !! exchange sinkinfo with preset when scan command is used
        # unit = array('c', '{:<5}'.format(''))
        # ec_fill_2 = array('c', '\t\t\t')
        # xcal.extend([ec_fill_1, unit, ec_fill_2])

        # Type mcahead:
        # mcahead = []
        # mc_fill = array('h', [0, 1, 0])
        # mc_fill2 = array('i', [0])

        # !! exchange sinkinfo with preset when scan command is used
        # spectr_name = array('c', '{:<26}'.format(self._preset['Name'][:26]))
        # mc_fill3 = array('h', [0])
        # filler = array('h', [0 for i in range(19)])
        # nchans = array('h', [16384])

        # mcahead.extend([mc_fill, mc_fill2, spectr_name, mc_fill3])
        # mcahead.extend(timeb)
        # mcahead.extend(elap)
        # mcahead.extend(xcal)
        # mcahead.extend([filler, nchans])

        # spec_data = array('i', [0 for i in range(16384)])
        # spec_data = array('i', spectra)

        # dir_ = os.path.dirname(__file__)
        # filename = self.filename()
        # path = os.path.join(dir_, filename)
        # with open(filename, 'wb') as f:
        #     for data in mcahead:
        #         data.tofile(f)
        #     spec_data.tofile(f)
        # self.log.warning('ok written?')
        # reset values
        # self._started = None
        # self._stop = None
        # self._preset = {}

    def presetInfo(self):
        return ('cond', 'value', 'Name', 'Name', 'Comment', 'Pos', 'Beam',
                'Attenuator', 'ElCol', 'started', 'Subfolder', 'Detectors',
                'Filename')

    def filename(self):
        code = ''

        blades = {
            100.: ('out', 'out', 'out'),
            47.: ('out', 'in', 'out'),
            16.: ('in', 'out', 'out'),
            7.5: ('in', 'in', 'out'),
            5.9: ('out', 'out', 'in'),
            3.5: ('out', 'in', 'in'),
            2.7: ('in', 'out', 'in'),
            1.6: ('in', 'in', 'in')
        }[self._preset['Attenuator']]

        for i, item in enumerate(blades):
            if item == 'in':
                code += str(i + 1)

        code += 'E' if self._preset['ElCol'] == 'Ell' else 'C'
        if self._preset['Beam'] == 'closed':
            code += 'O'

        filename = 'logfiles/%s_%s_%s__%s' % (
            self.prefix, self._preset['Name'], self._preset['Comment'], code)
        return filename
