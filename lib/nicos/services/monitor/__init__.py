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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Base class for instrument monitors."""

__version__ = "$Revision$"

import os
import re
import sys
import time
import threading
from os import path
from time import sleep, strftime, time as currenttime

from nicos import session
from nicos.core import listof, Param, Override
from nicos.core.status import BUSY
from nicos.protocols.cache import OP_TELL, OP_TELLOLD, OP_SUBSCRIBE, cache_load
from nicos.devices.cacheclient import BaseCacheClient


class Field(object):
    # what to display
    key = ''         # main key (displayed value)
    item = -1        # item to display of value, -1 means whole value
    name = ''        # name of value
    statuskey = ''   # key for value status
    unitkey = ''     # key for value unit
    formatkey = ''   # key for value format string
    fixedkey = ''    # key for value fixed-ness

    # how to display it
    widget = ''      # which widget to use (empty for default)
    width = 8        # width of the widget (in characters, usually)
    height = 8       # height of the widget
    istext = False   # true if not a number but plain text
    maxlen = None    # max length of displayed text before cutoff
    min = None       # minimum value
    max = None       # maximum value; if out of range display in red

    # current values
    value = None     # current value
    strvalue = None  # current value as string
    status = None    # current status
    expired = False  # is value expired?
    exptime = 0      # time when value expired
    changetime = 0   # time of last change to value
    fixed = ''       # current fixed status
    unit = ''        # unit for display
    format = '%s'    # format string for display

    # for plots
    plot = None           # which plot to plot this value in
    plotinterval = 3600   # time span of plot

    def __init__(self, prefix, desc):
        if isinstance(desc, str):
            desc = {'dev': desc}
        if 'dev' in desc:
            dev = desc.pop('dev')
            if 'name' not in desc:
                desc['name'] = dev
            desc['key'] =       dev + '/value'
            desc['statuskey'] = dev + '/status'
            desc['fixedkey'] =  dev + '/fixed'
            if 'unit' not in desc:
                desc['unitkey'] = dev + '/unit'
            if 'format' not in desc:
                desc['formatkey'] = dev + '/fmtstr'
        for kn in ('key', 'statuskey', 'fixedkey', 'unitkey', 'formatkey'):
            if kn in desc:
                desc[kn] = (prefix + desc[kn]).lower()
        if 'name' not in desc:
            desc['name'] = desc['key']
        self.__dict__.update(desc)


class Monitor(BaseCacheClient):
    """
    A graphical window showing values of cache keys.

    For cache keys that correspond to NICOS devices, not only the devicevalue,
    but also the device status and unit are shown.
    """

    # server and prefix parameters come from BaseCacheClient
    parameters = {
        'title':     Param('Title of status window', type=str,
                           default='Status'),
        'layout':    Param('Status monitor layout', type=listof(list),
                           mandatory=True),
        'font':      Param('Font name for the window', type=str,
                           default='Luxi Sans'),
        'valuefont': Param('Font name for the value displays', type=str),
        'fontsize':  Param('Basic font size', type=int, default=12,
                           settable=True),
        'padding':   Param('Padding for the display fields', type=int,
                           default=2, settable=True),
        'geometry':  Param('Geometry for status window', type=str,
                           settable=True),
        'resizable': Param('Whether the window is resizable', type=bool,
                           default=True),
    }

    parameter_overrides = {
        'prefix':    Override(mandatory=False, default='nicos/'),
    }

    # methods to be implemented in concrete implementations

    def initGui(self):
        raise NotImplementedError('Implement initGui() in subclasses')

    def mainLoop(self):
        raise NotImplementedError('Implement mainLoop() in subclasses')

    def closeGui(self):
        raise NotImplementedError('Implement closeGui() in subclasses')

    def signal(self, field, signal, *args):
        raise NotImplementedError('Implement signal() in subclasses')

    def switchWarnPanel(self, off=False):
        raise NotImplementedError('Implement switchWarnPanel() in subclasses')

    def reconfigureBoxes(self):
        raise NotImplementedError('Implement reconfigureBoxes() in subclasses')

    def updateTitle(self, text):
        raise NotImplementedError('Implement updateTitle() in subclasses')

    def start(self, options):
        self.log.info('monitor starting up, creating main window')

        self._fontsize = options.fontsize or self.fontsize
        self._fontsizebig = int(self._fontsize * 1.2)
        self._padding  = options.padding or self.padding
        self._geometry = options.geometry or self.geometry

        if self._geometry and self._geometry != 'fullscreen':
            try:
                m = re.match(r'(?:(\d+)x(\d+))?\+(\d+)+(\d+)', self._geometry)
                w, h, x, y = m.groups()
                if w is None:
                    w = h = 0
                else:
                    w, h = int(w), int(h)
                x, y = int(x), int(y)
                self._geometry = (w, h, x, y)
            except Exception:
                self.log.warning('invalid geometry %s' % self._geometry)
                self._geometry = None

        # timeout for select() call
        self._selecttimeout = 0.2
        # list of fields to watch
        self._watch = set()
        # maps keys to field-dicts defined in self.layout (see above)
        self._keymap = {}
        # maps "only" entries to block boxes to hide
        self._onlymap = {}
        # remembers loaded setups
        self._setups = set()
        # master active?
        self._masteractive = False
        # currently shown warnings
        self._currwarnings = ''
        # time when warnings were last shown/hidden?
        self._warningswitchtime = 0

        # start a thread checking for modification of the setup file
        checker = threading.Thread(target=self._checker, name='refresh checker')
        checker.setDaemon(True)
        checker.start()

        self.initLayout()
        self.initGui()

        # now start the worker thread
        self._worker.start()

        self.log.info('starting main loop')
        try:
            self.mainLoop()
        except KeyboardInterrupt:
            pass
        self._stoprequest = True

    def _checker(self):
        setupname = session.explicit_setups[0]
        fn = session._setup_info[setupname]['filename']
        if not path.isfile(fn):
            self.log.warning('setup watcher could not find %s.py' % setupname)
            return
        mtime = path.getmtime(fn)
        while True:
            if path.getmtime(fn) != mtime:
                self.log.info('setup file changed; restarting monitor process')
                os.execv(sys.executable, [sys.executable] + sys.argv)
                return
            time.sleep(1)

    def wait(self):
        self.log.info('monitor quitting')
        self._worker.join()
        self.log.info('done')

    def quit(self, *ignored):
        self.closeGui()
        self._stoprequest = True

    def initLayout(self):
        # convert configured layout to internal structure and register keys for
        # further processing
        self._layout = []
        for superrowdesc in self.layout:
            columns = []
            for columndesc in superrowdesc:
                blocks = []
                for blockdesc in columndesc:
                    rows = []
                    for rowdesc in blockdesc[1]:
                        if rowdesc == '---':
                            rows.append(None)
                            continue
                        fields = []
                        for fielddesc in rowdesc:
                            field = Field(self._prefix, fielddesc)
                            fields.append(field)
                            self.updateKeymap(field)
                        rows.append(fields)
                    block = ({'name': blockdesc[0], 'visible': True,
                              'only': None}, rows)
                    if len(blockdesc) > 2:
                        block[0]['only'] = blockdesc[2]
                    blocks.append(block)
                columns.append(blocks)
            self._layout.append(columns)

    def updateKeymap(self, field):
        # store reference from key to field for updates
        for kn in ('key', 'statuskey', 'fixedkey', 'unitkey', 'formatkey'):
            key = getattr(field, kn)
            if key:
                self._keymap.setdefault(key, []).append(field)

    def _connect_action(self):
        BaseCacheClient._connect_action(self)
        # also subscribe to all watchdog events
        self._socket.sendall('@watchdog/%s\n' % OP_SUBSCRIBE)

    # called between connection attempts
    def _wait_retry(self):
        self.updateTitle('Disconnected (%s)' % strftime('%d.%m.%Y %H:%M:%S'))
        sleep(1)

    # called while waiting for data
    def _wait_data(self):
        # update current time
        self.updateTitle('%s (%s)%s' %
                         (self.title, strftime('%d.%m.%Y %H:%M:%S'),
                          '' if self._masteractive else ', no master active'))

        # adjust the colors of status displays
        newwatch = set()
        for field in self._watch:
            status = field.status
            value = field.value

            # determined if value limits are hit (typically displayed as a red
            # background color)

            if field.min is not None and value < field.min:
                self.signal(field, 'rangeChanged', -1)
            elif field.max is not None and value > field.max:
                self.signal(field, 'rangeChanged', +1)
            else:
                self.signal(field, 'rangeChanged', 0)

            # determine the status (typically displayed as the color of the
            # displayed value)

            time = currenttime()
            valueage = time - field.changetime
            if valueage < 2:
                self.signal(field, 'statusChanged', BUSY)
                newwatch.add(field)
            else:
                # if we have a status
                try:
                    const = status[0]
                except (TypeError, ValueError):
                    const = status
                if const is not None:
                    self.signal(field, 'statusChanged', const)

            # determine by the value's up-to-dateness (typically displayed as
            # a background color of the value)

            if value is None:
                self.signal(field, 'expireChanged', True)
            elif field.expired:
                if time - field.exptime > 0.7:
                    self.signal(field, 'expireChanged', True)
                else:
                    self.signal(field, 'expireChanged', False)
                    newwatch.add(field)
            else:
                self.signal(field, 'expireChanged', False)
        self._watch = newwatch
        #self.log.debug('newwatch has %s items' % len(newwatch))

        # check if warnings need to be shown
        if self._currwarnings:
            if currenttime() > self._warningswitchtime + 10:
                self.switchWarnPanel()
                self._warningswitchtime = currenttime()

    # called to handle an incoming protocol message
    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if op not in (OP_TELL, OP_TELLOLD):
            return
        try:
            time = float(time)
        except (ValueError, TypeError):
            time = currenttime()
        try:
            value = cache_load(value)
        except ValueError:
            pass

        if key == 'watchdog/warnings':
            self._process_warnings(value)
            return

        #self.log.debug('processing %s' % [time, ttl, key, op, value])

        if key == self._prefix + 'session/master':
            self._masteractive = value and op != OP_TELLOLD

        if key == self._prefix + 'session/mastersetup':
            self._setups = set(value)
            # reconfigure displayed blocks
            self.reconfigureBoxes()
            self.log.info('reconfigured display for setups %s'
                           % ', '.join(self._setups))

        expired = value is None or op == OP_TELLOLD

        # now check if we need to update something
        fields = self._keymap.get(key, [])
        for field in fields:
            self._watch.add(field)
            if key == field.key:
                field.expired = expired
                if expired:
                    field.exptime = time
                if field.item >= 0 and value is not None:
                    try:
                        fvalue = value[field.item]
                    except Exception:
                        fvalue = value
                else:
                    fvalue = value
                if value is None:
                    strvalue = '----'
                else:
                    if isinstance(fvalue, list):
                        fvalue = tuple(fvalue)
                    try:
                        strvalue = field.format % fvalue
                    except Exception:
                        strvalue = str(fvalue)
                if field.strvalue != strvalue:
                    field.changetime = time
                field.strvalue = strvalue
                field.value = value
                self.signal(field, 'newValue', time, value, strvalue)
            elif key == field.formatkey:
                if value is not None:
                    field.format = value
                    fvalue = field.value
                    if field.item >= 0 and fvalue is not None:
                        try:
                            fvalue = fvalue[field.item]
                        except Exception:
                            pass
                    if fvalue is None:
                        strvalue = '----'
                    else:
                        if isinstance(fvalue, list):
                            fvalue = tuple(fvalue)
                        try:
                            strvalue = field.format % fvalue
                        except Exception:
                            strvalue = str(fvalue)
                    self.signal(field, 'newValue', time, field.value, strvalue)
            elif key == field.statuskey:
                if value is not None:
                    if field.status != value:
                        field.changetime = time
                    field.status = value
            elif key == field.unitkey:
                if value is not None:
                    if field.item >= 0:
                        try:
                            value = value.split()[field.item]
                        except Exception:
                            pass
                    field.unit = value
                    self.signal(field, 'metaChanged')
            elif key == field.fixedkey:
                field.fixed = ' (F)' if value else ''
                self.signal(field, 'metaChanged')

    def _process_warnings(self, warnings):
        #self.log.debug('new warnings: %s' % warnings)
        self._currwarnings = warnings
        if not warnings:
            self.switchWarnPanel(off=True)
