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

from __future__ import with_statement

__version__ = "$Revision$"

import os
from time import strftime, asctime, localtime, time as currenttime

import numpy as np

from nicos import session
from nicos.core import Measurable, Param, Value, Override, NicosError, \
     intrange, listof, status
from nicos.abstract import ImageStorage

from nicos.toftof.toni import DelayBox
from nicos.toftof.chopper import Controller
from nicos.toftof.tofcounter import TofCounter
from nicos.toftof import calculations as calc


class TofTofMeasurement(Measurable, ImageStorage):

    attached_devices = {
        'counter': (TofCounter, 'The TOF counter'),
        'chopper': (Controller, 'The chopper controller'),
        'chdelay': (DelayBox, 'Setting chopper delay'),
    }

    parameters = {
        'delay':            Param('Additional chopper delay', type=float,
                                  settable=True, default=0),
        'timechannels':     Param('Number of time channels', default=1024,
                                  type=intrange(1, 1025), settable=True),
        'timeinterval':     Param('Time interval between pulses, or zero to '
                                  'auto-select', type=float, settable=True),
        'detinfofile':      Param('Path to the detector-info file',
                                  type=str, mandatory=True),

        # status parameters
        'laststats':       Param('Count statistics of the last measurement',
                                 type=listof(float), settable=True),
    }

    parameter_overrides = {
        'nametemplate': Override(default='%06d_0000.raw'),
        'subdir': Override(default='', mandatory=False),
    }

    def valueInfo(self):
        return Value('filename', type='info'),

    def presetInfo(self):
        return ['info', 't', 'm', 'nosave']

    def doInit(self):
        with open(self.detinfofile, 'U') as fp:
            self._detinfo = list(fp)
        i = 0
        for i, line in enumerate(self._detinfo):
            if not line.startswith('#'):
                break
        self._detinfolength = len(self._detinfo) - i
        dmap = {}
        for line in self._detinfo:
            if not line.startswith('#'):
                ls = line.split()
                if 'None' not in ls[13]:
                    dmap[int(ls[12])] = float(ls[5])
        self._anglemap = tuple((i-1) for i in sorted(dmap, key=dmap.__getitem__))
        self._measuring = False
        self._devicelogs = {}
        self._lastnosave = False

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
        self._curtitle = preset.get('info', '')
        self._curnosave = bool(preset.get('nosave', False))

        try:
            rc = session.getDevice('rc')
            if rc.status()[0] != status.BUSY:
                self.log.warning('radial collimator is not moving!')
        except NicosError:
            self.log.warning('could not check radial collimator', exc=1)

        self.log.debug('reading chopper parameters')
        chwl, chspeed, chratio, _, chst = self._adevs['chopper']._getparams()
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

        # make sure to set the correct monitor input and number of time channels
        # in the TACO server
        ctr.timechannels = ctr.timechannels
        ctr.monitorchannel = ctr.monitorchannel

        if 'm' in preset:
            self._last_mode = 'monitor'
            self._last_preset = preset['m']
        else:
            self._last_mode = 'time'
            self._last_preset = preset['t']

        self.log.debug('collecting status information')
        self._startheader = self._startHeader(interval, chdelay)
        # update interval: about every 30 seconds for 1024 time channels
        self._updateevery = max(int(15.*ctr.timechannels/1024 * 40), 80)

        # start new file
        self._newFile(increment=not self._lastnosave)
        self._startheader.append('FileName: %s\n' % self.lastfilename)

        # open individual device logfiles
        self._openDeviceLogs()

        self._lastcounts = 0
        self._lastmoncounts = 0
        self._lasttemps = []
        self.log.info('Measurement %06d started' % self.lastfilenumber)
        self._measuring = True
        self._starttime = self._lasttime = currenttime()
        ctr.start(**preset)

    def _startHeader(self, interval, chdelay):
        ctr = self._adevs['counter']
        chwl, chspeed, chratio, chcrc, chst = self._adevs['chopper']._getparams()
        head = []
        head.append('File_Creation_Time: %s\n' % asctime())
        head.append('Title: %s\n' % self._curtitle)
        head.append('ExperimentTitle: %s\n' % session.experiment.title)
        head.append('ProposalTitle: %s\n' % session.experiment.title)
        head.append('ProposalNr: %s\n' % session.experiment.proposal)
        head.append('ExperimentTeam: %s\n' % ', '.join(session.experiment.users))
        head.append('LocalContact: %s\n' % session.experiment.localcontact)
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
        head.append('TOF_TimeChannels: %u\n' % ctr.timechannels)
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
            lvvals.append(value)
        head.append('LV_PowerSupplies: lv0-7: %s\n' % ', '.join(map(str, lvvals)))
        slit_pos = session.getDevice('slit').read()
        head.append('SampleSlit_ho: %s\n' % slit_pos[0])
        head.append('SampleSlit_hg: %s\n' % slit_pos[2])
        head.append('SampleSlit_vo: %s\n' % slit_pos[1])
        head.append('SampleSlit_vg: %s\n' % slit_pos[3])
        head.append('Chopper_Speed: %.1f rpm\n' % chspeed)
        head.append('Chopper_Wavelength: %.2f A\n' % chwl)
        head.append('Chopper_Ratio: %s\n' % chratio)
        head.append('Chopper_CRC: %s\n' % chcrc)
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

    def _openDeviceLogs(self):
        if not self._cache:
            return
        self._closeDeviceLogs()
        self._logstarttime = currenttime()
        i = 5001
        for dev in ['ReactorPower', 'chDS'] + session.experiment.sampleenv:
            try:
                if isinstance(dev, str):
                    dev = session.getDevice(dev)
                fn = self.lastfilename.replace('0000.raw', '%04d.raw' % i)
                self._devicelogs[dev.name.lower()] = fp = open(fn, 'w')
                fp.write('# File_Creation_Time: %s\n' %
                         asctime(localtime(self._logstarttime)))
                fp.write('# Title: logging of changes to %s' % dev.name)
                if dev.unit:
                    fp.write(' (%s)' % dev.unit)
                fp.write('\n\n%10.2f  %s\n' % (0.0, dev.read()))
                self._cache.addCallback(dev, 'value', self._logCallback)
                self.log.debug('opened logfile %d for device %s' % (i, dev))
            except Exception:
                self.log.warning('could not open device logfile for %s' % dev, exc=1)
                self._devicelogs.pop(dev.name.lower(), None)
            i += 1

    def _logCallback(self, key, value, time):
        self.log.debug('device log: %s = %s' % (key, value))
        devname = key.split('/')[0]
        if devname not in self._devicelogs:
            return  # shouldn't happen
        self._devicelogs[devname].write(
            '%10.2f  %s\n' % (time - self._logstarttime, value))

    def _closeDeviceLogs(self):
        # first clear the dictionary, then close files, so that the callback
        # doesn't write to closed files
        olddevlogs = self._devicelogs.copy()
        self._devicelogs.clear()
        self.log.debug('closing device logs')
        for devname, fp in olddevlogs.iteritems():
            try:
                fp.close()
            except Exception:
                pass
            if self._cache:
                self._cache.removeCallback(devname, 'value')

    def _saveDataFile(self):
        try:
            timeleft, moncounts, counts = self._adevs['counter'].read_full()
        except NicosError:
            self.log.exception('error reading measurement data')
            return 0, 0, 0, 0, 0, None
        meastime = currenttime() - self._starttime
        countsum = counts.sum() - moncounts  # monitor counts are in the array
        head = []
        head.append('SavingDate: %s\n' % strftime('%d.%m.%Y'))
        head.append('SavingTime: %s\n' % strftime('%H:%M:%S'))
        if self._last_mode == 'monitor':
            if moncounts < self._last_preset:
                head.append('ToGo: %d counts\n' % (self._last_preset - moncounts))
            head.append('Status: %5.1f %% completed\n' %
                        ((100. * moncounts) / self._last_preset))
        else:
            if timeleft > 0:
                head.append('ToGo: %.0f s\n' % timeleft)
            head.append('Status: %5.1f %% completed\n' %
                (100. * (self._last_preset - timeleft) / self._last_preset))
        # sample temperature is assumed to be the first device in the envlist
        tempinfo = []
        if session.experiment.sampleenv:
            tdev = session.experiment.sampleenv[0]
            try:
                curtemp = tdev.read()
                tempinfo.append(curtemp)
                tempinfo.append(tdev.unit)
                if tdev.unit == 'degC':
                    curtemp += 273.15
            except NicosError:
                curtemp = 0
            else:
                self._lasttemps.append(curtemp)
                lt = self._lasttemps
                stats = np.mean(lt), np.std(lt), np.min(lt), np.max(lt)
                head.append('AverageSampleTemperature: %10.4f K\n' % stats[0])
                head.append('StandardDeviationOfSampleTemperature: %10.4f K\n' %
                            stats[1])
                head.append('MinimumSampleTemperature: %10.4f K\n' % stats[2])
                head.append('MaximumSampleTemperature: %10.4f K\n' % stats[3])
                tempinfo.extend(stats)
                tempinfo = tuple(tempinfo)
        # more info
        head.append('MonitorCounts: %d\n' % moncounts)
        # next 3 fields are new in the data file
        head.append('TotalCounts: %d\n' % countsum)
        head.append('MonitorCountRate: %.3f\n' % (moncounts / meastime))
        head.append('TotalCountRate: %.3f\n' % (countsum / meastime))
        head.append('NumOfDetectors: %d\n' % counts.shape[0])
        head.append('NumOfChannels: %d\n' % counts.shape[1])
        head.append('Plattform: Linux\n')
        head.append('aDetInfo(%u,%u): \n' % (14, self._detinfolength))
        self.log.debug('saving data file')
        with open(self.lastfilename, 'w') as fp:
            fp.write(''.join(self._startheader))
            fp.write(''.join(head))
            fp.write(''.join(self._detinfo))
            fp.write('aData(%u,%u): \n' % (counts.shape[0], counts.shape[1]))
            np.savetxt(fp, counts, '%d')
            os.fsync(fp)
        try:
            treated = counts.T[self._anglemap, :].astype('<I4')
            ndet = treated.shape[0]
            session.updateLiveData('toftof', self.lastfilename, '<I4',
                                   1024, ndet, 1, meastime, buffer(treated))
        except Exception:
            pass
        return timeleft, moncounts, counts, countsum, meastime, tempinfo

    def duringMeasureHook(self, i):
        if (i + 400) % self._updateevery:
            return
        self.log.debug('collecting progress info')
        _, moncounts, _, countsum, meastime, tempinfo = self._saveDataFile()
        monrate = detrate = 0.0
        if meastime > 0:
            monrate = moncounts / meastime
            monrate_inst = (moncounts - self._lastmoncounts) / (meastime - self._lasttime)
            detrate = countsum / meastime
            detrate_inst = (countsum - self._lastcounts) / (meastime - self._lasttime)
            if tempinfo:
                self.log.info('Sample:  current: %.4f %s, average: %.4f, '
                              'stddev: %.4f, min: %.4f, max: %.4f' % tempinfo)
            self.log.info('Monitor: rate: %8.3f counts/s, instantaneous rate: '
                          '%8.3f counts/s' % (monrate, monrate_inst))
            self.log.info('Signal:  rate: %8.3f counts/s, instantaneous rate: '
                          '%8.3f counts/s' % (detrate, detrate_inst))
        self._lasttime = meastime
        self._lastmoncounts = moncounts
        self._lastcounts = countsum
        self.laststats = [meastime, moncounts, countsum, monrate, detrate]

    def doStop(self):
        self._adevs['counter'].stop()
        self._measuring = False
        self._closeDeviceLogs()

    def doReset(self):
        self._adevs['counter'].reset()

    def doSave(self):
        self._saveDataFile()
        self.log.debug('saving current script')
        if session.experiment.scripts:
            script_fn = self.lastfilename.replace('0000.raw', '5200.raw')
            with open(script_fn, 'w') as fp:
                fp.write(session.experiment.scripts[-1])
        self.log.info('Measurement %06d finished' % self.lastfilenumber)
        self._measuring = False
        self._lastnosave = self._curnosave
        self._closeDeviceLogs()
        session.breakpoint(2)

    def doRead(self):
        return [self.lastfilename]

    def doIsCompleted(self):
        return self._adevs['counter'].isCompleted()
