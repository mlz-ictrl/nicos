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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF measurement."""

__version__ = "$Revision$"

import os
from time import strftime, time as currenttime

import numpy as np

from nicos import session
from nicos.core import Measurable, Moveable, Param, Value, Override, \
     NicosError, intrange
from nicos.abstract import ImageStorage

from nicos.toftof.tofcounter import TofCounter
from nicos.toftof import chopper

# TofChopper parameters: wavelength, speed, ratio, crc, slittype


class TofTofMeasurement(Measurable, ImageStorage):

    attached_devices = {
        'counter': (TofCounter, 'The TOF counter'),
        'chopper': (TofChopper, 'The chopper controller'),
        'chdelay': (Moveable, 'Setting chopper delay'),
    }

    parameters = {
        'ch5_90deg_offset': Param('Whether chopper 5 is mounted the right way '
                                  '(= 0) or with 90deg offset (= 1)',
                                  type=intrange(0, 2), default=0, mandatory=True),
        'delay_address':    Param('Chopper delay address ???',
                                  settable=True, type=int, default=241),
        'delay':            Param('Additional delay ???', type=float,
                                  settable=True, default=0),
        # XXX do we need those in here and on TofCounter?
        'timechannels':     Param('Number of time channels', default=1024,
                                  type=intrange(1, 1025), settable=True),
        'timeinterval':   Param('Time interval ???', type=float, settable=True),
    }

    parameter_overrides = {
        'nametemplate': Override(default='%06d_0000.raw'),
        'subdir': Override(default='', mandatory=False),
    }

    def valueInfo(self):
        return Value('filename', type='info')

    def doInit(self):
        self._detinfo = []   # XXX
        self._detinfolength = 0

    def doSetPreset(self, **preset):
        self._adevs['counter'].setPreset(**preset)

    def doReadTimechannels(self):
        return self._adevs['counter'].timechannels

    def doWriteTimechannels(self, value):
        self._adevs['counter'].timechannels = value

    def doStart(self, **preset):
        ctr = self._adevs['counter']
        self.doSetPreset(**preset)

        chwl, chspeed, chratio, chcrc, chst = self._adevs['chopper'].read()
        if chratio == 1:
            chratio2 = 1.0
        else:
            chratio2 = (chratio-1.0)/chratio

        if self.timeinterval == 0:
            if chspeed == 0:
                interval = 0.052
            else:
                interval = 30.0 / chspeed * chratio
        else:
            interval = self.timeinterval
        ctr.timeinterval = interval

        chdelay = 0.0
        if chspeed > 150:
            if self.ch5_90deg_offset:
                # chopper 5 90 deg rotated
                chdelay = -15.0e6/chspeed/chratio2
            if chst == 1:
                chdelay = 15.0e6/chspeed
            chdelay += (252.7784 * chwl * 8.028 - 15.0e6*(1.0/chspeed/chratio2-1.0/chspeed))
            chdelay = chdelay % (30.0e6/chspeed)
            chdelay -= 100.0
            if chdelay < 0:
                chdelay += 30.0e6/chspeed
            chdelay = int(round(chdelay))
        self._adevs['chdelay'].start(chdelay)
        if chspeed > 150:
            if self.ch5_90deg_offset:
                TOFoffset = 30.0/chspeed/chratio2   # chopper 5 90 deg rotated
            else:
                TOFoffset = 15.0/chspeed/chratio2   # normal mode
            tel = (chopper.a[0]-chopper.a[5]) * chopper.mn * chwl * 1.0e-10 / chopper.h + TOFoffset
            tel += self.delay
            n = int(tel / (chratio / chspeed * 30.0))
            tel = tel - n * (chratio / chspeed * 30.0)
            tel = int(round(tel/5.0e-8))
            ctr.delay = tel

        if 'm' in preset:
            self._last_mode = 'monitor'
            self._last_preset = preset['m']
        else:
            self._last_mode = 'time'
            self._last_preset = preset['t']

        self._startheader = self._start_header(interval, chdelay)
        # update interval: about every 30 seconds for 1024 time channels
        self._updateevery = int(30*ctr.timechannels/1024 * 40)

        # start new file
        self._newFile()

        self._startheader.append('FileName: %s\n' % self.lastfilename)
        # write once already, to check that it doesn't exist
        self._writeFile(''.join(self._last_startheader))

        self._starttime = self._lasttime = currenttime()
        self._lastcounts = 0
        self._lastmonitor = 0
        self.log.info('Measurement %s started' % self.lastfilenumber)
        ctr.start(**preset)

    def _start_header(self, interval, chdelay):
        ctr = self._adevs['counter']
        chwl, chspeed, chratio, chcrc, chst = self._adevs['chopper'].read()
        head = []
        head.append('StartDate: %s\n' % strftime('%d.%m.%Y'))
        head.append('StartTime: %s\n' % strftime('%H:%M:%S'))
        if self._last_mode == 'monitor':
            head.append('TOF_MMode: Monitor_Counts\n')
            head.append('TOF_CountPreselection: %d\n' % self._last_preset)
        else:
            head.append('TOF_MMode: Total_Time\n')
            head.append('TOF_TimePreselection: %g\n' % self._last_preset)
        head.append('TOF_TimeInterval: %g\n' % interval)
        head.append('TOF_ChannelWidth: %lu\n' % ctr.channelwidth)
        head.append('TOF_NumInputs: %lu\n' % ctr.numinputs)
        head.append('TOF_Delay: %lu\n' % ctr.delay)
        head.append('TOF_MonitorInput: %d\n' % ctr.monitorchannel)
        head.append('TOF_Ch5_90deg_Offset: %d\n' % self.ch5_90deg_offset)
        guess = round(4.0*chwl*2.527784152e-4/5.0e-8/ctr.channelwidth)
        head.append('TOF_ChannelOfElasticLine_Guess: %d\n' % guess)
        hvvals = []
        for i in range(3):
            try:
                value = session.getDevice('hv%d' % i).read()
            except NicosError:
                value = 'unknown'
            hvvals.append(value)
        head.append('HV_PowerSupplies: hv0-2: %s V, %s V, %s V\n' % tuple(hvvals))
        lvvals = []
        for i in range(8):
            try:
                value = session.getDevice('lv%d' % i).read()
            except NicosError:
                value = 'unknown'
            hvvals.append(value)
        head.append('LV_PowerSupplies: lv0-7: %s\n' % ', '.join(map(str, lvvals)))
        slit_pos = session.getDevice('ss').read()
        head.append('SampleSlit_ho: %s\n' % slit_pos[0])
        head.append('SampleSlit_hg: %s\n' % slit_pos[2])
        head.append('SampleSlit_vo: %s\n' % slit_pos[1])
        head.append('SampleSlit_vg: %s\n' % slit_pos[3])
        head.append('Chopper_Speed: %.1f rpm\n' % chspeed)
        head.append('Chopper_Wavelength: %.2f A\n' % chwl)
        head.append('Chopper_Ratio: %s\n' % chratio)
        head.append('Chopper_SlitType: %s\n' % chst)
        head.append('Chopper_Delay: %s\n' % chdelay)
        for i in range(4):
            try:
                value = session.getDevice('vac%d' % i).read()
            except NicosError:
                value = 'unknown'
            head.append('Chopper_Vac%d: %s\n' % (i, value))
        gvals = {}
        for gonio in ['gx', 'gy', 'gz', 'gphi', 'gcx', 'gcy']:
            try:
                dev = session.getDevice(gonio)
                gvals[gonio] = dev.format(dev.read()) + ' ' + dev.unit
            except NicosError:
                gvals[gonio] = 'unknown'
        head.append('Goniometer_XYZ: %s %s %s\n' % (gvals['gx'],
                                                    gvals['gy'], gvals['gz']))
        head.append('Goniometer_PhiCxCy: %s %s %s\n' % (gvals['gphi'],
                                                        gvals['gcx'], gvals['gcy']))
        return head

    def _saveDataFile(self):
        try:
            meastime, moncounts, counts = self._adevs['counter'].read_full()
        except NicosError:
            self.log.exception('error getting measurement data')
            return 0, 0, 0
        head = []
        head.append('SavingDate: %s\n' % strftime('%d.%m.%Y'))
        head.append('SavingTime: %s\n' % strftime('%H:%M:%S'))
        if self._last_mode == 'monitor':
            if moncounts < self._last_preset:
                head.append('ToGo: %d counts\n' % (self._last_preset - moncounts))
            head.append('Status: %5.1f %% completed\n' %
                        ((100. * moncounts)/self._last_preset))
        else:
            if meastime < self._last_preset:
                head.append('ToGo: %.0f s\n' % (self._last_preset - meastime))
            head.append('Status: %5.1f %% completed\n' %
                        ((100. * meastime)/self._last_preset))
        # XXX sample temperature info
        head.append('MonitorCounts: %d\n' % moncounts)
        head.append('NumOfDetectors: %d\n' % counts[1])
        head.append('NumOfChannels: %d\n' % counts[0])
        head.append('aDetInfo(%u,%u): \n' % (14, self._detinfolength))
        with open(self.lastfilename, 'w') as fp:
            fp.write(''.join(self._staticheader))
            fp.write(''.join(head))
            fp.write(''.join(self._detinfo))
            fp.write('aData(%u,%u): \n' % (counts[1], counts[0]))
            np.savetxt(fp, counts[2:], '%d')
            os.fsync(fp)
        return meastime, moncounts, counts

    def duringMeasureHook(self, i):
        if i % self._updateevery:
            return
        result = self._saveDataFile()
        if not result[0]:
            return
        countsum = sum(result[2]) - result[1]  # monitor counts are in the array
        monrate = result[1]/result[0]
        monrate_inst = (result[1] - self._lastmonitor) / (result[0] - self._lasttime)
        detrate = countsum/result[0]
        detrate_inst = (countsum - self._lastcounts) / (result[0] - self._lasttime)
        self._lasttime = result[0]
        self._lastmonitor = result[1]
        self._lastcounts = countsum
        # XXX sample temperature info
        self.log.info('Monitor: rate: %.3f counts/s, instantaneous rate: %.3f counts/s' %
                      (monrate, monrate_inst))
        self.log.info('Signal: rate: %.3f counts/s, instantaneous rate: %.3f counts/s' %
                      (detrate, detrate_inst))

    def doStop(self):
        self._adevs['counter'].stop()

    def doReset(self):
        pass

    def doSave(self):
        self._saveDataFile()
        # XXX save log files accordingly


# XXX nosave measurement!
