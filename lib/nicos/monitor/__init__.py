#  -*- coding: utf-8 -*-
# *****************************************************************************
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
from nicos.utils import listof
from nicos.device import Param
from nicos.notify import Notifier
from nicos.status import OK, BUSY, ERROR, PAUSED, NOTREACHED
from nicos.cache.utils import OP_TELL, OP_TELLOLD, cache_load
from nicos.cache.client import BaseCacheClient


class Field(dict):
    def __hash__(self):
        return id(self)


class Monitor(BaseCacheClient):
    """
    A graphical window showing values of cache keys.

    For cache keys that correspond to NICOS devices, not only the devicevalue,
    but also the device status and unit are shown.
    """

    # server and prefix parameters come from BaseCacheClient
    parameters = {
        # XXX add more configurables: timeouts ...?
        'title':     Param('Title of status window', type=str,
                           default='Status'),
        'layout':    Param('Status monitor layout', type=listof(list),
                           mandatory=True),
        'warnings':  Param('List of warning conditions', type=listof(list),
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

    attached_devices = {
        'notifiers': [Notifier],
    }

    # methods to be implemented in concrete implementations

    def initColors(self):
        raise NotImplementedError

    def initGui(self):
        raise NotImplementedError

    def mainLoop(self):
        raise NotImplementedError

    def closeGui(self):
        raise NotImplementedError

    def switchWarnPanel(self, off=False):
        raise NotImplementedError

    def reconfigureBoxes(self):
        raise NotImplementedError

    def setLabelText(self, label, text):
        raise NotImplementedError

    def setLabelUnitText(self, label, text, unit):
        raise NotImplementedError

    def setForeColor(self, label, color):
        raise NotImplementedError

    def setBackColor(self, label, color):
        raise NotImplementedError

    def setBothColors(self, label, fore, back):
        raise NotImplementedError

    def start(self, options):
        self.log.info('monitor starting up, creating main window')

        self._fontsize = options.fontsize or self.fontsize
        self._fontsizebig = int(self._fontsize * 1.2)
        self._padding  = options.padding or self.padding
        self._geometry = options.geometry or self.geometry

        if self._geometry and self._geometry != 'fullscreen':
            try:
                self._geometry = map(int, re.match('(\d+)x(\d+)+(\d+)+(\d+)',
                                                   self._geometry).groups())
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
        # maps warning keys
        self._warnmap = {}
        # current warnings
        self._currwarnings = []
        # keys that have warnings, with info about time it occurred first
        self._haswarnings = {}
        # time when warnings were last shown/hidden?
        self._warningswitchtime = 0

        # start a thread checking for modification of the setup file
        checker = threading.Thread(target=self._checker)
        checker.setDaemon(True)
        checker.start()

        for warning in self.warnings:
            try:
                key, cond, desc, setup = warning
            except:
                key, cond, desc = warning
                setup = None
            self._warnmap[self._prefix + '/' + key] = \
                {'condition': cond, 'description': desc, 'setup': setup}

        self.initLayout()
        self.initColors()
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
        fn = path.join(session.getSetupPath(), 'monitor.py')
        if not path.isfile(fn):
            return
        mtime = path.getmtime(fn)
        while True:
            if path.getmtime(fn) != mtime:
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
        field_defaults = {
            # display/init properties
            'name': '', 'dev': '', 'width': 8, 'istext': False, 'maxlen': None,
            'min': None, 'max': None, 'unit': '', 'item': -1, 'format': '%s',
            # current values
            'value': None, 'strvalue': None, 'expired': 0, 'status': None,
            'changetime': 0, 'exptime': 0,
            # key names
            'key': '', 'statuskey': '', 'unitkey': '', 'formatkey': '',
        }

        # convert configured layout to internal structure
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
                            field = Field(field_defaults)
                            if isinstance(fielddesc, str):
                                fielddesc = {'dev': fielddesc}
                            field.update(fielddesc)
                            if not field['name']:
                                field['name'] = field['dev']
                            fields.append(field)
                        rows.append(fields)
                    block = ({'name': blockdesc[0], 'visible': True,
                              'labelframe': None, 'only': None}, rows)
                    if len(blockdesc) > 2:
                        block[0]['only'] = blockdesc[2]
                    blocks.append(block)
                columns.append(blocks)
            self._layout.append(columns)

    def updateKeymap(self, field):
        prefix = self._prefix + '/'
        # store reference from key to field for updates
        def _ref(name, key):
            field[name] = key
            self._keymap.setdefault(key, []).append(field)
        if field['dev']:
            _ref('key', prefix + field['dev'].lower() + '/value')
            _ref('statuskey', prefix + field['dev'].lower() + '/status')
            _ref('unitkey', prefix + field['dev'].lower() + '/unit')
            if field['format'] == '%s':  # explicit format has preference
                _ref('formatkey', prefix + field['dev'].lower() + '/fmtstr')
        else:
            _ref('key', prefix + field['key'])
            if field['statuskey']:
                _ref('statuskey', prefix + field['statuskey'])
            if field['unitkey']:
                _ref('unitkey', prefix + field['unitkey'])
            if field['formatkey']:
                _ref('formatkey', prefix + field['formatkey'])

    # called between connection attempts
    def _wait_retry(self):
        self.setLabelText(self._timelabel,
                          'Disconnected (%s)' % strftime('%d.%m.%Y %H:%M:%S'))
        sleep(1)

    # called while waiting for data
    def _wait_data(self):
        # update current time
        self.setLabelText(self._timelabel, '%s (%s)' %
                          (self.title, strftime('%d.%m.%Y %H:%M:%S')))

        # adjust the colors of status displays
        newwatch = set()
        for field in self._watch:
            vlabel, status = field['valuelabel'], field['status']
            value = field['value']

            # set name label background color: determined by the value limits

            if field['min'] is not None and value < field['min']:
                self.setBackColor(field['namelabel'], self._red)
            elif field['max'] is not None and value > field['max']:
                self.setBackColor(field['namelabel'], self._red)
            else:
                self.setBackColor(field['namelabel'], self._bgcolor)

            # set the foreground color: determined by the status

            time = currenttime()
            valueage = time - field['changetime']
            if valueage < 2:
                self.setForeColor(vlabel, self._yellow)
                newwatch.add(field)
            else:
                # if we have a status
                try:
                    const = status[0]
                except (TypeError, ValueError):
                    const = status
                if const == OK:
                    self.setForeColor(vlabel, self._green)
                elif const in (BUSY, PAUSED):
                    self.setForeColor(vlabel, self._yellow)
                elif const in (ERROR, NOTREACHED):
                    self.setForeColor(vlabel, self._red)
                else:
                    self.setForeColor(vlabel, self._white)

            # set the background color: determined by the value's up-to-dateness

            if value is None or \
                (field['expired'] and time - field['exptime'] > 0.7):
                self.setBackColor(vlabel, self._gray)
            else:
                self.setBackColor(vlabel, self._black)
        self._watch = newwatch
        #self.log.debug('newwatch has %s items' % len(newwatch))

        # check if warnings need to be shown
        if self._currwarnings:
            if currenttime() > self._warningswitchtime + 10:
                self.switchWarnPanel()
                self._warningswitchtime = currenttime()

    # called to handle an incoming protocol message
    def _handle_msg(self, time, ttl, tsop, key, op, value):
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

        #self.log.debug('processing %s' % [time, ttl, key, op, value])

        if key == self._prefix + '/session/mastersetup':
            self._setups = set(value)
            # reconfigure displayed blocks
            self.reconfigureBoxes()
            self.log.info('reconfigured display for setups %s'
                           % ', '.join(self._setups))

        expired = value is None or op == OP_TELLOLD

        if key in self._warnmap and not expired:
            info = self._warnmap[key]
            try:
                condvalue = eval('__v__ ' + info['condition'],
                                 {'__v__': value})
            except Exception:
                self.log.warning('error evaluating %r warning condition'
                                  % key, exc=1)
            else:
                self._process_warnings(key, info, condvalue)

        # now check if we need to update something
        fields = self._keymap.get(key, [])
        for field in fields:
            self._watch.add(field)
            if key == field['key']:
                field['expired'] = expired
                if expired:
                    field['exptime'] = time
                if field['item'] >= 0 and value is not None:
                    fvalue = value[field['item']]
                else:
                    fvalue = value
                if value is None:
                    strvalue = '----'
                else:
                    try:
                        strvalue = field['format'] % fvalue
                    except Exception, e:
                        strvalue = str(fvalue)
                if field['strvalue'] != strvalue:
                    field['changetime'] = time
                field['strvalue'] = strvalue
                field['value'] = value
                self.setLabelText(field['valuelabel'], strvalue[:field['maxlen']])
            elif key == field['statuskey']:
                if value is not None:
                    if field['status'] != value:
                        field['changetime'] = time
                    field['status'] = value
            elif key == field['unitkey']:
                if value is not None:
                    field['unit'] = value
                    self.setLabelUnitText(field['namelabel'],
                                          field['name'], value)
            elif key == field['formatkey']:
                if value is not None:
                    field['format'] = value
                if field['value'] is not None and field['item'] < 0:
                    try:
                        self.setLabelText(field['valuelabel'], field['format'] %
                                          field['value'])
                    except Exception:
                        self.setLabelText(field['valuelabel'], str(field['value']))

    def _process_warnings(self, key, info, value):
        if info['setup']:
            value &= info['setup'] in self._setups
        if not value:
            if key not in self._haswarnings:
                return
            self._currwarnings.remove(self._haswarnings.pop(key))
        elif value:
            if key in self._haswarnings:
                return
            warning_desc = strftime('%Y-%m-%d %H:%M') + ' -- ' + \
                           info['description']
            self._currwarnings.append((key, warning_desc))
            self._haswarnings[key] = (key, warning_desc)
            for notifier in self._adevs['notifiers']:
                notifier.send('New warning from ' + self.title,
                              warning_desc)
        if self._currwarnings:
            self.setBothColors(self._timelabel, self._black, self._red)
            self.setLabelText(self._warnlabel,
                              '\n'.join(w[1] for w in self._currwarnings))
        else:
            self.setBothColors(self._timelabel, self._gray, self._bgcolor)
            self.switchWarnPanel(off=True)
