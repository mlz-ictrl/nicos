#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS System device
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""
NICOS system device.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time

from nicm import nicos
from nicm.data import DataSink
from nicm.utils import sessionInfo
from nicm.device import Device, Param
from nicm.errors import ModeError, UsageError
from nicm.instrument import Instrument
from nicm.experiment import Experiment
from nicm.cache.client import CacheClient


EXECUTIONMODES = ['master', 'slave', 'simulation', 'maintenance']


class System(Device):
    """A special singleton device that serves for global configuration of
    the NICM system.
    """

    parameters = {
        'logpath': Param('Path for logfiles', type=str, mandatory=True),
        'datapath': Param('Path for data files', type=str, mandatory=True),
    }

    attached_devices = {
        'cache': CacheClient,
        'datasinks': [DataSink],
        'instrument': Instrument,
        'experiment': Experiment,
    }

    def __repr__(self):
        return '<NICM System (%s mode)>' % self._mode

    def __init__(self, name, **config):
        # need to pre-set this to avoid bootstrapping issue
        self._mode = 'slave'
        Device.__init__(self, name, **config)

    def doInit(self):
        try:
            self.setMode('master')
        except ModeError:
            self.printinfo('could not enter master mode; remaining slave')

    @property
    def cache(self):
        return self._adevs['cache']

    @property
    def instrument(self):
        return self._adevs['instrument']

    @property
    def experiment(self):
        return self._adevs['experiment']

    @property
    def mode(self):
        return self._mode

    def setMode(self, mode):
        mode = mode.lower()
        oldmode = self.mode
        if mode == oldmode:
            return
        if mode not in EXECUTIONMODES:
            raise UsageError('mode %r does not exist' % mode)
        if oldmode in ['simulation', 'maintenance']:
            # no way to switch back from special modes
            raise ModeError('switching from %s mode is not supported' % oldmode)
        if mode == 'master':
            # switching from slave to master
            if not self._cache:
                raise ModeError('no cache present, cannot get master lock')
            self.printinfo('checking master status...')
            entry = self._cache.getMaster()
            if entry:
                if entry[0] != nicos.sessionid:
                    if entry[1] + entry[2] >= time.time():
                        raise ModeError('another master is already active: %s' %
                                        sessionInfo(entry[0]))
            self._cache.setMaster()
        elif mode in ['slave', 'maintenance']:
            # switching from master to slave or to maintenance
            if not self._cache:
                raise ModeError('no cache present, cannot get master lock')
            self._cache._ismaster = False
        for dev in nicos.devices.itervalues():
            dev._setMode(mode)
        if mode == 'simulation':
            self.cache.doShutdown()
        self.printinfo('switched to %s mode' % mode)
        nicos.resetPrompt()

    def getSinks(self, scantype=None):
        if scantype is None:
            sinks = self._adevs['datasinks']
        else:
            sinks = [sink for sink in self._adevs['datasinks']
                     if not sink.scantypes or scantype in sink.scantypes]
        if self._mode == 'simulation':
            sinks = [sink for sink in sinks if sink.activeInSimulation]
        return sinks

    def doWriteDatapath(self, value):
        for sink in self._adevs['datasinks']:
            sink.setDatapath(value)
