# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
import re
import shutil
import socket
import tempfile
from math import log10
from os import path
from signal import SIGTERM, SIGUSR2
from subprocess import PIPE
from time import monotonic

import numpy as np
from psutil import AccessDenied, NoSuchProcess, Popen

from nicos import session
from nicos.core import MASTER, SLAVE, ArrayDesc, Attach, Override, Param, \
    Readable, Value, Waitable, dictof, floatrange, intrange, nonemptystring, \
    oneof, status, tupleof
from nicos.core.constants import FINAL, LIVE
from nicos.devices.generic import ActiveChannel, Detector as BaseDetector, \
    ImageChannelMixin, PassiveChannel
from nicos.utils import createThread

# Minimum time to let McStas run before attempting to save data
# via SIGUSR2.  If McStas is still in the initialization phase,
# it can crash with SIGUSR2.
MIN_RUNTIME = 0.5
NEUTRONS_PER_SECOND_DEFAULT = 1e6


class McStasSimulation(Readable):
    """Base device for running McStas simulations.

    This is used as a central place to start and control the simulation process.
    Individual detector channels can use it as an attached device in order
    to get data to return.
    """

    _mythread = None
    _process = None
    _started = False
    _start_time = None
    _signal_sent = 0

    # to be implemented in derived classes
    _mcstas_params = None
    _mcstasdirpath = ''

    parameters = {
        'mcstasprog': Param('Name of the McStas simulation executable',
                            type=str, settable=False),
        'mcstasdir':  Param('Directory where McStas stores results', type=str,
                            default='%(session.experiment.dataroot)s'
                                    '/singlecount',
                            settable=False),
        'mcsiminfo':  Param('Name for the McStas Siminfo file', settable=False,
                            type=str, default='mccode.sim'),
        'neutronspersec': Param('Approximate simulated neutrons per second '
                                'for machines running this device. Tune this '
                                'parameter according to your hardware for '
                                'realistic count times',
                                type=dictof(nonemptystring, floatrange(1e3)),
                                default={
                                    'localhost': NEUTRONS_PER_SECOND_DEFAULT,
                                },
                                ),
        'intensityfactor': Param('Constant multiplied with simulated McStas '
                                 'intensity to get simulated neutron counts '
                                 'per second', settable=True,
                                 type=floatrange(1e-10), default=1),
        'preselection':    Param('Simulation preset value (should be set by '
                                 'the timer device)', type=float,
                                 settable=True, default=1., unit='s'),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
    }

    def doInit(self, mode):
        self._workdir = os.getcwd()
        if os.path.dirname(self._workdir) == self._workdir:  # Root dir "/"
            self._workdir = tempfile.gettempdir()
        self.log.debug('Working dir: %s', self._workdir)
        self._interesting_files = set([self.mcsiminfo])
        self._hostname = socket.getfqdn()
        self._mcstasdirpath = session.experiment.data.expandNameTemplates(
             self.mcstasdir)[0]

    def doStatus(self, maxage=0):
        if self._started or (self._mythread and self._mythread.is_alive()):
            return status.BUSY, 'running'
        return status.OK, ''

    def doRead(self, maxage=0):
        return ''  # nothing useful here

    def _saveIntermediate(self):
        # give the simulation some time to initialize
        if self._getTime() > MIN_RUNTIME:
            self._send_signal(SIGUSR2)

    def _joinProcess(self):
        if self._mythread and self._mythread.is_alive():
            self._mythread.join(1.)
            if self._mythread.is_alive():
                self.log.exception("Couldn't join readout thread.")
            else:
                self._mythread = None

    def _dev_value(self, dev, scale=1, default='0', fmtstr=None):
        """Prepare a device value as parameter for the McStas executable.

        - scale: If the device value has to be scaled (i.e. 1000 for mm -> m)
        - default: If the device is not available return this value
        - fmtstr: Used to format value instead of using device format string
        """
        if not dev:
            return str(default)
        if not fmtstr:
            fmtstr = dev.fmtstr
        if scale > 1:
            sf = int(log10(scale))
            expr = re.compile(r'(?<=\.)\d+')
            nums = re.findall(expr, fmtstr)
            if nums:
                num = int(nums[0]) + sf
                m = re.search(expr, fmtstr)
                fmtstr = '%s%d%s' % (fmtstr[:m.start()], num, fmtstr[m.end()])
        return fmtstr % (dev.read(0) / scale)

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
            self._mythread = createThread('detector %s' % self, self._run)
            self._started = True
            self._signal_sent = 0

    def _finish(self):
        """Finish the simulation.

        This is ok to be called multiple times, since multiple channels can be
        connected to this simulation.
        """
        if self._started:
            self.log.debug('still running, finishing up')
            self._send_signal(SIGTERM)
            self._joinProcess()
        self._started = False
        self._mcstas_params = None

    def _send_signal(self, sig):
        """Send a signal to the McStas process, if it is running."""
        if self._process and self._process.is_running():
            self._process.send_signal(sig)
            self._signal_sent = sig
            # wait for mcstas releasing interesting fds
            try:
                while self._process and self._process.is_running():
                    session.delay(.01)
                    fnames = set(path.basename(f.path)
                                 for f in self._process.open_files())
                    if not (fnames & self._interesting_files):
                        break
            except (AccessDenied, NoSuchProcess):
                self.log.warning(
                    'McStas process already terminated in _send_signal(%r)',
                    sig)
            self.log.debug(
                'McStas process has written file on signal (%r)', sig)

    def _getDatafile(self, name):
        """Return a file object for the McStas data file with given name."""
        # pylint: disable=consider-using-with
        return open(path.join(self._mcstasdirpath, name), 'r', encoding='utf-8')

    def _getTime(self):
        """Return elapsed time for simulation."""
        if self._started:
            if self._start_time is None:
                # McStas about to be started, preparation still in progress
                return 0
            # McStas already running
            return min(monotonic() - self._start_time, self.preselection)
        # no McStas running or about to run, i.e. finished
        return self.preselection

    def _getScaleFactor(self):
        """Return scale factor for simulation intensity data."""
        return self._getTime() * self.intensityfactor

    def _getNeutronsToSimulate(self):
        """Return number of neutrons to simulate.

        default: neutronspersec['hostname -f'] * preselection
        """
        # get the default rate
        default = self.neutronspersec.get('localhost',
                                          NEUTRONS_PER_SECOND_DEFAULT)
        # try first 'hostname -f' and then 'hostname -s' and then take
        # the default rate
        return self.neutronspersec.get(
            self._hostname, self.neutronspersec.get(
                self._hostname.split('.', 1)[0], default)) * self.preselection

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
            self.mcstasprog, self._getNeutronsToSimulate(),
            self._mcstasdirpath, self._mcstas_params,
        )
        self.log.debug('run %s', command)
        try:
            self._start_time = monotonic()
            self._process = Popen(command.split(), stdout=PIPE, stderr=PIPE,
                                  cwd=self._workdir)
            out, err = self._process.communicate()
            for line in out.splitlines():
                self.log.debug('[McStas out] %s', line.decode('utf-8', 'ignore'))
            for line in err.splitlines():
                func = self.log.warning if b'Error' in line else self.log.debug
                func('[McStas err] %s', line.decode('utf-8', 'ignore'))
        except OSError as e:
            self.log.error('Execution failed: %s', e)
        if self._process:
            self._process.wait()
        self._process = None
        self._started = False


