#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

"""VTREFF detector image based on McSTAS simulation."""

from __future__ import absolute_import, division, print_function

import os
import shutil
import subprocess
from os import path

import numpy as np

from nicos.core import ArrayDesc, Attach, Param, Readable, Value, intrange, \
    status, tupleof
from nicos.devices.generic import ImageChannelMixin, PassiveChannel, Slit
from nicos.utils import createThread

from nicos_mlz.treff.devices import MirrorSample


class McStasImage(ImageChannelMixin, PassiveChannel):

    _mythread = None

    parameters = {
        'size': Param('Detector size in pixels (x, y)',
                      settable=False,
                      type=tupleof(intrange(1, 1024), intrange(1, 1024)),
                      default=(256, 256),
                      ),
    }

    attached_devices = {
        'sample': Attach('Mirror sample', MirrorSample),
        's1': Attach('Slit 1', Slit),
        's2': Attach('Slit 2', Slit),
        'sample_x': Attach('Sample position x', Readable),
        'sample_y': Attach('Sample position y', Readable),
        'sample_z': Attach('Sample position z', Readable),
        'beamstop': Attach('Beam stop positon', Readable),
        'omega': Attach('Sample omega rotation', Readable),
        'chi': Attach('Sample chi rotation', Readable),
        'phi': Attach('Sample phi rotation', Readable),
        'detarm': Attach('Position detector arm', Readable),
    }

    def doInit(self, mode):
        self.arraydesc = ArrayDesc(self.name, self.size, '<u4')
        self._workdir = os.getcwd()

    def doReadArray(self, quality):
        return self._buf

    def doPrepare(self):
        sample = self._attached_sample
        params = []
        params.append('s1_width=%s' % self._attached_s1.width.read(0))
        params.append('s1_height=%s' % self._attached_s1.height.read(0))
        params.append('s2_width=%s' % self._attached_s2.width.read(0))
        params.append('s2_height=%s' % self._attached_s2.height.read(0))
        params.append('sample_x=%s' % self._attached_sample_x.read(0))
        sample_y = self._attached_sample_y
        params.append('sample_y=%s' % (sample_y.read(0) + sample_y.offset +
                                       sample._misalignments['sample_y']))
        params.append('sample_z=%s' % self._attached_sample_z.read(0))
        params.append('beamstop_pos=%s' % self._attached_beamstop.read(0))
        omega = self._attached_omega
        params.append('omega=%s' % (
            omega.read(0) + omega.offset + sample._misalignments['omega']))
        chi = self._attached_chi
        params.append('chi=%s' % (
            chi.read(0) + chi.offset + sample._misalignments['chi']))
        params.append('phi=%s' % self._attached_phi.read(0))
        detarm = self._attached_detarm
        params.append('detarm=%s' % (
            detarm.read(0) + detarm.offset + sample._misalignments['detarm']))
        params.append('mirror_length=%s' % self._attached_sample.length)
        params.append('mirror_thickness=%s' % self._attached_sample.thickness)
        params.append('mirror_height=%s' % self._attached_sample.height)
        params.append('mirror_m=%s' % self._attached_sample.m)
        params.append('mirror_alfa=%s' % self._attached_sample.alfa)
        params.append('mirror_wav=%s' % self._attached_sample.waviness)
        if self._attached_sample.rflfile:
            params.append('rflfile=%s' % self._attached_sample.rflfile)
        else:
            params.append('rflfile=0')

        self._mcstas_params = ' '.join(params)
        self.log.debug('McStas parameters: %s', self._mcstas_params)
        self._buf = np.zeros(self.size)
        self.readresult = [self._buf.sum()]

    def valueInfo(self):
        return Value(self.name + '.sum', unit='cts', type='counter',
                     errors='sqrt', fmtstr='%d'),

    def doStart(self):
        self._mythread = createThread('detector %s' % self, self._run)

    def doStatus(self, maxage=0):
        if self._mythread and self._mythread.is_alive():
            return status.BUSY, 'busy'
        return status.OK, 'idle'

    def _run(self):
        """
        runs treff_fast with current settings of the instrument parameters
        """
        mcstasdir = 'singlecount'
        os.chdir(self._workdir)
        try:
            shutil.rmtree(mcstasdir)
        except (IOError, OSError):
            self.log.info('could not remove old data')
        command = 'treff_fast -n 100000 -d %s %s' % (
            mcstasdir, self._mcstas_params)
        self.log.debug('run %s', command)
        try:
            retcode = subprocess.call(command, shell=True)
            if retcode < 0:
                self.log.error("McStas was terminated by signal: %d", -retcode)
        except OSError as e:
            self.log.error('Execution failed: %s', e)
        self._readpsd(path.join(self._workdir, mcstasdir))
        self.readresult = [self._buf.sum()]
        os.chdir(self._workdir)

    def _readpsd(self, somedir):
        try:
            with open(path.join(somedir, 'PSD_TREFF_total.psd'), 'r') as f:
                i = 0
                while True:
                    line = f.readline()
                    if not line:
                        return
                    items = line.strip('\n').strip(' ').split(' ')
                    if items and items[0] != '#' and i < 256:
                        self._buf[i] = list(map(float, items))
                        i += 1
        except IOError:
            self.log.error('Could not read result file')
        self._buf = np.around(self._buf)
