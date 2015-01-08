#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

import ast
import subprocess
from os import path
from time import time as currenttime, strftime

from nicos import session, config
from nicos.core import Param, Override, listof, dictof, anytype
from nicos.utils import lc_dict
from nicos.protocols.cache import OP_TELL, OP_TELLOLD, cache_dump, cache_load
from nicos.devices.notifiers import Notifier, Mailer
from nicos.devices.cacheclient import BaseCacheClient
from nicos.pycompat import OrderedDict, iteritems, listitems


class Entry(object):
    id = None
    setup = ''
    condition = ''
    gracetime = 5
    message = ''
    priority = 1
    pausecount = False
    action = ''
    type = 'default'

    def __init__(self, values):
        self.__dict__.update(values)


class Watchdog(BaseCacheClient):

    parameters = {
        'watch':   Param('The configuration of things to watch',
                         type=listof(dictof(str, anytype))),
        'mailreceiverkey': Param('Cache key that updates the receivers for '
                                 'any mail notifiers we have configured',
                                 type=str),
        # these would be adevs, but adevs don't allow this flexible
        # configuration with dictionaries
        'notifiers': Param('Configures the notifiers for each warning type',
                           type=dictof(str, listof(str))),
    }

    parameter_overrides = {
        'prefix':  Override(mandatory=False, default='nicos/'),
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
        # current conditions: all entry ids where the condition is true
        self._conditions = set()
        # current warnings: mapping entry ids to the string description
        self._warnings = OrderedDict()
        # current count loop pause reasons: mapping like self._warnings
        self._pausecount = OrderedDict()
        # dictionary of keys used to evaluate the conditions
        self._keydict = lc_dict()

        # create all notifier devices
        self._all_notifiers = []
        self._notifiers = {'': []}
        for key, devnames in iteritems(self.notifiers):
            self._notifiers[key] = notiflist = []
            for devname in devnames:
                dev = session.getDevice(devname, Notifier)
                notiflist.append(dev)
                self._all_notifiers.append(dev)

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
            if entry.type and entry.type not in self._notifiers:
                self.log.error('condition %r type is not valid, must be '
                               'one of %r' %
                               (entry.condition,
                                ', '.join(map(repr, self._notifiers))))
                continue
            self._entries[i] = entry
            # find all cache keys that the condition evaluates, to get a mapping
            # of cache key -> interesting watchlist entries
            cond_parse = ast.parse(entry.condition)
            for node in ast.walk(cond_parse):
                if isinstance(node, ast.Name):
                    key = node.id[::-1].replace('_', '/', 1).lower()[::-1]
                    self._keymap.setdefault(self._prefix + key, set()).add(entry)

    def _put_message(self, msgtype, message, timestamp=True):
        if timestamp:
            message = [currenttime(), message]
        self._queue.put('watchdog/%s%s%s\n' % (msgtype, OP_TELL,
                                               cache_dump(message)))

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if not value:
            return
        if key == self._prefix + 'session/mastersetup':
            self._setups = set(cache_load(value))
        if key == self._prefix + self.mailreceiverkey:
            self._update_mailreceivers(cache_load(value))
            return
        # do we care for this key?
        if key not in self._keymap:
            return
        # put key in db
        self._keydict[key[len(self._prefix):].replace('/', '_').lower()] = \
            cache_load(value)
        for entry in self._keymap[key]:
            eid = entry.id
            # is the necessary setup loaded?
            if entry.setup and entry.setup not in self._setups:
                self._clear_warning(entry)
                continue
            # is it a new value or an expiration?
            if op == OP_TELLOLD or value is None:
                # add it to the watchlist, and if the value doesn't come back in 10
                # minutes, we warn
                self._watch_expired[eid] = [currenttime() + 600]
                continue
            if op == OP_TELL:
                # remove from expiration watchlist
                self._watch_expired.pop(eid, None)
                try:
                    value = eval(entry.condition, self._keydict)
                except Exception:
                    self.log.warning('error evaluating %r warning condition' % key,
                                     exc=1)
                    continue
                if entry.gracetime and value and eid not in self._watch_grace:
                    self.log.info('condition %r triggered, awaiting grace time'
                                  % entry.condition)
                    self._watch_grace[eid] = [currenttime() + entry.gracetime,
                                              value]
                else:
                    self._process_warning(entry, value)

    def _update_mailreceivers(self, emails):
        self.log.info('updating any Mailer receivers to %s' % emails)
        for notifier in self._all_notifiers:
            if isinstance(notifier, Mailer):
                # we're in slave mode, so _setROParam is necessary to set params
                notifier._setROParam('receivers', emails)

    def _clear_warning(self, entry):
        self.log.info('Clear warning for %r' % entry.condition)
        eid = entry.id
        if eid in self._watch_grace:
            del self._watch_grace[eid]
        if eid in self._warnings:
            del self._warnings[eid]
            self._update_warnings_str()

    def _update_warnings_str(self, timestamp=False):
        self._put_message('warnings', '\n'.join(self._warnings.values()),
                                  timestamp=False)


    def _process_warning(self, entry, value):
        eid = entry.id
        if not value:
            if eid in self._watch_grace:
                self.log.info('condition %r went normal during gracetime' %
                              entry.condition)
                del self._watch_grace[eid]
            if eid not in self._conditions:
                return
            if entry.type:
                del self._warnings[eid]
                self._update_warnings_str()
            if entry.pausecount:
                del self._pausecount[eid]
                self._put_message('pausecount',
                                  ', '.join(self._pausecount.values()),
                                  timestamp=False)
            self.log.info('condition %r normal again' % entry.condition)
            self._conditions.discard(eid)
        else:
            if eid in self._conditions:
                # warning has already been given
                return
            self._conditions.add(eid)
            self.log.info('got a new warning for %r' % entry.condition)
            warning_desc = strftime('%Y-%m-%d %H:%M') + ' -- ' + entry.message
            if entry.action:
                warning_desc += ' -- executing %r' % entry.action
            if entry.pausecount:
                self._pausecount[eid] = entry.message
                self._put_message('pausecount',
                                  ', '.join(self._pausecount.values()),
                                  timestamp=False)
                warning_desc += ' -- counting paused'
            if entry.type:
                for notifier in self._notifiers[entry.type]:
                    notifier.send('New warning from NICOS', warning_desc)
            self._put_message('warning', entry.message)
            self._warnings[eid] = warning_desc
            self._update_warnings_str()
            if entry.action:
                self._put_message('action', entry.action)
                self._spawn_action(entry.action)
        self.log.debug('new conditions: %s' % self._conditions)

    def _wait_data(self):
        t = currenttime()
        # don't use iteritems() here, the dict is changed in the loop
        for eid, wentry in listitems(self._watch_expired):
            if t > wentry[0]:
                # warn that we cannot check the condition anymore
                del self._watch_expired[eid]
                msg = ('current value missing for condition %r, '
                       'cannot check watchdog condition' %
                       self._entries[eid].condition)
                self._put_message('warning', msg)
                for notifier in self._notifiers[self._entries[eid].type]:
                    notifier.send('New warning from NICOS', msg)
        for eid, wentry in listitems(self._watch_grace):
            if t > wentry[0]:
                # grace time expired
                del self._watch_grace[eid]
                self._process_warning(self._entries[eid], wentry[1])

    def _spawn_action(self, action):
        self.log.warning('will execute action %r' % action)
        script = path.join(config.nicos_root, 'bin', 'nicos-script')
        subprocess.Popen([script, '-M', '-A', 'watchdog-action',
                          ','.join(self._setups), action])
