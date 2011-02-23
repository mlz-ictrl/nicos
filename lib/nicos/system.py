#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""
NICOS system device.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicos import session
from nicos.data import DataSink
from nicos.utils import sessionInfo
from nicos.device import Device, Param
from nicos.errors import ModeError, UsageError
from nicos.notify import Notifier
from nicos.instrument import Instrument
from nicos.experiment import Experiment
from nicos.cache.client import CacheClient, CacheLockError


EXECUTIONMODES = ['master', 'slave', 'simulation', 'maintenance']


class System(Device):
    """A special singleton device that serves for global configuration of
    the NICOS system.
    """

    parameters = {
        'datapath': Param('Path for data files', type=str, mandatory=True),
    }

    attached_devices = {
        'cache': CacheClient,
        'datasinks': [DataSink],
        'instrument': Instrument,
        'experiment': Experiment,
        'notifiers': [Notifier],
    }

    def __repr__(self):
        return '<NICOS System (%s mode)>' % self._mode

    def __init__(self, name, **config):
        # need to pre-set this to avoid bootstrapping issue
        self._mode = 'slave'
        Device.__init__(self, name, **config)

    def doShutdown(self):
        if self.mode == 'master':
            self._cache._ismaster = False
            self._cache.unlock('master')

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
            try:
                self._cache.lock('master')
            except CacheLockError, err:
                raise ModeError('another master is already active: %s' %
                                sessionInfo(err.locked_by))
            else:
                self._cache._ismaster = True
        elif mode in ['slave', 'maintenance']:
            # switching from master to slave or to maintenance
            if not self._cache:
                raise ModeError('no cache present, cannot release master lock')
            self._cache._ismaster = False
            self._cache.unlock('master')
        for dev in session.devices.itervalues():
            dev._setMode(mode)
        if mode == 'simulation':
            self.cache.doShutdown()
        self.printinfo('switched to %s mode' % mode)
        session.resetPrompt()

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

    def notifyConditionally(self, runtime, subject, body, what=None, short=None):
        """Send a notification if the current runtime exceeds the configured
        minimum runtimer for notifications."""
        for notifier in self._adevs['notifiers']:
            notifier.sendConditionally(runtime, subject, body, what, short)

    def notify(self, subject, body, what=None, short=None):
        """Send a notification unconditionally."""
        for notifier in self._adevs['notifiers']:
            notifier.send(subject, body, what, short)
