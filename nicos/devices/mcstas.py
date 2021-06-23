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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""Devices for simulated instruments based on McStas simulation."""

import os
import shutil
import time
from os import path
from signal import SIGTERM, SIGUSR2
from subprocess import PIPE

import numpy as np
from psutil import AccessDenied, NoSuchProcess, Popen

from nicos import session
from nicos.core import MASTER, ArrayDesc, Attach, Override, Param, Value, \
    Waitable, floatrange, intrange, status, tupleof
from nicos.core.constants import FINAL, LIVE
from nicos.devices.generic import ActiveChannel, ImageChannelMixin, \
    PassiveChannel
from nicos.utils import createThread


class McStasImage(ImageChannelMixin, PassiveChannel):
    """Image channel based on McStas simulation.

    This channel should be used together with `McStasTimerChannel`
    which provides the preselection [s] for calculating the number of
    simulated neutron counts:

      Ncounts = preselection [s] * ratio [cts/s]

    Note: Please configure **ratio** to match the average simulated neutron
          counts per second on your system.
    """

    _mythread = None

    _process = None

    _started = None

    parameters = {
        'size': Param('Detector size in pixels (x, y)',
                      settable=False,
                      type=tupleof(intrange(1, 8192), intrange(1, 8192)),
                      default=(1, 1),
                      ),
        'mcstasprog': Param('Name of the McStas simulation executable',
                            type=str, settable=False),
        'mcstasdir': Param('Directory where McStas stores results', type=str,
                           default='%(session.experiment.dataroot)s'
                                   '/singlecount',
                           settable=False),
        'mcstasfile': Param('Name of the McStas data file',
                            type=str, settable=False),
        'mcsiminfo': Param('Name for the McStas Siminfo file', settable=False,
                           type=str, default='mccode.sim'),
        'ratio': Param('Simulated neutrons per second for this machine. Please'
                       ' tune this parameter according to your hardware for '
                       ' realistic count times', settable=False,
                       type=floatrange(1e3), default=1e6),
        'ci': Param('Constant ci multiplied with simulated intensity I',
                    settable=False, type=floatrange(1.)),
        # preselection time, usually set by McStasTimer
        'preselection': Param('Preset value for this channel', type=float,
                              settable=True, default=1.),
    }

    def doInit(self, mode):
        self.arraydesc = ArrayDesc(self.name, self.size, '<u4')
        self._workdir = os.getcwd()
        self._start_time = None

    def doReadArray(self, quality):
        self.log.debug('quality: %s', quality)
        if quality == LIVE:
            self._send_signal(SIGUSR2)
        elif quality == FINAL:
            if self._mythread and self._mythread.is_alive():
                self._mythread.join(1.)
                if self._mythread.is_alive():
                    self.log.exception("Couldn't join readout thread.")
                else:
                    self._mythread = None
        self._readpsd(quality)
        return self._buf

    def _prepare_params(self):
        """Return a list of key=value strings.

        Each entry defines a parameter setting for the mcstas simulation call.

        examples:
            param=10
        """
        raise NotImplementedError('Please implement _prepare_params method')

    def doPrepare(self):
        self._mcstas_params = ' '.join(self._prepare_params())
        self.log.debug('McStas parameters: %s', self._mcstas_params)
        self._buf = np.zeros(self.size[::-1])
        self.readresult = [0]
        self._start_time = None
        self._mcstasdirpath = session.experiment.data.expandNameTemplates(
            self.mcstasdir)[0]

    def valueInfo(self):
        return (Value(self.name + '.sum', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'),)

    def doStart(self):
        self._started = True
        self._mythread = createThread('detector %s' % self, self._run)

    def doStatus(self, maxage=0):
        if self._started or (self._mythread and self._mythread.is_alive()):
            return status.BUSY, 'busy'
        return status.OK, 'idle'

    def doFinish(self):
        self.log.debug('finish')
        self._started = None
        self._send_signal(SIGTERM)

    def _send_signal(self, sig):
        if self._process and self._process.is_running():
            self._process.send_signal(sig)
            # wait for mcstas releasing fds
            datafile =  path.join(self._mcstasdirpath, self.mcstasfile)
            siminfo = path.join(self._mcstasdirpath, self.mcsiminfo)
            try:
                while self._process and self._process.is_running():
                    fnames = [f.path for f in self._process.open_files()]
                    if siminfo not in fnames and datafile not in fnames:
                        break
                    session.delay(.01)
            except (AccessDenied, NoSuchProcess):
                self.log.debug(
                    'McStas process already terminated in _send_signal(%r)',
                    sig)
            self.log.debug('McStas process has written file on signal (%r)',
                           sig)

    def _run(self):
        """Run McStas simulation executable.

        The current settings of the instrument parameters will be transferred
        to it.
        """
        try:
            shutil.rmtree(self._mcstasdirpath)
        except OSError:
            self.log.warning('could not remove old data')
        command = '%s -n %d -d %s %s' % (
            self.mcstasprog, self.ratio * self.preselection,
            self._mcstasdirpath, self._mcstas_params,
        )
        self.log.debug('run %s', command)
        try:
            self._start_time = time.time()
            self._process = Popen(command.split(), stdout=PIPE, stderr=PIPE,
                                  cwd=self._workdir)
            out, err = self._process.communicate()
            if out:
                self.log.debug('McStas output:')
                for line in out.splitlines():
                    self.log.debug('[McStas] %s', line.decode('utf-8', 'ignore'))
            if err:
                self.log.warning('McStas found some problems:')
                for line in err.splitlines():
                    self.log.warning('[McStas] %s', line.decode('utf-8', 'ignore'))
        except OSError as e:
            self.log.error('Execution failed: %s', e)
        if self._process:
            self._process.wait()
        self._process = None
        self._started = None

    def _readpsd(self, quality):
        try:
            with open(path.join(self._mcstasdirpath, self.mcstasfile),
                      'r') as f:
                lines = f.readlines()[-3 * (self.size[0] + 1):]
            if lines[0].startswith('# Data') and self.mcstasfile in lines[0]:
                if quality == FINAL:
                    seconds = self.preselection
                else:
                    seconds = min(time.time() - self._start_time,
                                  self.preselection)
                self._buf = (np.loadtxt(lines[1:self.size[0] + 1],
                                        dtype=np.float32)
                             * self.ci
                             * seconds).astype(np.uint32)
                self.readresult = [self._buf.sum()]
            elif quality != LIVE:
                raise OSError('Did not find start line: %s' % lines[0])
        except OSError:
            if quality != LIVE:
                self.log.exception('Could not read result file')


class McStasTimer(ActiveChannel, Waitable):
    """Timer channel for McStas simulations

    This channel provides an internal neutron timer for running McStas
    simulations using `McStasImage`.
    """

    attached_devices = {
        'mcstasimage': Attach('McStasImage channel', McStasImage),
    }

    parameters = {
        'curvalue':  Param('Current value', settable=True, unit='main'),
    }

    parameter_overrides = {
        'unit': Override(default='s'),
    }

    is_timer = True

    def doInit(self, mode):
        self._start_time = None
        if mode == MASTER:
            self.curvalue = 0

    def setChannelPreset(self, name, value):
        ActiveChannel.setChannelPreset(self, name, value)
        self._attached_mcstasimage.preselection = value

    def doStart(self):
        if not self._start_time:
            self._start_time = time.time()

    def doStatus(self, maxage=0):
        # wait for attached mcstas simulation
        return Waitable.doStatus(self, maxage)

    def doRead(self, maxage=0):
        if self._start_time:
            self.curvalue = time.time() - self._start_time
        return self.curvalue

    def doFinish(self):
        self._start_time = None

    def valueInfo(self):
        return Value(self.name, unit='s', type='time', fmtstr='%.3f'),
