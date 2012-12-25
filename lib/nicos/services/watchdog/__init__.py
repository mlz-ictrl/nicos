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

"""The NICOS watchdog daemon."""

__version__ = "$Revision$"

import subprocess
from os import path
from time import time as currenttime, strftime

import ast
from ordereddict import OrderedDict

from nicos import session
from nicos.core import Param, Override, listof, dictof, anytype
from nicos.protocols.cache import OP_TELL, OP_TELLOLD, cache_dump, cache_load
from nicos.devices.notifiers import Notifier
from nicos.devices.cacheclient import BaseCacheClient


class LCDict(dict):
    """Dictionary with automatic lower-casing of keys."""
    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())
    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.lower(), value)
    def __delitem__(self, key, value):
        return dict.__delitem__(self, key.lower())


class Entry(object):
    id = None
    setup = ''
    condition = ''
    gracetime = 0
    message = ''
    priority = 1
    action = ''

    def __init__(self, values):
        self.__dict__.update(values)


class Watchdog(BaseCacheClient):

    parameters = {
        'watch':   Param('The configuration of things to watch',
                         type=listof(dictof(str, anytype))),
    }

    parameter_overrides = {
        'prefix':  Override(mandatory=False, default='nicos/'),
    }

    attached_devices = {
        'notifiers_1': ([Notifier], 'A list of notifiers used for warning '
                        'messages of priority 1'),
        'notifiers_2': ([Notifier], 'A list of notifiers used for warning '
                        'messages of priority 2'),
    }

    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        # current setups
        self._setups = set()
        # mapping entry ids to entrys
        self._entries = {}
        # mapping cache keys to entry dicts that check this key
        self._keymap = {}
        # mapping entry ids to entrys for which one or more keys have expired
        self._watch_expired = {}
        # mapping entry ids to entrys that are in grace time period
        self._watch_grace = {}
        # current warnings: mapping entry ids to the string description
        self._warnings = OrderedDict()
        # dictionary of keys used to evaluate the conditions
        self._keydict = LCDict()

        # process watchlist entries
        for i, entryd in enumerate(self.watch):
            # some values cannot have defaults
            if not entryd['condition']:
                self.log.warning('entry %s missing "condition" key' % entryd)
                continue
            if not entryd['message']:
                self.log.warning('entry %s missing "message" key' % entryd)
                continue
            entry = Entry(entryd)
            entry.id = i
            self._entries[i] = entry
            # find all cache keys that the condition evaluates, to get a mapping
            # of cache key -> interesting watchlist entries
            cond_parse = ast.parse(entry.condition)
            for node in ast.walk(cond_parse):
                if isinstance(node, ast.Name):
                    key = node.id.replace('_', '/').lower()
                    self._keymap[self._prefix + key] = entry

    def _put_message(self, type, message, timestamp=True):
        if timestamp:
            message = [currenttime(), message]
        self._queue.put('watchdog/%s%s%s\n' % (type, OP_TELL,
                                               cache_dump(message)))

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if key == self._prefix + 'session/mastersetup':
            self._setups = set(cache_load(value))
        # do we care for this key?
        if key not in self._keymap:
            return
        # put key in db
        self._keydict[key[len(self._prefix):].replace('/', '_').lower()] = \
            cache_load(value)
        entry = self._keymap[key]
        eid = entry.id
        # is the necessary setup loaded?
        if entry.setup and entry.setup not in self._setups:
            return
        # is it a new value or an expiration?
        if op == OP_TELLOLD or value is None:
            # add it to the watchlist, and if the value doesn't come back in 10
            # minutes, we warn
            self._watch_expired[eid] = [currenttime() + 600]
            return
        if op == OP_TELL:
            # remove from expiration watchlist
            self._watch_expired.pop(eid, None)
            try:
                value = eval(entry.condition, self._keydict)
            except Exception:
                self.log.warning('error evaluating %r warning condition' % key,
                                 exc=1)
                return
            if entry.gracetime and value and eid not in self._watch_grace:
                self.log.info('condition %r triggered, awaiting grace time'
                              % entry.condition)
                self._watch_grace[eid] = [currenttime() + entry.gracetime,
                                          value]
            else:
                self._process_warning(entry, value)

    def _process_warning(self, entry, value):
        eid = entry.id
        if not value:
            if eid in self._watch_grace:
                self.log.info('condition %r went normal during gracetime' %
                              entry.condition)
                del self._watch_grace[eid]
            if eid not in self._warnings:
                return
            self.log.info('condition %r normal again' % entry.condition)
            del self._warnings[eid]
        else:
            if eid in self._warnings:
                # warning has already been given
                return
            self.log.info('got a new warning for %r' % entry.condition)
            self._put_message('warning', entry.message)
            warning_desc = strftime('%Y-%m-%d %H:%M') + ' -- ' + entry.message
            if entry.action:
                warning_desc += ' -- executing %r' % entry.action
            self._warnings[eid] = warning_desc
            for notifier in self._adevs['notifiers_%d' % entry.priority]:
                notifier.send('New warning from NICOS', warning_desc)
            if entry.action:
                self._put_message('action', entry.action)
                self._spawn_action(entry.action)
        self.log.debug('new warnings: %s' % self._warnings)
        self._put_message('warnings', '\n'.join(self._warnings.values()),
                          timestamp=False)

    def _wait_data(self):
        t = currenttime()
        # don't use iteritems() here, the dict is changed in the loop
        for eid, wentry in self._watch_expired.items():
            if t > wentry[0]:
                # warn that we cannot check the condition anymore
                del self._watch_expired[eid]
                msg = ('current value missing for condition %r, '
                       'cannot check watchdog condition' %
                       self._entries[eid].condition)
                self._put_message('warning', msg)
                for notifier in self._adevs['notifiers_1']:
                    notifier.send('New warning from NICOS', msg)
        for eid, wentry in self._watch_grace.items():
            if t > wentry[0]:
                # grace time expired
                del self._watch_grace[eid]
                self._process_warning(self._entries[eid], wentry[1])

    def _spawn_action(self, action):
        self.log.warning('will execute action %r' % action)
        script = path.join(session.config.control_path, 'bin', 'nicos-script')
        subprocess.Popen([script, '-M', '-A', 'watchdog-action',
                          ','.join(self._setups), action])
