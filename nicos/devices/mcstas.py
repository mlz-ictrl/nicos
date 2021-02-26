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
#   Georg Brandl <g.brandl@fz-juelich.de>
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
from nicos.core import ArrayDesc, Param, Value, floatrange, intrange, status, \
    tupleof, Override, Attach, MASTER, Waitable, Readable
from nicos.core.constants import FINAL, LIVE
from nicos.devices.generic import ActiveChannel, ImageChannelMixin, \
    PassiveChannel
from nicos.utils import createThread


class McStasSimulation(Readable):
    """Base device for running McStas simulations.

    This is used as a central place to start and control the simulation process.
    Individual detector channels can use it as an attached device in order
    to get data to return.
    """

    _mythread = None
    _process = None
    _started = None
    _start_time = None

    # to be implemented in derived classes
    _mcstas_params = None

    parameters = {
        'mcstasprog': Param('Name of the McStas simulation executable',
                            type=str, settable=False),
        'mcstasdir':  Param('Directory where McStas stores results', type=str,
                            default='%(session.experiment.dataroot)s'
                                    '/singlecount',
                            settable=False),
        'mcsiminfo':  Param('Name for the McStas Siminfo file', settable=False,
                            type=str, default='mccode.sim'),
        'neutronspersec':  Param('Approximate simulated neutrons per second '
                                 'for this machine. Tune this parameter '
                                 'according to your hardware for realistic '
                                 'count times', settable=True,
                                 type=floatrange(1e3), default=1e6),
        'intensityfactor': Param('Constant multiplied with simulated McStas '
                                 'intensity to get a simulated neutron counts '
                                 'per second', settable=True,
                                 type=floatrange(1.)),
        'preselection':    Param('Simulation preset value (should be set by '
                                 'the timer device)', type=float,
                                 settable=True, default=1., unit='s'),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
    }

    def doInit(self, mode):
        self._workdir = os.getcwd()
        self._interesting_files = set([self.mcsiminfo])

    def doStatus(self, maxage=0):
        if self._started or (self._mythread and self._mythread.is_alive()):
            return status.BUSY, 'running'
        return status.OK, ''

    def doRead(self, maxage=0):
        return ''  # nothing useful here

    def _saveIntermediate(self):
        self._send_signal(SIGUSR2)

    def _joinProcess(self):
        if self._mythread and self._mythread.is_alive():
            self._mythread.join(1.)
            if self._mythread.is_alive():
                self.log.exception("Couldn't join readout thread.")
            else:
                self._mythread = None

    def _prepare_params(self):
        """Return a list of key=value strings.

        Each entry defines a parameter setting for the mcstas simulation call.

        examples:
            param=10
        """
        raise NotImplementedError('Please implement _prepare_params method')

    def _prepare(self, *datafiles):
        """Prepare the simulation parameters.

        This is ok to be called multiple times, since multiple channels can be
        connected to this simulation.

        If some `datafiles` are present, they must be simple filenames and
        are registered as "interesting" files which must be written completely
        by the McStas process before `send_signal` returns.
        """
        self._interesting_files.update(path.basename(p) for p in datafiles)
        if not self._mcstas_params:
            self._mcstas_params = ' '.join(self._prepare_params())
            self.log.debug('McStas parameters: %s', self._mcstas_params)
            self._start_time = None
            self._mcstasdirpath = session.experiment.data.expandNameTemplates(
                self.mcstasdir)[0]

    def _start(self):
        """Start the simulation.

        This is ok to be called multiple times, since multiple channels can be
        connected to this simulation.
        """
        if not self._started:
            self._started = True
            self._mythread = createThread('detector %s' % self, self._run)

    def _finish(self):
        """Finish the simulation.

        This is ok to be called multiple times, since multiple channels can be
        connected to this simulation.
        """
        if self._started:
            self.log.debug('still running, finishing up')
            self._send_signal(SIGTERM)
            self._joinProcess()
        self._started = None
        self._mcstas_params = None

    def _send_signal(self, sig):
        """Send a signal to the McStas process, if it is running."""
        if self._process and self._process.is_running():
            self._process.send_signal(sig)
            # wait for mcstas releasing interesting fds
            try:
                while self._process and self._process.is_running():
                    fnames = set(path.basename(f.path) for f in self._process.open_files())
                    if not (fnames & self._interesting_files):
                        break
                    session.delay(.01)
            except (AccessDenied, NoSuchProcess):
                self.log.debug(
                    'McStas process already terminated in _send_signal(%r)',
                    sig)
            self.log.debug('McStas process has written file on signal (%r)',
                           sig)

    def _getDatafile(self, name):
        """Return a file object for the McStas data file with given name."""
        # pylint: disable=consider-using-with
        return open(path.join(self._mcstasdirpath, name), 'r')

    def _getTime(self):
        """Return elapsed time for simulation."""
        if self._started:
            return min(time.time() - self._start_time, self.preselection)
        else:
            return self.preselection

    def _getScaleFactor(self):
        """Return scale factor for simulation intensity data."""
        return self._getTime() * self.intensityfactor

    def _run(self):
        """Thread to run McStas simulation executable.

        The current settings of the instrument parameters will be transferred
        to it.
        """
        try:
            shutil.rmtree(self._mcstasdirpath)
        except OSError:
            self.log.warning('could not remove old data')
        command = '%s -n %d -d %s %s' % (
            self.mcstasprog, self.neutronspersec * self.preselection,
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


class McStasImage(ImageChannelMixin, PassiveChannel):
    """Image channel based on McStas simulation.

    This channel should be used together with `McStasTimerChannel`
    which provides the preselection [s] for calculating the number of
    simulated neutron counts:

      Ncounts = preselection [s] * neutronspersec [cts/s]

    Note: Please configure **neutronspersec** to match the average simulated
    neutron counts per second on your system.
    """

    attached_devices = {
        'mcstas': Attach('McStasSimulation device', McStasSimulation),
    }

    parameters = {
        'size': Param('Detector size in pixels (x, y)',
                      settable=False,
                      type=tupleof(intrange(1, 8192), intrange(1, 8192)),
                      default=(1, 1),
                      ),
        'mcstasfile': Param('Name of the McStas data file',
                            type=str, settable=False),
    }

    def doInit(self, mode):
        self.arraydesc = ArrayDesc(self.name, self.size, '<u4')

    def doReadArray(self, quality):
        self.log.debug('quality: %s', quality)
        if quality == LIVE:
            self._attached_mcstas._saveIntermediate()
        elif quality == FINAL:
            self._attached_mcstas._joinProcess()
        self._readpsd(quality)
        return self._buf

    def doPrepare(self):
        self._buf = np.zeros(self.size[::-1])
        self.readresult = [0]
        self._attached_mcstas._prepare(self.mcstasfile)

    def valueInfo(self):
        return (Value(self.name + '.sum', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'),)

    def doStart(self):
        self._attached_mcstas._start()

    def doStatus(self, maxage=0):
        return Waitable.doStatus(self, maxage)

    def doFinish(self):
        self._attached_mcstas._finish()

    def doStop(self):
        self.doFinish()

    def _readpsd(self, quality):
        try:
            with self._attached_mcstas._getDatafile(self.mcstasfile) as f:
                lines = f.readlines()[-3 * (self.size[1] + 1):]
            if lines[0].startswith('# Data') and self.mcstasfile in lines[0]:
                factor = self._attached_mcstas._getScaleFactor()
                buf = np.loadtxt(lines[1:self.size[1] + 1], dtype=np.float32)
                self._buf = (buf * factor).astype(np.uint32)
                self.readresult = [self._buf.sum()]
            elif quality != LIVE:
                raise OSError('Did not find start line: %s' % lines[0])
        except OSError:
            if quality != LIVE:
                self.log.exception('Could not read result file', exc=1)


class McStasTimer(ActiveChannel, Waitable):
    """Timer channel for McStas simulations

    This channel provides an internal neutron timer for running McStas
    simulations using `McStasImage`.
    """

    attached_devices = {
        'mcstas': Attach('McStasImage channel', McStasSimulation),
    }

    parameters = {
        'curvalue':  Param('Current value', settable=True, unit='main'),
    }

    parameter_overrides = {
        'unit': Override(default='s'),
    }

    is_timer = True

    def doInit(self, mode):
        if mode == MASTER:
            self.curvalue = 0

    def setChannelPreset(self, name, value):
        ActiveChannel.setChannelPreset(self, name, value)
        self._attached_mcstas.preselection = value

    def doPrepare(self):
        self._attached_mcstas._prepare()

    def doStart(self):
        self._attached_mcstas._start()

    def doStatus(self, maxage=0):
        # wait for attached mcstas simulation
        return Waitable.doStatus(self, maxage)

    def doRead(self, maxage=0):
        self.curvalue = self._attached_mcstas._getTime()
        return self.curvalue

    def doFinish(self):
        self._attached_mcstas._finish()

    def doStop(self):
        self.doFinish()

    def valueInfo(self):
        return Value(self.name, unit='s', type='time', fmtstr='%.3f'),
