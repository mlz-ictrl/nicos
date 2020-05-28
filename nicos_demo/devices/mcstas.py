#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""detector based on McSTAS simulation."""

from __future__ import absolute_import, division, print_function

import os
import shutil
from os import path
from signal import SIGTERM, SIGUSR2
from subprocess import PIPE

import numpy as np

from nicos import session
from nicos.core import ArrayDesc, Param, Value, floatrange, intrange, status, \
    tupleof
from nicos.core.constants import LIVE
from nicos.core.errors import HardwareError
from nicos.devices.generic import ImageChannelMixin, PassiveChannel
from nicos.utils import createSubprocess, createThread


class McStasImage(ImageChannelMixin, PassiveChannel):
    """Image channel based on McSTAS simulation."""

    _mythread = None

    _process = None

    parameters = {
        'size': Param('Detector size in pixels (x, y)',
                      settable=False,
                      type=tupleof(intrange(1, 8192), intrange(1, 8192)),
                      default=(1, 1),
                      ),
        'mcstasprog': Param('Name of the McStas simulation executable',
                            type=str, settable=False),
        'mcstasdir': Param('Directory where McStas stores results',
                           type=str, default='singlecount', settable=False),
        'mcstasfile': Param('Name of the McStas data file',
                            type=str, settable=False),
        'writedelay': Param('Time to wait after initiating result writing',
                            settable=False, type=floatrange(0.1), default=0.1),
    }

    def doInit(self, mode):
        self.arraydesc = ArrayDesc(self.name, self.size, '<u4')
        self._workdir = os.getcwd()

    def doReadArray(self, quality):
        self.log.debug('quality: %s', quality)
        if quality == LIVE:
            self._send_signal(SIGUSR2)
        self._readpsd(
            path.join(self._workdir, self.mcstasdir), quality == LIVE)
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
        self.readresult = [self._buf.sum()]

    def valueInfo(self):
        return (Value(self.name + '.sum', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'),)

    def doStart(self):
        self._mythread = createThread('detector %s' % self, self._run)

    def doStatus(self, maxage=0):
        if self._mythread and self._mythread.is_alive():
            return status.BUSY, 'busy'
        return status.OK, 'idle'

    def doFinish(self):
        self.log.debug('finish')
        self._send_signal(SIGTERM)

    def _send_signal(self, sig):
        if self._process:
            self._process.send_signal(sig)
            # Give external process time to write all data to disc(file)
            session.delay(self.writedelay)

    def _run(self):
        """Run McStas simulation executable.

        The current settings of the instrument parameters will be transferred
        to it.
        """
        os.chdir(self._workdir)
        try:
            shutil.rmtree(self.mcstasdir)
        except (IOError, OSError):
            self.log.info('could not remove old data')
        command = '%s -n 1e8 -d %s %s' % (
            self.mcstasprog, self.mcstasdir, self._mcstas_params)
        self.log.debug('run %s', command)
        try:
            self._process = createSubprocess(command.split(), stdout=PIPE,
                                             stderr=PIPE)
            out, err = self._process.communicate()
            if out:
                for line in out.split(b'\n'):
                    self.log.debug('McStas output: %s', line)
            if err:
                self.log.warning('McStas found some problems: %s', err)
        except OSError as e:
            self.log.error('Execution failed: %s', e)
        os.chdir(self._workdir)
        self._process = None

    def _readpsd(self, somedir, ignore_error=False):
        try:
            with open(path.join(somedir, self.mcstasfile), 'r') as f:
                lines = f.readlines()[-(self.size[1] + 1):]
            if lines[0].startswith('# Events'):
                for i, line in enumerate(lines[1:]):
                    items = line.strip('\n').strip(' ').split(' ')
                    if items and items[0] != '#' and i < self.size[1]:
                        self._buf[i] = list(map(int, items))
            else:
                raise HardwareError('Did not found start line: %s' % lines[0])
        except IOError:
            if not ignore_error:
                self.log.error('Could not read result file')
        self._buf = np.around(self._buf)
        self.readresult = [self._buf.sum()]