class DetectorMixin:
    """Detector mixin for McStas simulations.

    In order to read out McStas intermediate data, it needs to be triggered
    to write data (by a signal).
    """

    attached_devices = {
        'mcstas': Attach('McStasSimulation device', McStasSimulation),
    }

    def duringMeasureHook(self, elapsed):
        quality = super().duringMeasureHook(elapsed)
        if quality == LIVE:
            self._attached_mcstas._saveIntermediate()
        return quality


class Detector(DetectorMixin, BaseDetector):
    """Detector subclass for McStas simulations that don't require a custom
    Detector class.
    """


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

    image_data_type = np.uint32

    parameters = {
        'size':       Param('Detector size in pixels (x, y)',
                            type=tupleof(intrange(1, 8192), intrange(1, 8192)),
                            mandatory=True),
        'mcstasfile': Param('Name of the McStas data file',
                            type=str, mandatory=True),
    }

    def doInit(self, mode):
        self.arraydesc = ArrayDesc(self.name, self.size[::-1], '<u4')

    def doReadArray(self, quality):
        self.log.debug('quality: %s', quality)
        if quality == FINAL:
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
        if self._attached_mcstas._signal_sent or quality == FINAL:
            try:
                with self._attached_mcstas._getDatafile(self.mcstasfile) as f:
                    lines = f.readlines()[-3 * (self.size[1] + 1):]
                if lines[0].startswith('# Data') and self.mcstasfile in lines[0]:
                    factor = self._attached_mcstas._getScaleFactor()
                    buf = factor * np.loadtxt(lines[1:self.size[1] + 1], dtype=np.float32)
                    self._buf = buf.astype(self.image_data_type)
                    self.readresult = [self._buf.sum()]
                elif quality != LIVE:
                    raise OSError('Did not find start line: %s' % lines[0])
            except OSError:
                if quality != LIVE:
                    self.log.exception('Could not read result file', exc=1)
        else:
            self.readresult = [0]
            self._buf = np.zeros(self.size).astype(self.image_data_type)


