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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""
Base class for NICOS UI widgets.
"""

__version__ = "$Revision$"

from PyQt4.QtCore import SIGNAL

from nicos.core.status import OK
from nicos.protocols.daemon import DAEMON_EVENTS

# Import resources file
import nicos.guisupport.gui_rc #pylint: disable=W0612


class NicosListener(object):
    """Base mixin class for an object that can receive cache events."""

    def setSource(self, source):
        self._source = source
        self._devmap = {}
        self.devinfo = {}
        self.registerKeys()

    def registerDevice(self, dev, valueindex=-1, unit='', fmtstr=''):
        # value, valueindex, strvalue, strvalue with unit,
        # status, strvalue, fmtstr, unit, fixed, changetime
        self.devinfo[dev] = ['-', valueindex, '-', '-',
                             (OK, ''), fmtstr or '%s', unit, '', 0]
        self._devmap[self._source.register(self, dev+'/value')] = dev
        self._devmap[self._source.register(self, dev+'/status')] = dev
        self._devmap[self._source.register(self, dev+'/fixed')] = dev
        if not unit:
            self._devmap[self._source.register(self, dev+'/unit')] = dev
        if not fmtstr:
            self._devmap[self._source.register(self, dev+'/fmtstr')] = dev

    def registerKey(self, valuekey, statuskey='', valueindex=-1,
                    unit='', fmtstr=''):
        # value, valueindex, strvalue, strvalue with unit,
        # status, strvalue, fmtstr, unit, fixed, changetime
        self.devinfo[valuekey] = ['-', valueindex, '-', '-',
                                  (OK, ''), fmtstr or '%s', unit, '', 0]
        self._devmap[self._source.register(self, valuekey)] = valuekey
        if statuskey:
            self._devmap[self._source.register(self, statuskey)] = valuekey

    def registerKeys(self):
        """Register any keys that should be watched."""
        raise NotImplementedError('Implement registerKeys() in %s' %
                                  self.__class__)

    def on_keyChange(self, key, value, time, expired):
        """Default handler for changing keys.

        The default handler handles changes to registered devices.
        """
        if key not in self._devmap:
            return
        devinfo = self.devinfo[self._devmap[key]]
        if key.endswith('/status'):
            devinfo[4] = value
            devinfo[8] = time
            self.on_devStatusChange(self._devmap[key],
                                    value[0], value[1], expired)
            return
        elif key.endswith('/fixed'):
            devinfo[7] = value
            self.on_devMetaChange(self._devmap[key], devinfo[5],
                                  devinfo[6], devinfo[7])
            return
        elif key.endswith('/fmtstr'):
            devinfo[5] = value
            fvalue = devinfo[0]
            if fvalue is None:
                strvalue = '----'
            else:
                if isinstance(fvalue, list):
                    fvalue = tuple(fvalue)
                try:
                    strvalue = devinfo[5] % fvalue
                except Exception:
                    strvalue = str(fvalue)
            devinfo[3] = (strvalue + ' ' + devinfo[6]).strip()
            if devinfo[2] != strvalue:
                devinfo[2] = strvalue
                self.on_devValueChange(self._devmap[key], fvalue, strvalue,
                                       devinfo[3], expired)
            self.on_devMetaChange(self._devmap[key], devinfo[5],
                                  devinfo[6], devinfo[7])
        elif key.endswith('/unit'):
            devinfo[6] = value
            self.on_devMetaChange(self._devmap[key], devinfo[5],
                                  devinfo[6], devinfo[7])
        else:
            # apply item selection
            if devinfo[1] >= 0 and value is not None:
                try:
                    fvalue = value[devinfo[1]]
                except Exception:
                    fvalue = value
            else:
                fvalue = value
            devinfo[0] = fvalue
            if fvalue is None:
                strvalue = '----'
            else:
                if isinstance(fvalue, list):
                    fvalue = tuple(fvalue)
                try:
                    strvalue = devinfo[5] % fvalue
                except Exception:
                    strvalue = str(fvalue)
            devinfo[8] = time
            devinfo[3] = (strvalue + ' ' + devinfo[6]).strip()
            if devinfo[2] != strvalue:
                devinfo[2] = strvalue
                self.on_devValueChange(self._devmap[key], fvalue, strvalue,
                                       devinfo[3], expired)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        pass

    def on_devStatusChange(self, dev, code, status, expired):
        pass

    def on_devMetaChange(self, dev, fmtstr, unit, fixed):
        pass


class DisplayWidget(NicosListener):
    """Base mixin class for a widget that can receive cache events.

    This class can't inherit directly from QObject because Python classes
    can only derive from one PyQt base class, and that base class will be
    different for different widgets.
    """

    _source = None

    # set this to a description of the widget for the Qt designer
    designer_description = ''
    # set this to an icon name for the Qt designer
    designer_icon = None

    def __init__(self):
        self.connect(self, SIGNAL('keyChange'), self.on_keyChange)
        self.initUi()

    def initUi(self):
        """Create user interface if necessary."""

    def setConfig(self, config, labelfont, valuefont, scale):
        """Configure the widget from a dictionary (the status monitor setup)."""


class InteractiveWidget(DisplayWidget):
    """Base mixin class for a widget that can use a client object."""

    _client = None

    def __init__(self):
        DisplayWidget.__init__(self)

    def setClient(self, client):
        self._client = client
        # auto-connect client signal handlers
        for signal in DAEMON_EVENTS:
            if hasattr(self, 'on_client_' + signal):
                self.connect(self._client, SIGNAL(signal),
                             getattr(self, 'on_client_' + signal))
