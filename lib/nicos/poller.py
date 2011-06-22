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

from __future__ import with_statement

"""
Contains a process that polls devices automatically.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import time
import errno
import signal
import threading
import subprocess

from nicos import status, session
from nicos.utils import listof, whyExited
from nicos.device import Device, Readable, Param
from nicos.errors import NicosError, ConfigurationError


class Poller(Device):

    parameters = {
        'autosetup':  Param('True if all master setups should always be polled',
                            type=bool, default=True),
        'alwayspoll': Param('Setups whose devices should always be polled',
                            type=listof(str), mandatory=True),
        'blacklist':  Param('Devices that should never be polled',
                            type=listof(str)),
    }

    def doInit(self):
        self._stoprequest = False
        self._workers = []
        self._creation_lock = threading.Lock()

    def _long_sleep(self, interval):
        te = time.time() + interval
        while time.time() < te:
            if self._stoprequest:
                return
            time.sleep(5)

    def _worker_thread(self, devname, event):
        state = ['unused']

        def reconfigure(key, value):
            if key.endswith('target'):
                state[0] = 'moving'
            elif key.endswith('pollinterval'):
                state[0] = 'newinterval'
            event.set()

        def poll_loop(dev):
            wait_event = event.wait
            clear_event = event.clear
            interval = dev.pollinterval
            errcount = 0
            i = 0
            while not self._stoprequest:
                i += 1
                try:
                    stval, rdval = dev.poll(i)
                    self.printdebug('%-10s status = %-25s, value = %s' %
                                    (dev, stval, rdval))
                except Exception, err:
                    if errcount < 5:
                        # only print the warning the first five times
                        self.printwarning('error reading %s' % dev, exc=err)
                    elif errcount == 5:
                        # make the interval a bit larger
                        interval *= 5
                    errcount += 1
                else:
                    if errcount > 0:
                        interval = dev.pollinterval
                        errcount = 0
                    if state[0] == 'moving':
                        interval = 0.5
                        if stval and stval[0] != status.BUSY:
                            state[0] = 'normal'
                            interval = dev.pollinterval
                    elif state[0] == 'newinterval':
                        interval = dev.pollinterval
                        state[0] = 'normal'
                wait_event(interval)
                clear_event()

        dev  = None
        while not self._stoprequest:
            if dev is None:
                try:
                    with self._creation_lock:
                        dev = session.getDevice(devname)
                    if not isinstance(dev, Readable):
                        self.printdebug('%s is not a readable' % dev)
                        return
                    session.cache.addCallback(dev, 'target', reconfigure)
                    session.cache.addCallback(dev, 'pollinterval', reconfigure)
                    state = ['normal']
                except NicosError, err:
                    self.printwarning('error creating %s, trying again in '
                                      '%d sec' % (devname, 30), exc=err)
                    self._long_sleep(30)
                    continue
            self.printinfo('starting polling loop for %s' % dev)
            try:
                poll_loop(dev)
            except Exception:
                self.printexception('error in polling loop')

    def start(self, setup=None):
        self._setup = setup
        if setup is None:
            return self._start_master()
        self.printinfo('%s poller starting' % setup)

        if setup == '<dummy>':
            return

        session.loadSetup(setup)
        for devname in session.getSetupInfo()[setup]['devices']:
            if devname in self.blacklist:
                self.printdebug('not polling %s, it is blacklisted' % devname)
                continue
            self.printdebug('starting thread for %s' % devname)
            event = threading.Event()
            worker = threading.Thread(target=self._worker_thread,
                                      args=(devname, event))
            worker.event = event
            worker.setDaemon(True)
            worker.start()
            self._workers.append(worker)

    def wait(self):
        if self._setup is None:
            return self._wait_master()
        while not self._stoprequest:
            time.sleep(1)
        for worker in self._workers:
            worker.join()

    def quit(self):
        if self._setup is None:
            return self._quit_master()
        if self._stoprequest:
            return  # already quitting
        self.printinfo('poller quitting...')
        self._stoprequest = True
        for worker in self._workers:
            worker.event.set()
        for worker in self._workers:
            worker.join()
        self.printinfo('poller finished')

    def reload(self):
        if self._setup is not None:
            # do nothing for single pollers
            return
        self.printinfo('got SIGUSR1, restarting all pollers')
        for pid in self._childpids.keys():
            try:
                os.kill(pid, signal.SIGTERM)
            except Exception, err:
                self.printerror(str(err))

    def _start_master(self):
        self._childpids = {}
        self._children = {}

        if not self._cache:
            raise ConfigurationError('the poller needs a cache configured')

        self._setups = set()
        if self.autosetup:
            self._setups.update(self._cache.get(session, 'mastersetup') or [])
        self._setups.update(self.alwayspoll)

        if not self._setups:
            # if no pollers are running, this would terminate the _wait_master
            # loop instantly, so wait here until there are some setups
            self._setups.add('<dummy>')

        for setup in self._setups:
            self._start_child(setup)

        if self.autosetup:
            self._cache.addCallback(session, 'mastersetup', self._reconfigure)

    def _reconfigure(self, key, value):
        self.printinfo('reconfiguring for new master setups %s' % value)
        session.readSetups()
        old_setups = self._setups

        new_setups = set(value)
        new_setups.update(self.alwayspoll)
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
        process = subprocess.Popen([poller_script, setup])
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
                setup = self._childpids[pid]
                if setup in self._setups and not self._stoprequest:
                    session.log.warning('%s poller terminated with %s, '
                                        'restarting' % (setup, whyExited(ret)))
                    del self._children[setup]
                    del self._childpids[pid]
                    self._start_child(setup)
                else:
                    session.log.info('%s poller terminated with %s' %
                                     (setup, whyExited(ret)))
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