class McStasTimer(ActiveChannel, Waitable):
    """Timer channel for McStas simulations

    This channel provides an internal neutron timer for running McStas
    simulations using `McStasImage`.
    """

    attached_devices = {
        'mcstas': Attach('McStasSimulation device', McStasSimulation),
    }

    parameters = {
        'curvalue': Param('Current value', settable=True, unit='main'),
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

    def doTime(self, preset):
        return self._attached_mcstas.preselection if self.iscontroller else 0

    def doPrepare(self):
        self._attached_mcstas._prepare()

    def doStart(self):
        self._attached_mcstas._start()

    def doStatus(self, maxage=0):
        # wait for attached mcstas simulation
        return Waitable.doStatus(self, maxage)

    def doRead(self, maxage=0):
        if self._mode != SLAVE:
            self.curvalue = self._attached_mcstas._getTime()
        return self.curvalue

    def doFinish(self):
        self._attached_mcstas._finish()

    def doStop(self):
        self.doFinish()

    def valueInfo(self):
        return Value(self.name, unit='s', type='time', fmtstr='%.3f'),


class McStasCounter(PassiveChannel, Waitable):
    """Counter channel for McStas simulations"""

    attached_devices = {
        'mcstas': Attach('McStasSimulation device', McStasSimulation),
    }

    parameters = {
        'curvalue':        Param('Current value', settable=True, unit='main'),
        'type':            Param('Counter type', type=oneof('monitor', 'counter'),
                                 mandatory=True),
        'mcstasfile':      Param('Name of the McStas data file', type=str,
                                 mandatory=True),
        'intensityfactor': Param('Factor to attenuate simulated counts, e.g. '
                                 'for beam monitors', settable=True,
                                 type=floatrange(1e-10), default=1),
    }

    parameter_overrides = {
        'unit': Override(default='cts'),
        'fmtstr': Override(default='%d'),
    }

    def doInit(self, mode):
        if mode == MASTER:
            self.curvalue = 0

    def doPrepare(self):
        self._attached_mcstas._prepare(self.mcstasfile)

    def doStart(self):
        self._attached_mcstas._start()

    def doStatus(self, maxage=0):
        # wait for attached mcstas simulation
        return Waitable.doStatus(self, maxage)

    def doRead(self, maxage=0):
        if self._mode == SLAVE:
            return self.curvalue
        try:
            with self._attached_mcstas._getDatafile(self.mcstasfile) as f:
                for line in f:
                    if line.startswith('# values:'):
                        sig = float(line.split()[2])
                        value = sig * self._attached_mcstas._getScaleFactor()
        except Exception:
            if self._attached_mcstas._getTime() > MIN_RUNTIME:
                self.log.warning('could not read result file', exc=1)
            value = 0
        self.curvalue = value * self.intensityfactor
        return self.curvalue

    def doFinish(self):
        self._attached_mcstas._finish()

    def doStop(self):
        self.doFinish()

    def valueInfo(self):
        return Value(self.name, unit='cts', errors='sqrt', type=self.type,
                     fmtstr='%d'),
