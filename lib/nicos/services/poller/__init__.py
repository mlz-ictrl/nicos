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

"""Contains a process that polls devices automatically."""

from __future__ import with_statement

__version__ = "$Revision$"

import os
import sys
import errno
import signal
import traceback
import threading
import subprocess
from time import time as currenttime, sleep

from nicos import session
from nicos.core import status, listof, Device, Readable, Param, NicosError, \
     ConfigurationError
from nicos.utils import whyExited


class Poller(Device):

    parameters = {
        'autosetup':  Param('True if all master setups should always be polled',
                            type=bool, default=True),
        'poll':       Param('Setups that should be polled if in master setup '
                            '(only used if autosetup is false)',
                            type=listof(str)),
        'alwayspoll': Param('Setups whose devices should always be polled',
                            type=listof(str), mandatory=True),
        'neverpoll':  Param('Setups that should never be polled, even if in '
                            'master setup', type=listof(str)),
        'blacklist':  Param('Devices that should never be polled',
                            type=listof(str)),
    }

    def doInit(self, mode):
        self._stoprequest = False
        self._workers = []
        self._creation_lock = threading.Lock()

    def _long_sleep(self, interval):
        # a sleep interruptible by stoprequest (otherwise, when we quit the
        # poller, processes with failed devices will stay around until the
        # recreate interval is expired, which can be a long time)
        te = currenttime() + interval
        while currenttime() < te:
            if self._stoprequest:
                return
            sleep(1)

    def _worker_thread(self, devname, event):
        state = ['unused']

        def reconfigure(key, value, time):
            # cache valuechange callback
            # if the target changes, assume that the state will be 'moving'
            # and shorten the poll interval
            if key.endswith('target'):
                state[0] = 'nowmoving'
            # if the pollinterval changes, update it on the next occasion
            elif key.endswith('pollinterval'):
                state[0] = 'newinterval'
            # wake up sleeper
            event.set()

        def poll_loop(dev):
            # the wait between pollings is controlled by an Event, so that
            # events from other threads (e.g. quit or cache updates) can
            # trigger a wakeup
            wait_event = event.wait
            clear_event = event.clear
            # get the initial interval
            interval = dev.pollinterval
            active = interval is not None
            if interval is None:
                interval = 3600
            # try to avoid polling the same hardware device too often
            maxage = 0 if dev.hardware_access else dev.maxage / 2.
            errcount = 0
            i = 0
            stval, rdval = None, None
            while not self._stoprequest:
                i += 1
                try:
                    if active:
                        stval, rdval = dev.poll(i, maxage=maxage)
                        self.log.debug('%-10s status = %-25s, value = %s' %
                                       (dev, stval, rdval))
                except Exception, err:
                    if errcount < 5:
                        # only print the warning the first five times
                        self.log.warning('error reading %s' % dev, exc=err)
                    elif errcount == 5:
                        # make the interval a bit larger
                        interval *= 5
                    errcount += 1
                else:
                    if errcount > 0:
                        interval = dev.pollinterval
                        errcount = 0
                # state change?
                if state[0] == 'nowmoving':
                    # if the device is moving, use a fixed small interval for
                    # polling, no matter what the parameters say
                    interval = 1.0
                    state[0] = 'moving'
                elif state[0] == 'moving':
                    # check for end of moving: if the device is idle or error,
                    # revert to normal polling interval
                    if stval and stval[0] != status.BUSY:
                        state[0] = 'normal'
                        interval = dev.pollinterval
                # poll interval changed
                elif state[0] == 'newinterval':
                    interval = dev.pollinterval
                    active = interval is not None
                    if interval is None:
                        interval = 3600
                    state[0] = 'normal'
                # now wait until either the poll interval is elapsed, or
                # something interesting happens
                wait_event(interval)
                clear_event()

        dev = None
        waittime = 30
        while not self._stoprequest:
            if dev is None:
                try:
                    # device creation should be serialized due to the many
                    # global state updates in the session object
                    with self._creation_lock:
                        dev = session.getDevice(devname)
                    if not isinstance(dev, Readable):
                        self.log.debug('%s is not a readable' % dev)
                        return
                    # keep track of some parameters via cache callback
                    session.cache.addCallback(dev, 'target', reconfigure)
                    session.cache.addCallback(dev, 'pollinterval', reconfigure)
                    state[0] = 'normal'
                except NicosError, err:
                    self.log.warning('error creating %s, trying again in '
                                     '%d sec' % (devname, waittime), exc=err)
                    self._long_sleep(waittime)
                    # use exponential back-off for the waittime; in the worst
                    # case wait 10 minutes between attempts
                    # (XXX could we have some way of knowing if another NICOS
                    # session creates and instance of this device, and in that
                    # case retry immediately?)
                    waittime = min(waittime*2, 600)
                    continue
            self.log.info('starting polling loop for %s' % dev)
            try:
                poll_loop(dev)
            except Exception:
                # should not happen (all exception-prone paths are protected
                # above), but if it does, the device will not be polled anymore
                self.log.exception('error in polling loop')

    def start(self, setup=None):
        self._setup = setup
        if setup is None:
            return self._start_master()
        self.log.info('%s poller starting' % setup)

        if setup == '[dummy]':
            return

        session.loadSetup(setup)
        for devname in session.getSetupInfo()[setup]['devices']:
            if devname in self.blacklist:
                self.log.debug('not polling %s, it is blacklisted' % devname)
                continue
            self.log.debug('starting thread for %s' % devname)
            event = threading.Event()
            worker = threading.Thread(name='%s poller' % devname,
                                      target=self._worker_thread,
                                      args=(devname, event))
            worker.event = event
            worker.setDaemon(True)
            worker.start()
            self._workers.append(worker)

    def wait(self):
        if self._setup is None:
            if os.name == 'nt':
                return self._wait_master_nt()
            return self._wait_master()
        while not self._stoprequest:
            sleep(1)
        for worker in self._workers:
            worker.join()

    def quit(self):
        if self._setup is None:
            return self._quit_master()
        if self._stoprequest:
            return  # already quitting
        self.log.info('poller quitting...')
        self._stoprequest = True
        for worker in self._workers:
            worker.event.set()
        for worker in self._workers:
            worker.join()
        self.log.info('poller finished')

    def reload(self):
        if self._setup is not None:
            # do nothing for single pollers
            return
        self.log.info('got SIGUSR1, restarting all pollers')
        for pid in self._childpids.keys():
            try:
                os.kill(pid, signal.SIGTERM)
            except Exception, err:
                self.log.error(str(err))

    def statusinfo(self):
        self.log.info('got SIGUSR2')
        if self._setup is not None:
            info = []
            for worker in self._workers:
                wname = worker.getName()
                if worker.isAlive():
                    info.append('%s: alive' % wname)
                else:
                    info.append('%s: dead' % wname)
            self.log.info(', '.join(info))
            self.log.info('current stacktraces for each thread:')
            active = threading._active
            for tid, frame in sys._current_frames().items():
                if tid in active:
                    name = active[tid].getName()
                else:
                    name = str(tid)
                self.log.info('%s: %s' % (name,
                    ''.join(traceback.format_stack(frame))))

    def _start_master(self):
        # the poller consists of two types of processes: one master process
        # that spawns and waits for the children (and restarts them in case
        # of unintended termination, e.g. by segfault); and N slave processes
        # (one for each setup loaded) that do the actual polling

        self._childpids = {}
        self._children = {}

        if not self._cache:
            raise ConfigurationError('the poller needs a cache configured')

        # by default, the polled devices always reflects the loaded setups
        # in the current NICOS master, but it can be configured to only
        # poll specific setups if loaded, or always:
        #
        # * self.poll: poll if loaded by master
        # * self.alwayspoll: always poll
        # * self.neverpoll: never poll, even if loaded
        #
        mastersetups = set(self._cache.get(session, 'mastersetup') or [])
        if self.autosetup:
            self._setups = mastersetups
        else:
            self._setups = mastersetups & set(self.poll)
        self._setups.difference_update(self.neverpoll)
        self._setups.update(self.alwayspoll)

        if not self._setups:
            # if no pollers are running, this would terminate the _wait_master
            # loop instantly, so wait here until there are some setups
            self._setups.add('[dummy]')

        for setup in self._setups:
            self._start_child(setup)

        # listen for changes in master setups if we depend on them
        if self.autosetup or self.poll:
            self._cache.addCallback(session, 'mastersetup', self._reconfigure)

    def _reconfigure(self, key, value, time):
        self.log.info('reconfiguring for new master setups %s' % value)
        session.readSetups()
        old_setups = self._setups

        if self.autosetup:
            new_setups = set(value)
        else:
            new_setups = set(value) & set(self.poll)
        new_setups.difference_update(self.neverpoll)
        new_setups.update(self.alwayspoll)
        if not new_setups:  # setup list shouldn't be empty, see above
            new_setups.add('[dummy]')
        self._setups = new_setups

        for setup in old_setups - new_setups:
            os.kill(self._children[setup].pid, signal.SIGTERM)
        for setup in new_setups - old_setups:
            self._start_child(setup)

    def _start_child(self, setup):
        if session.config.control_path:
            poller_script = os.path.normpath(
                os.path.join(session.config.control_path, 'bin', 'nicos-poller'))
        else:
            poller_script = 'nicos-poller'
        if os.name == 'nt':
            execute = [sys.executable, poller_script, setup]
        else:
            execute = [poller_script, setup]
        process = subprocess.Popen(execute)
        # we need to keep a reference to the Popen object, since it calls
        # os.wait() itself in __del__
        self._children[setup] = process
        self._childpids[process.pid] = setup
        session.log.info('started %s poller, PID %s' % (setup, process.pid))

    def _wait_master(self):
        # wait for children to terminate; restart them if necessary
        while True:
            try:
                pid, ret = os.wait()
            except OSError, err:
                if err.errno == errno.EINTR:
                    # raised when the signal handler is fired
                    continue
                elif err.errno == errno.ECHILD:
                    # no further child processes found
                    break
                raise
            else:
                # a process exited; restart if necessary
                setup = self._childpids.pop(pid)
                del self._children[setup]
                if setup in self._setups and not self._stoprequest:
                    session.log.warning('%s poller terminated with %s, '
                                        'restarting' % (setup, whyExited(ret)))
                    self._start_child(setup)
                else:
                    session.log.info('%s poller terminated with %s' %
                                     (setup, whyExited(ret)))
        session.log.info('all pollers terminated')

    def _wait_master_nt(self):
        # this is the same as _wait_master, but with active polling instead
        # of using os.wait(), which does not exist on Windows
        while True:
            sleep(0.5)
            if not self._children:
                break
            for setup, ch in self._children.items():
                ret = ch.poll()
                if ret is not None:
                    # a process exited; restart if necessary
                    del self._childpids[ch.pid]
                    del self._children[setup]
                    if setup in self._setups and not self._stoprequest:
                        session.log.warning('%s poller terminated with %s, '
                                            'restarting' % (setup, ret))
                        self._start_child(setup)
                        break
                    else:
                        session.log.info('%s poller terminated with %s' %
                                         (setup, ret))
        session.log.info('all pollers terminated')

    def _quit_master(self):
        self._stoprequest = True
        for pid in self._childpids:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError, err:
                if err.errno == errno.ESRCH:
                    # process was already terminated
                    continue
                raise
