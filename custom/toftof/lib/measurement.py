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
from nicos.core import Measurable, Param, Value, Override, \
     NicosError, intrange
from nicos.abstract import ImageStorage

from nicos.toftof.toni import DelayBox
from nicos.toftof.chopper import Controller
from nicos.toftof.tofcounter import TofCounter
from nicos.toftof import calculations as calc

# TofChopper parameters: wavelength, speed, ratio, crc, slittype


class TofTofMeasurement(Measurable, ImageStorage):

    attached_devices = {
        'counter': (TofCounter, 'The TOF counter'),
        'chopper': (Controller, 'The chopper controller'),
        'chdelay': (DelayBox, 'Setting chopper delay'),
    }

    # XXX lastcounts, lastmonitor, rate etc. als parameter
    parameters = {
        'delay':            Param('Additional chopper delay', type=float,
                                  settable=True, default=0),
        'timechannels':     Param('Number of time channels', default=1024,
                                  type=intrange(1, 1025), settable=True),
        'timeinterval':     Param('Time interval between pulses, or zero to '
                                  'auto-select', type=float, settable=True),
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
        self._finished = False

    def doSetPreset(self, **preset):
        self._adevs['counter'].setPreset(**preset)

    def doReadTimechannels(self):
        return self._adevs['counter'].timechannels

    def doWriteTimechannels(self, value):
        self._adevs['counter'].timechannels = value

    def doStart(self, **preset):
        ctr = self._adevs['counter']
        ctr.stop()
        self.doSetPreset(**preset)

        self.log.debug('reading chopper parameters')
        chwl, chspeed, chratio, chcrc, chst = self._adevs['chopper']._getparams()
        if chratio == 1:
            chratio2 = 1.0
        else:
            chratio2 = (chratio-1.0)/chratio

        # select time interval from chopper parameters
        if self.timeinterval == 0:
            if chspeed == 0:
                interval = 0.052
            else:
                interval = 30.0 / chspeed * chratio
        else:
            interval = self.timeinterval
        ctr.timeinterval = interval

        # select chopper delay from chopper parameters
        self.log.debug('setting chopper delay')
        chdelay = 0.0
        if chspeed > 150:
            if self._adevs['chopper'].ch5_90deg_offset:
                # chopper 5 90 deg rotated
                chdelay = -15.0e6/chspeed/chratio2
            if chst == 1:
                chdelay = 15.0e6/chspeed
            chdelay += (252.7784 * chwl * 8.028 -
                        15.0e6*(1.0/chspeed/chratio2-1.0/chspeed))
            chdelay = chdelay % (30.0e6/chspeed)
            chdelay -= 100.0
            if chdelay < 0:
                chdelay += 30.0e6/chspeed
            chdelay = int(round(chdelay))
        self._adevs['chdelay'].start(chdelay)

        # select counter delay from chopper parameters
        self.log.debug('setting counter delay')
        if chspeed > 150:
            if self._adevs['chopper'].ch5_90deg_offset:
                TOFoffset = 30.0/chspeed/chratio2   # chopper 5 90 deg rotated
            else:
                TOFoffset = 15.0/chspeed/chratio2   # normal mode
            tel = (calc.a[0]-calc.a[5]) * calc.mn * chwl * 1.0e-10 / calc.h + \
                TOFoffset
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

        self.log.debug('collecting status information')
        self._startheader = self._start_header(interval, chdelay)
        # update interval: about every 30 seconds for 1024 time channels
        self._updateevery = max(int(30.*ctr.timechannels/1024 * 40), 10)

        # start new file
        self._newFile()

        self._startheader.append('FileName: %s\n' % self.lastfilename)
        # write once already, to check that it doesn't exist
        self._writeFile(''.join(self._startheader))

        self._starttime = self._lasttime = currenttime()
        self._lastcounts = 0
        self._lastmonitor = 0
        self._lasttemps = []
        self._finished = False
        self.log.info('Measurement %06d started' % self.lastfilenumber)
        ctr.start(**preset)

    def _start_header(self, interval, chdelay):
        ctr = self._adevs['counter']
        chwl, chspeed, chratio, chcrc, chst = self._adevs['chopper']._getparams()
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
        head.append('TOF_Ch5_90deg_Offset: %d\n' %
                    self._adevs['chopper'].ch5_90deg_offset)
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
        slit_pos = session.getDevice('slit').read()
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
            return 0, 0, 0, 0, None
        countsum = counts.sum() - moncounts  # monitor counts are in the array
        head = []
        head.append('SavingDate: %s\n' % strftime('%d.%m.%Y'))
        head.append('SavingTime: %s\n' % strftime('%H:%M:%S'))
        if self._last_mode == 'monitor':
            if moncounts < self._last_preset:
                head.append('ToGo: %d counts\n' % (self._last_preset - moncounts))
            head.append('Status: %5.1f %% completed\n' %
                        ((100. * moncounts)/self._last_preset))
        else:
            if meastime > 0:  # < self._last_preset:
                head.append('ToGo: %.0f s\n' % meastime)
            head.append('Status: %5.1f %% completed\n' %
                        ((100. * (self._last_preset - meastime))/self._last_preset))
        # sample temperature is assumed to be the first device in the envlist
        if session.experiment.sampleenv:
            tdev = session.experiment.sampleenv[0]
            try:
                temperature = tdev.read()
                if tdev.unit == 'degC':
                    temperature += 273.15
            except NicosError:
                temperature = 0
            else:
                head.append('AverageSampleTemperature: %10.4f K\n' % temperature)
        # more info
        tempinfo = []
        head.append('MonitorCounts: %d\n' % moncounts)
        head.append('NumOfDetectors: %d\n' % counts.shape[1])
        head.append('NumOfChannels: %d\n' % counts.shape[0])
        head.append('aDetInfo(%u,%u): \n' % (14, self._detinfolength))
        self.log.debug('saving data file')
        with open(self.lastfilename, 'w') as fp:
            fp.write(''.join(self._startheader))
            fp.write(''.join(head))
            fp.write(''.join(self._detinfo))
            fp.write('aData(%u,%u): \n' % (counts.shape[1], counts.shape[0]))
            np.savetxt(fp, counts, '%d')
            os.fsync(fp)
        return meastime, moncounts, counts, countsum, tempinfo

    def duringMeasureHook(self, i):
        if i % self._updateevery:
            return
        self.log.debug('collecting progress info')
        meastime, moncounts, counts, countsum, tempinfo = self._saveDataFile()
        if self._last_mode == 'monitor':
            pass
        else:
            monrate = moncounts/(self._last_preset - meastime)
            monrate_inst = - (moncounts - self._lastmonitor) / (meastime - self._lasttime)
            detrate = countsum/(self._last_preset - meastime)
            detrate_inst = - (countsum - self._lastcounts) / (meastime - self._lasttime)
            # XXX sample temperature info
            self.log.info('Monitor: rate: %.3f counts/s, instantaneous rate: %.3f counts/s' %
                          (monrate, monrate_inst))
            self.log.info('Signal: rate: %.3f counts/s, instantaneous rate: %.3f counts/s' %
                          (detrate, detrate_inst))
        self._lasttime = meastime
        self._lastmonitor = moncounts
        self._lastcounts = countsum

    def doStop(self):
        self._adevs['counter'].stop()

    def doReset(self):
        pass

    def doSave(self):
        self.log.debug('measurement finished')
        self._saveDataFile()
        if session.experiment.scripts:
            with open(self.lastfilename.replace('0000.raw', '5200.raw'), 'w') as fp:
                fp.write(session.experiment.scripts[-1])
        # XXX save device log files accordingly
        #with open(self.lastfilename.replace('0000.raw', '1200.raw'), 'w') as fp:

    def doRead(self):
        return [self.lastfilename]

    def doIsCompleted(self):
        return self._adevs['counter'].isCompleted()

# XXX nosave measurement!
