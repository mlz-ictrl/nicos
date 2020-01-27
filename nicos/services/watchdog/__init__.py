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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""The NICOS watchdog daemon."""

from __future__ import absolute_import, division, print_function

import hashlib
import os
import sys
from collections import OrderedDict
from os import path
from time import strftime, time as currenttime

from nicos import config, session
from nicos.core import Override, Param, anytype, dictof, listof, status
from nicos.devices.cacheclient import BaseCacheClient
from nicos.devices.notifiers import Mailer, Notifier
from nicos.protocols.cache import OP_SUBSCRIBE, OP_TELL, OP_TELLOLD, \
    cache_dump, cache_load
from nicos.pycompat import iteritems, itervalues, listvalues, to_utf8
from nicos.services.watchdog.conditions import DelayedTrigger, Expression, \
    Precondition
from nicos.utils import LCDict, createSubprocess, createThread, \
    watchFileContent


class Entry(object):
    """Represents a single watchdog configuration entry."""

    id = None
    enabled = True
    setup = ''
    condition = ''
    gracetime = 5
    message = ''
    scriptaction = ''
    action = ''
    type = 'default'
    precondition = ''
    precondtime = 5
    okmessage = ''
    okaction = ''

    from_setup = None
    cond_obj = None

    def __init__(self, values):
        self.__dict__.update(values)
        self.id = hashlib.md5(to_utf8(self.setup + self.condition +
                                      self.precondition)).hexdigest()

    def __repr__(self):
        return repr(self.condition)

    def serialize(self):
        res = {attr: getattr(self, attr) for attr in
               ('id', 'setup', 'condition', 'gracetime', 'message',
                'scriptaction', 'action', 'type', 'precondition',
                'precondtime', 'okmessage', 'okaction')}
        res['enabled'] = self.cond_obj.enabled
        return res


class Watchdog(BaseCacheClient):
    """Main device for running the watchdog service."""

    parameters = {
        'watch': Param('The configuration of things to watch',
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
        'prefix': Override(mandatory=False, default='nicos/'),
    }

    def doInit(self, mode):
        BaseCacheClient.doInit(self, mode)
        # cache of all interesting keys with current values
        self._keydict = LCDict()
        # put status constants in key dict to simplify status conditions
        for stval, stname in status.statuses.items():
            self._keydict[stname.upper()] = stval
        # set to true during connect action
        self._process_updates = False
        # current setups
        self._setups = set()
        # mapping entry ids to entrys
        self._entries = {}
        # (mangled) key to update mail receivers
        self._mailreceiverkey = self.mailreceiverkey.replace('/', '_').lower()
        # mapping cache keys to entries that check this key
        self._keymap = {'session_mastersetup': set()}
        if self._mailreceiverkey:
            self._keymap[self._mailreceiverkey] = set()
        # current warnings: mapping entry ids to the string description
        self._warnings = OrderedDict()
        # current count loop pause reasons: mapping like self._warnings
        self._pausecount = OrderedDict()

        # create all notifier devices
        self._all_notifiers = []
        self._notifiers = {'': []}
        for key, devnames in iteritems(self.notifiers):
            self._notifiers[key] = notiflist = []
            for devname in devnames:
                dev = session.getDevice(devname, Notifier)
                notiflist.append(dev)
                self._all_notifiers.append(dev)

        # process entries in the default watchlist
        for entry_dict in self.watch:
            self._add_entry(entry_dict, 'watchdog')

        # start a thread checking for modification of the setup file
        createThread('refresh checker', self._checker)

    def _checker(self):
        setupname = session.explicit_setups[0]
        fn = session._setup_info[setupname]['filenames']
        watchFileContent(fn, self.log)
        self.log.info('setup file changed; restarting watchdog process')
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def _add_entry(self, entryd, source):
        entryd = dict(entryd)  # convert back from readonlydict
        logprefix = 'entry %s from setup %r' % (entryd, source)

        # sanity-check the input
        if not entryd.get('condition'):
            self.log.warning('%s: missing "condition" key', logprefix)
            return
        if not entryd.get('message'):
            self.log.warning('%s: missing "message" key', logprefix)
            return
        if entryd.get('scriptaction') not in (None, 'pausecount', 'stop',
                                              'immediatestop'):
            self.log.warning('%s: scriptaction is invalid, needs '
                             "to be one of 'pausecount', 'stop' or "
                             "'immediatestop'", logprefix)
            entryd.pop('scriptaction')

        entry = Entry(entryd)
        entry.from_setup = source

        if entry.id in self._entries:
            self.log.error('%s: duplicate entry, ignoring', logprefix)
            return

        if entry.type and entry.type not in self._notifiers:
            log_msg = ('%s: the condition type %r is not valid, must be '
                       'one of %r' %
                       (logprefix, entry.type,
                        ', '.join(map(repr, self._notifiers))))
            if 'default' in self._notifiers:
                self.log.warning(log_msg + '; using default')
                entry.type = 'default'
            else:
                self.log.warning(log_msg + '; ignoring notifiers')
                entry.type = ''

        try:
            cond = Expression(self.log, entry.condition, entry.setup)
            if entry.gracetime:
                cond = DelayedTrigger(self.log, cond, entry.gracetime)
            if entry.precondition:
                precond = Expression(self.log, entry.precondition,
                                     entry.setup)
                if entry.precondtime:
                    precond = DelayedTrigger(self.log, precond,
                                             entry.precondtime)
                cond = Precondition(self.log, precond, cond)
            if not entry.enabled:
                cond.enabled = False
            entry.cond_obj = cond

        except Exception:
            self.log.error('%s: could not construct condition, ignoring '
                           'this condition', logprefix)
            return

        for key in cond.interesting_keys():
            self._keymap.setdefault(key, set()).add(entry)
        self._entries[entry.id] = entry

    def _remove_entry(self, eid):
        entry = self._entries.pop(eid, None)
        if entry:
            for key in entry.cond_obj.interesting_keys():
                self._keymap[key].discard(entry)

    # cache client API

    def _connect_action(self):
        # inhibit direct processing of updates
        self._process_updates = False
        try:
            BaseCacheClient._connect_action(self)
            # now process all keys we got
            time = currenttime()
            for key in list(self._keydict):
                try:
                    self._process_key(time, key, self._keydict[key])
                except Exception:
                    self.log.warning('error handling first update for key %s',
                                     key, exc=1)
        finally:
            self._process_updates = True
        self.storeSysInfo('watchdog')
        self._queue.put('watchdog/%s\n' % OP_SUBSCRIBE)
        self._publish_config()

    def _wait_data(self):
        t = currenttime()
        for entry in itervalues(self._entries):
            if entry.cond_obj.tick(t) or entry.cond_obj.is_expired(t):
                self._check_state(entry, t)

    def _handle_msg(self, time, ttlop, ttl, tsop, key, op, value):
        if key.startswith('watchdog/'):
            self._handle_control_msg(key, cache_load(value), time,
                                     op != OP_TELL)
            return

        key = key[len(self._prefix):].replace('/', '_').lower()

        # do we need the key for conditions?
        if key not in self._keymap:
            return
        expired = op == OP_TELLOLD or not value
        value = None if expired else cache_load(value)
        if not expired:
            self._keydict[key] = value
        else:
            self._keydict.pop(key, None)
        time = float(time)

        if self._process_updates:
            self._process_key(time, key, value)

    # internal watchdog API

    def _handle_control_msg(self, key, value, time, expired):
        if key == 'watchdog/enable':
            time = currenttime()
            for (eid, enabled) in value[1]:
                entry = self._entries.get(eid)
                if entry:
                    entry.cond_obj.enabled = enabled
                    entry.cond_obj.update(time, self._keydict)
                    self._check_state(entry, time)
            self.log.info('updated enabled conditions by user request')
        elif key == 'watchdog/reset':
            # reset all condition enables to their initial state
            # (e.g. due to NewExperiment)
            for entry in itervalues(self._entries):
                if entry.enabled != entry.cond_obj.enabled:
                    entry.cond_obj.enabled = entry.enabled
                    entry.cond_obj.update(time, self._keydict)
                    self._check_state(entry, time)
            self.log.info('enable status of all conditions reset')
        self._publish_config()

    def _publish_config(self):
        # publish current condition info in the cache
        self._put_message('configured', None,
                          [c.serialize() for c in itervalues(self._entries)])

    def _process_key(self, time, key, value):
        # check setups?
        if key == 'session_mastersetup' and value:
            self._setups_updated(time, set(value))
            return
        # update notification targets?
        if key == self._mailreceiverkey and value:
            self._update_mailreceivers(value)
            return
        for entry in self._keymap.get(key, ()):
            entry.cond_obj.update(time, self._keydict)
            self._check_state(entry, time)

    def _setups_updated(self, time, new_setups):
        prev_setups, self._setups = self._setups, new_setups
        # check if we need to remove some conditions
        for entry in listvalues(self._entries):
            if entry.from_setup != 'watchdog':
                if entry.from_setup not in self._setups:
                    self._remove_entry(entry.id)
        # check if we need to add some conditions
        session.readSetups()  # refresh setup info
        for new_setup in self._setups - prev_setups:
            info = session._setup_info.get(new_setup)
            if info and info['watch_conditions']:
                self.log.info('adding conditions from setup %s', new_setup)
                for entry_dict in info['watch_conditions']:
                    self._add_entry(entry_dict, new_setup)
        # trigger an update of all conditions
        for entry in itervalues(self._entries):
            entry.cond_obj.new_setups(self._setups)
            entry.cond_obj.update(time, self._keydict)
            self._check_state(entry, time)
        # update everyone els
        self._publish_config()
        self.log.info('new setups list: %s', ', '.join(self._setups))

    def _check_state(self, entry, time):
        """Check if the state of this entry changed and we need to
        emit a warning or a clear it.
        """
        eid = entry.id
        if entry.cond_obj.is_expired(time):
            if eid not in self._warnings or self._warnings[eid][0]:
                self._emit_expired_warning(entry)
        elif entry.cond_obj.triggered:
            if eid not in self._warnings or not self._warnings[eid][0]:
                self._emit_warning(entry)
        else:
            if eid in self._warnings:
                self._clear_warning(entry)
        self.log.debug('new conditions: %s', self._warnings)

    def _emit_warning(self, entry):
        """Emit a warning that this condition is now triggered."""
        self.log.info('got a new warning for %r', entry)
        warning_desc = strftime('%Y-%m-%d %H:%M') + ' -- ' + entry.message
        if entry.action:
            warning_desc += ' -- executing %r' % entry.action
        if entry.scriptaction == 'pausecount':
            self._pausecount[entry.id] = entry.message
            self._update_pausecount_str()
            warning_desc += ' -- counting paused'
        elif entry.scriptaction:
            self._put_message('scriptaction', entry, (entry.scriptaction,
                                                      entry.message))
        if entry.type:
            for notifier in self._notifiers[entry.type]:
                notifier.send('New warning from NICOS', warning_desc)
        self._put_message('warning', entry, entry.message)
        self._warnings[entry.id] = (True, warning_desc)
        self._update_warnings_str()
        if entry.action:
            self._put_message('action', entry, entry.action)
            self._spawn_action(entry.action)

    def _emit_expired_warning(self, entry):
        """Emit a warning that this condition has missing information."""
        self.log.info('value(s) missing for %r', entry)
        warning_desc = (strftime('%Y-%m-%d %H:%M') +
                        ' -- current value(s) missing, '
                        'cannot check condition %r' % entry.condition)
        # warn that we cannot check the condition anymore
        if entry.type:
            for notifier in self._notifiers[entry.type]:
                notifier.send('New warning from NICOS', warning_desc)
        self._put_message('warning', entry, warning_desc)
        self._warnings[entry.id] = (False, warning_desc)
        self._update_warnings_str()

    def _clear_warning(self, entry):
        """Clear a previously emitted warning for this condition."""
        self.log.info('condition %r normal again', entry)
        was_real_warning = self._warnings.pop(entry.id)[0]
        if entry.scriptaction == 'pausecount':
            self._pausecount.pop(entry.id, None)
            self._update_pausecount_str()
        self._update_warnings_str()

        if was_real_warning:
            self._put_message('resolved', entry, '')
            if entry.okmessage and entry.type:
                msg = strftime('%Y-%m-%d %H:%M -- ')
                msg += '%s\n\nWarning was: %s' % (entry.okmessage,
                                                  entry.message)
                for notifier in self._notifiers[entry.type]:
                    notifier.send('NICOS warning resolved', msg)
            if entry.okaction:
                self._put_message('action', entry, entry.okaction)
                self._spawn_action(entry.okaction)

    # internal helper methods

    def _put_message(self, msgtype, entry, message):
        if entry is not None:
            message = [currenttime(), message, entry.id]
        self._queue.put('watchdog/%s%s%s\n' % (msgtype, OP_TELL,
                                               cache_dump(message)))

    def _update_mailreceivers(self, emails):
        self.log.info('updating any Mailer receivers to %s', emails)
        for notifier in self._all_notifiers:
            if isinstance(notifier, Mailer):
                # we're in slave mode, so _setROParam is necessary to set params
                notifier._setROParam('receivers', emails)

    def _update_warnings_str(self):
        self._put_message('warnings', None,
                          '\n'.join(v[1] for v in self._warnings.values()))

    def _update_pausecount_str(self):
        self._put_message('pausecount', None,
                          ', '.join(self._pausecount.values()))

    def _spawn_action(self, action):
        self.log.warning('will execute action %r', action)
        script = path.join(config.nicos_root, 'bin', 'nicos-script')
        createSubprocess([sys.executable,
                          script,
                          '-M',                     # start in maintenance mode
                          '-S', '60',               # abort after 60 seconds
                          '-A', 'watchdog-action',  # appname for the logfiles
                          ','.join(self._setups),   # setups to load
                          action])                  # code to execute
