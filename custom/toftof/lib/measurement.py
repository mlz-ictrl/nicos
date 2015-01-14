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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF measurement."""

import os
from time import strftime, asctime, localtime, time as currenttime

import numpy as np

from nicos import session
from nicos.core import Measurable, Device, Param, Value, Override, NicosError, \
    intrange, listof, status, ImageProducer
from nicos.pycompat import string_types

from nicos.devices.vendor.toni import DelayBox
from nicos.toftof.chopper import Controller
from nicos.toftof.tofcounter import TofCounter
from nicos.toftof import calculations as calc


class TofTofMeasurement(Measurable, ImageProducer):
    """The TOFTOF measurement device.

    This is a temporarely used device which should be substituted by a detector
    and filesaver device according to the NICOS philosophy.
    """

    attached_devices = {
        'counter': (TofCounter, 'The TOF counter'),
        'chopper': (Controller, 'The chopper controller'),
        'chdelay': (DelayBox, 'Setting chopper delay'),
    }

    parameters = {
        'delay':            Param('Additional chopper delay', type=float,
                                  settable=True, default=0),
        'timechannels':     Param('Number of time channels', default=1024,
                                  type=intrange(1, 4096), settable=True),
        'timeinterval':     Param('Time interval between pulses, or zero to '
                                  'auto-select', type=float, settable=True),
        'detinfofile':      Param('Path to the detector-info file',
                                  type=str, mandatory=True),

        # status parameters
        'laststats':       Param('Count statistics of the last measurement',
                                 type=listof(float), settable=True,),
        'filenametemplate': Param('Templates for data file name',
                                  type=str, default='%06d_0000.raw',
                                  settable=True),
    }

    parameter_overrides = {
        'subdir': Override(default='', mandatory=False),
    }

    def valueInfo(self):
        return Value('filename', type='info'),

    def presetInfo(self):
        return ['info', 't', 'm']

    def doInit(self, mode):
        with open(self.detinfofile, 'U') as fp:
            self._detinfo = list(fp)
        i = 0
        for i, line in enumerate(self._detinfo):
            if not line.startswith('#'):
                break
        self._detinfolength = len(self._detinfo) - i
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
                    list(map(int, ls[9:13])) + [' '.join(ls[13:-2]).strip("'")] +
                    list(map(int, ls[-2:]))
                )
        self._detinfo_parsed = dinfo
        self._anglemap = tuple((i-1) for i in sorted(dmap, key=dmap.__getitem__))
        self._measuring = False
        self._devicelogs = {}

    def doSetPreset(self, **preset):
        ctr = self._adevs['counter']
        ctr.stop()
        ctr.setPreset(**preset)
        self._curtitle = preset.get('info', '')
        if 'm' in preset:
            self._last_mode = 'monitor'
            self._last_preset = preset['m']
        else:
            self._last_mode = 'time'
            self._last_preset = preset['t']

    def doReadTimechannels(self):
        return self._adevs['counter'].timechannels

    def doWriteTimechannels(self, value):
        self._adevs['counter'].timechannels = value

    def doStart(self):
        ctr = self._adevs['counter']
        ctr.stop()

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
            chratio = float(chratio)
            n = int(tel / (chratio / chspeed * 30.0))
            tel = tel - n * (chratio / chspeed * 30.0)
            tel = int(round(tel/5.0e-8))
            ctr.delay = tel

        # make sure to set the correct monitor input and number of time channels
        # in the TACO server
        if ctr.timechannels is None:
            # detector disconnected?
            raise NicosError(self, 'detector device appears unavailable')
        ctr.timechannels = ctr.timechannels
        ctr.monitorchannel = ctr.monitorchannel

        self.log.debug('collecting status information')
        self._startheader = self._startHeader(interval, chdelay)
        # update interval: about every 30 seconds for 1024 time channels
        self._updateevery = min(int(30.*ctr.timechannels/1024), 80)

        self._newFile()
        self._startheader.append('FileName: %s\n' % self.lastfilename)

        # open individual device logfiles
        self._openDeviceLogs()

        self._lastcounts = 0
        self._lastmoncounts = 0
        self._lasttemps = []
        self.log.info('Measurement %06d started' % session.experiment.doReadLastimage())
        session.action('#%06d' % session.experiment.doReadLastimage())
        self._measuring = True
        self._starttime = currenttime()
        self._lasttime = 0
        ctr.start()

    def _newFile(self):
        self.log.warning('Deprecated: _newFile')
        exp = session.experiment
        sname, lname, fp = exp.createImageFile(self.filenametemplate, self.subdir)
        self._imagename = sname
        self.lastfilename = self._relpath = lname
        self._file = fp
        self._counter = session.experiment.lastimage
        self.log.info('self.lastfilename : %r' % self.lastfilename)

    def _startHeader(self, interval, chdelay):
        ctr = self._adevs['counter']
        chwl, chspeed, chratio, chcrc, chst = self._adevs['chopper']._getparams()
        head = []
        head.append('File_Creation_Time: %s\n' % asctime())
        head.append('Title: %s\n' % self._curtitle)
        head.append('ExperimentTitle: %s\n' % session.experiment.sample.samplename)
        head.append('ProposalTitle: %s\n' % session.experiment.title)
        head.append('ProposalNr: %s\n' % session.experiment.proposal)
#        head.append('ExperimentTeam: %s\n' % ', '.join(session.experiment.users))
        head.append('ExperimentTeam: %s\n' % session.experiment.users)
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
        try:
            guide = session.getDevice('ngc').read()
        except NicosError:
            guide = 'unknown'
        head.append('Guide_config: %s\n' % guide)
        head.append('Chopper_Speed: %.1f rpm\n' % chspeed)
        head.append('Chopper_Wavelength: %.2f A\n' % chwl)
        head.append('Chopper_Ratio: %s\n' % chratio)
        head.append('Chopper_CRC: %s\n' % chcrc)
        head.append('Chopper_SlitType: %s\n' % chst)
        head.append('Chopper_Delay: %s\n' % chdelay)
#       for i in range(4):
        for i in range(0):
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
                if isinstance(dev, string_types):
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
                if isinstance(dev, Device):
                    self._devicelogs.pop(dev.name.lower(), None)
            i += 1

    def _logCallback(self, key, value, time):
        self.log.debug('device log: %s = %s' % (key, value))
        devname = key.split('/')[0]
        if devname not in self._devicelogs:
            return  # shouldn't happen
        if value is not None:  # ignore expiration messages
            self._devicelogs[devname].write(
                '%10.2f  %s\n' % (time - self._logstarttime, value))
            self._devicelogs[devname].flush()

    def _closeDeviceLogs(self):
        # first clear the dictionary, then close files, so that the callback
        # doesn't write to closed files
        self.laststats = [0.0] * 7
        olddevlogs = self._devicelogs.copy()
        self._devicelogs.clear()
        self.log.debug('closing device logs')
        for devname, fp in olddevlogs.items():
            try:
                fp.close()
            except Exception:
                pass
            if self._cache:
                self._cache.removeCallback(devname, 'value', self._logCallback)

    def _saveDataFile(self):
        try:
            timeleft, moncounts, counts = self._adevs['counter'].read_full()
            if counts is None:
                raise NicosError(self, 'detector returned no counts')
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
                if tdev.unit == 'degC':
                    tempinfo[2] -= 273.15
                    tempinfo[4] -= 273.15
                    tempinfo[5] -= 273.15
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
        # write into a different file, so that if the writing is interrupted,
        # the original file with full contents is not overwritten
        with open(self.lastfilename + '.new', 'w') as fp:
            fp.write(''.join(self._startheader))
            fp.write(''.join(head))
            fp.write(''.join(self._detinfo))
            fp.write('aData(%u,%u): \n' % (counts.shape[0], counts.shape[1]))
            np.savetxt(fp, counts, '%d')
            os.fsync(fp)
        # and only if the write completed successfully, move the new file over
        os.rename(self.lastfilename + '.new', self.lastfilename)
        try:
            treated = counts[self._anglemap, :].astype('<u4')
            ndet, ntime = treated.shape
            session.updateLiveData('toftof', self.lastfilename, '<u4',
                                   ntime, ndet, 1, meastime, buffer(treated))
        except Exception:
            pass
        return timeleft, moncounts, counts, countsum, meastime, tempinfo

    def duringMeasureHook(self, elapsed):
        if elapsed - self._lasttime < self._updateevery:
            return
        self.log.debug('collecting progress info')
        _, moncounts, _, countsum, meastime, tempinfo = self._saveDataFile()
        monrate = detrate = monrate_inst = detrate_inst = 0.0
        if meastime > 0:
            monrate = moncounts / meastime
            monrate_inst = (moncounts - self._lastmoncounts) / \
                (meastime - self._lasttime)
            detrate = countsum / meastime
            detrate_inst = (countsum - self._lastcounts) / \
                (meastime - self._lasttime)
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
        self.laststats = [meastime, moncounts, countsum, monrate, detrate,
                          monrate_inst, detrate_inst,]

    def doStop(self):
        self._adevs['counter'].stop()
        self._measuring = False
        self._closeDeviceLogs()

    def doReset(self):
        self._adevs['counter'].reset()

    def doSave(self, exception=False):
        _, moncounts, _, countsum, meastime, tempinfo = self._saveDataFile()
        monrate = moncounts / meastime
        detrate = countsum / meastime
        self.log.debug('saving current script')
        if session.experiment.scripts:
            script_fn = self.lastfilename.replace('0000.raw', '5200.raw')
            with open(script_fn, 'w') as fp:
                fp.write(session.experiment.scripts[-1])
        self.log.info('Measurement %06d finished' %
                      session.experiment.doReadLastimage())
        self.log.info('Monitor: average rate: %8.3f counts/s' % monrate)
        self.log.info('Signal:  average rate: %8.3f counts/s' % detrate)
        if tempinfo:
            self.log.info('Sample:  current: %.4f %s, average: %.4f, '
                          'stddev: %.4f, min: %.4f, max: %.4f' % tempinfo)
        self._measuring = False
        self._closeDeviceLogs()
        session.breakpoint(2)

    def doRead(self, maxage=0):
        return [self.lastfilename]

    def doIsCompleted(self):
        return self._adevs['counter'].isCompleted()
